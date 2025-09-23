# Stay\_Awake - C# WinForms Re-implementation (SPEC)

## 0) Goal (What we’re doing)

We are re-imagining and re-developing the **Stay\_Awake** utility
originally written in Python (tkinter + Pillow + pystray + wakepy) into **C# (.NET 8, WinForms)**.

This is specifically **not** a line-for-line re-implementation of the example python program (although the 
visible GUI must be close to or perhaps nearly visibly identical).  It is a re-development into
C# using Visual Studio Community edition with specific intent to
- redesign the structure/code to make it easiler for novice developers and maintainers to manage
- to avoid false positives by antivirus products on pyinstaller-created .exe's

* **From:** Python, script-based, interpreted, depending on Pillow, wakepy, pstray, tkinter, and windows system calls.
* **To:** C# .NET 8 (WinForms) compiled desktop app that builds to a portable, self-contained, standalone, single-file EXE which works on Windows 10/11 (x64 only)

* **Not** a direct translation of the example working python program: instead, a **clear and novice-friendly rewrite**, leveraging
- C# idioms and WinForms with clear and expansive commenting to make it easiler for novice developers and maintainers to manage
- while matching the example python program (in commandline and visible GUI and behaviour and outcomes, though not necessarily code nor even structure):
  * all *CLI/GUI behavior*; GUI, image processing, tray icon, CLI options, etc
  * stay-awake behaviors, windows timer calls and countdowns, gui-update cadance bands, etc)

 * **Primary features requiring parity in outcome and visible GUI**:
  * **Prevent system sleep/hibernation** while the app runs (**display monitor sleep remains allowed**); Restores defaults on exit.
  * Main window hosts a squared (and possibly resized) image + labels + countdown fields (countdown related labels and fields are conditionally visible)
  * Windows System-tray icon (based on the final image) with Show/Hide/Quit
  * CLI options `--icon`, `--for`, `--until`, `--verbose`, with the same parsing rules, bounds, and mutual exclusivity of `--for`/`--until`
  * Low-cpu-usage timer/cadence behaviors (via time bands) near/far from deadline (adaptive, throttled when hidden); refer to the example python program

---

## 1) Coding rules (style + diagnostics)

* **Comprehensively commented program**: the code must be extremely well-commented and clarifying (eg including purpose and commandline options and examples etc at the top of the program) specifically to assist novice developers/maintainers who are unfamiliar with C#.
* **Novice-friendly comments**: clear descriptive comments intended to assist novice developers/maintainers
* **Novice-friendly code**: descriptively named methods and variables and types etc intended to assist novice developers/maintainers 
* **Novice-friendly Method/Function decriptions**: every method/function must have a block comment at the top describing its purpose, inputs, outputs, and side-effects

* Wherever possible: when making or using system calls or library calls or return values or constants or enums etc
  * import and use the formal structures, constants, enums, etc
  * where not possible, define/use them precisely as the system or library etc specifies
  * ensure 100% compliance with formal definitions and usage

* **Defensive programming**: always use **safe practices** in all approaches wherever possible
  * wrap meaningful blocks in `try/catch`
  * in `catch`, always also log **exception type, message, and stack trace** if debug is on.
  * fail with a single **centralized `Fatal()` if recovery is not possible
    * Show a modal `MessageBox` with error details.
    * Clear stay-awake state (if set).
    * Cleans up
    * Exit with code 1.
  * Always use strict comprehensive null/argument validation
    * prefer `ArgumentException`/`InvalidOperationException` with helpful messages
  * Always use strict comprehensive return-value validation

* **Use Debugging traces everywhere**:
  * Use a conditional **global flag** `AppState.DEBUG_IS_ON` (defaults `false` in Release builds; toggled true if `--verbose` supplied on CLI, resettable by the developer at any point in the code) to control debug messages.
  * Use `System.Diagnostics.Debug.WriteLine` (visible in Visual Studio Output window).
  * Apply this style of debug messaging at a minimum and more messaging where appropriate to complex coding situations:
    * Enter/exit function: `"Entered function X: purpose: XYZ..."`, `"Exiting function X."`.
    * Start/End of code blocks: `"Start of code block ZZZ, purpose: XYZ..."`, `"End of code block block ZZZ."`.
    * TRY/CATCH blocks: `"Start of WWW TRY"`, `"Caught WWW CATCH: {ex}"`, `"End of WWW TRY"`.
    * Variable changes: `"Function X: Variable Y changed from A to B"`.

* **Naming Consistency**:
   * For constants use ALL_CAPS (UPPERCASE with words separated by `_`) 
   * For global variables use ALL_CAPS (UPPERCASE with words separated by `_`) 
   * For local variables use camelCase (camelCase means: first word lowercase, subsequent words capitalized)
   * For Enum members use PascalCase (PascalCase means: capitalize the first letter of every word, no underscores)
   * For methods, properties, and class names use PascalCase (PascalCase means: capitalize the first letter of every word, no underscores)

* **Iterative development** with testing in between iterations

* **Refer to the Python program for examples only** (only examples !) of what some things look like (eg the GUI) or how some things may be calculated or images are resized by edge replication, or how an icon created from image

---

## 2) Requirements & operation

### 2.1 Purpose

* Prevent **system sleep/hibernation** while running.
* Optionally, as specified (or not) on the CLI, **auto-quit** after a duration or at a local timestamp.
* Allow **display monitor to sleep**.
* Exit cleanly when requested or when timer expires, cleanup and release any 'stay-awake' state if necessary.

### 2.2 Command-line interface (exact semantics)

#### 2.2.1 `--icon PATH`
  * Use a specific image for the window and tray icon.
  * Search order priority:
  1. CLI `--icon PATH`
  2. embedded base64 variable (if non-empty)
  3. file named `Stay_Awake_icon.*` next to the EXE/script; supported types: **PNG, JPG/JPEG, WEBP, BMP, GIF, ICO**
  4. Validation:
    * File must exist.
    * Extension must be one of above (case-insensitive).
    * If unsupported: fatal error message, listing supported types.

#### 2.2.2 `--for DURATION`
  * Run for fixed duration, then quit gracefully.
  * Token form: **no spaces**.
  * Allowed syntax encompasses mixed numbers of days hours minutes seconds or parts thereof; examples:
    * `3d4h2m5s`, `2h`, `90m`, `3600s`, `1h30m3s`
    * Mixed units allowed (`1h30m15s`)
    * Bare number means **minutes**
    * Duplicate units forbidden (`1h2h`)
  * Bounds: **>= 10 seconds**, **<= \~366 days** (configurable global constants).
  * Value `0` disables auto-quit (runs indefinitely, no countdown etc visible in the gui).
  * Mutually exclusive with `--until`.
  * Before arming**, re-ceil the remaining time to whole seconds for a calm countdown.

#### 2.2.3 `--until "YYYY-MM-DD HH:MM:SS"`
  * Run until the given **local timestamp**, then quit gracefully.
  * Local timezone timestamp in **24-hour** format.
  * Quoted string, tolerant of extra spaces and 1–2 digit parts:
    * `"2025-01-02 23:22:21"`
    * `"2025- 1- 2  3: 2: 1"`
    * `"2025-1-2 3:2:1"`
  * Validation:
    * Date must exist (reject Feb 30, etc.).
    * Time must be >= 10s in future, <= \~366 days.
    * Reject DST *nonexistent* times (spring forward gap).
    * Reject DST *ambiguous* times (fall back overlap).
  * Mutually exclusive with `--for`.
  * Before arming**, re-ceil the remaining time to whole seconds for a calm countdown.

#### 2.2.4 `--verbose`
  * Toggles `DEBUG_IS_ON` to true

#### 2.2.5 **Exit codes**
  * 0 = normal
  * non-zero = validation or runtime error

### 2.3 UI and Global behavior

* **Capability for Single instance**:
  * Enabled/disabled with global boolean variable `SINGLE_INSTANCE_IS_ON` initially set to false 
    * Acquire named Mutex.
    * If already running: attempt to bring existing window to foreground or show tray balloon. If not possible, show modal and exit.

* **Main Window**:
  * DPI-aware for maximum high quality image display fidelity   .
  * Contains:
    * Centered **image** (maximum size per global variable, initially 512 px; image is pre auto-sized to a square by **edge replication** (no solid-color padding) so it never need be stretched afterward).
    * Labels for: blurb, ETA, remaining time, cadence (frequency of gui countdown update, adjusts based on bands of time remaining, throttles when hidden, timer display snaps to neat boundaries when far from the deadline (calm UI)).
  * Window re-sized to cater for image size plus other labels and fields.
  * User Resizing disabled (via `FormBorderStyle.FixedSingle`, `MaximizeBox=false`).

* **Stay-Awake logic**:
  * On ready: call `SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)`.
  * On quit: call `SetThreadExecutionState(ES_CONTINUOUS)` to clear.
  * please check/confirm this is the case with the working python program as the example .
  
* **`Fatal()` logic**: 
  * Explicitly, Fatal() must work pre-UI (using MessageBox.Show without depending on Form or NotifyIcon).
  * This avoids confusion later (when deciding if mutex/CLI validation can call Fatal before UI exists).

* **Single-instance flow**:
  * This behaviour is conditional according to a global boolean variable in the program.
  * This specification mentions “If already running bring the other instance forward”.
  * For clarity, first already-running instance is the one being `brought forward` (gain focus) if possible and very easy; inter-process communication et al is specifically not desired; The later instance only signals then exits.

* **NotifyIcon visibility timing**:
  * the context menu may be created early, but `NotifyIcon.Visible = true` should only be set after the icon image is ready (to avoid flashing the default blank icon). This prevents confusion when coding step 1.4 vs 2.x.


---

## 3) Architecture outline (phased, iterative)

### 3.1 Main outline

1. **Setup/Init**
   1.1 Parse CLI -> validate (`--icon`, `--for`, `--until`, `--verbose`).
   1.2 Validate inputs
   1.3 Conditionally according to a global boolean variable: Acquire single-instance mutex, If already running bring the other instance forward and exit.
   1.4 Initialize the UI
     * Initialize and configure WinForms (DPI-aware and ensuring AutoScaleMode = Dpi in the form) to provide message dialogs, error popups, Fatal(msg), main window with controls etc.
     * User Resizing disabled hook basic keyboard/mouse.
     * The form layout and labels and buttons are to be positioned and look exactly like as used in the example python program
     * Build context menu (“Show/Minimize/Quit”) per the python example
     * Fatal(msg) on error: modal error dialog, **clear stay-awake** if set, exit.
     * The Image and the Tray icon will be done in a future step and not here
   1.5 Initialize Time/Timezone helpers:
     * use always-safe approach; `TimeZoneInfo.Local`with added Win32 verification for DST edge cases.

2. **Image and Icon preparation and insertion**
   2.1 Load and prepare image in memory, if required making image square by edge-replication (max px size according to a global parameter, adjust size if and as required eg aligning with the working example python program)
   2.2 Using the image, build a multi-size icon in memory (sizes=[(16,16),(20,20),(24,24),(32,32),(40,40),(48,48),(64,64),(128,128),(256,256)]) for use as the windows system-tray icon.
   2.3. **Image and Icon insertion**
     * Insert squared image in memory into PictureBox.
     * Use multi-size icon as the icon in the windows system-tray.

3. **Timers & updates**
   * Arm countdown timer(s) based on validated `--for` or `--until`.
   * Update labels and tray tooltip.
   * Use adaptive cadence (frequency of gui countdown update, adjusts based on bands of time remaining, throttles when hidden, timer display snaps to neat boundaries when far from the deadline (calm UI))

4. **Stay-Awake logic**
   * Set thread execution state.
   * Ensure revert on quit.

5. **Cleanup**
   * Dispose tray icon.
   * If required, release Mutex.
   * Exit application.

### 3.2 Alternative outline notation, hopefully consistent with §3.1

```
1. Setup/Init
   1.1 Conditionally according to a global boolean variable: Acquire single-instance mutex
       └─ If another instance exists, signal primary to foreground and exit
   1.2 Parse CLI -> validate (log paths, image file, etc.)
   1.3 Validate inputs (paths, duration/DT bounds, exclusivity)
       └─ On error: Fatal(msg) — modal MessageBox, pre-UI safe
   1.4 Initialize the UI (WinForms)
       ├─ Ensure STA and ApplicationConfiguration.Initialize()
       ├─ Provide message dialogs, error popups (shows modal MessageBox with error?)
       ├─ fatal(msg): centralized, no dependency on Form/NotifyIcon
       └─ Prepare main form shell (FixedSingle, AutoScaleMode=Dpi) and contents
            ├─ The form layout and labels and buttons are to be positioned and look exactly like as used in the example python program
            ├─ Image widget (PictureBox or custom control)
            ├─ Label fields for calculated values
            ├─ Hook keyboard/mouse events
            ├─ Disable user resize and maximize button
            ├─ Create system tray menu (NotifyIcon + ContextMenuStrip)
            └─ “Show Window” / “Minimize to System Tray” / “Quit”
   1.5 Init time/timezone helpers
       └─ TimeZoneInfo.Local + Win32 check for DST edges
2. Image preparation and insertion
     ├─ Load image (from an internal base64 variable, or --icon, falling back to images in disk, whatever order is specified in this spec, fallback to the order the python program does it)
     ├─ manipulate image in memory to make it square and even number of pixels WxH using edge replication (no solid-color padding)
     ├─ in memory (sizes=[(16,16),(20,20),(24,24),(32,32),(40,40),(48,48),(64,64),(128,128),(256,256)]) for use as the windows system-tray icon
     ├─ Adjust window size if required
     ├─ Insert squared image in memory into PictureBox.
     ├─ Use multi-size icon as the icon in the windows system-tray; Assign NotifyIcon.Icon and set Visible = true
     └─ Adjust window size if required
3. Timers & Updates (System.Windows.Forms.Timer (UI thread), not System.Timers.Timer)
   ├─ Start timers (System.Windows.Forms.Timer (UI thread), not System.Timers.Timer) (Timers are on the UI thread, simplifying updates.)
   ├─ Periodically recalc and update labels according to cadence (countdown update frequency) and related specifications
   └─ Throttle updates to avoid repaints storms
4. Stay-Awake Logic
   ├─ Once UI + timers are stable, call SetThreadExecutionState
   └─ On quit/exit: Clear, restore defaults, cleanup, exit
5. Cleanup
   ├─ Conditionally Release mutex (per global boolean variable)
   ├─ Dispose of NotifyIcon
   └─ Application.Exit()
```

---

## 4) Technical Clarifications

### 4.1 CLI parsing & validation

* Simple parser supporting:
  * Flags: `--verbose`
  * Key/Value: `--icon=PATH`, `--for=...`, `--until="..."`
* Mutual exclusion: `--for` **xor** `--until`.
* Validate:
  * `--icon`: exists and is supported format (we’ll load with **ImageSharp** or System.Drawing on Windows).
  * `--for`: parse composite tokens to total seconds; apply min/max bounds; 0 disables. (parity with Python)
  * `--until`: tolerate whitespace and 1–2 digit parts; turn into a **local epoch**; reject **nonexistent** and **ambiguous** times (DST transitions) with clear messages. (parity with Python)

### 4.2 Time/Timezone strategy (reliable)

* Primary: `TimeZoneInfo.Local` + `DateTimeOffset` for everyday logic.
* DST edge validation (mirrors Python’s two-pass logic):
  * Attempt two conversions (as if STD vs DST).
  * If neither maps to the same civil components -> nonexistent -> error.
  * If both map but produce different instants -> ambiguous -> error. (guide the user to choose another time.)
* Verification via Win32 `GetDynamicTimeZoneInformation` for zone bias/DST rules.

### 4.3 Image/icon handling

* Load image from source priority order
  * CLI --icon PATH
  * embedded base64
  * Stay_Awake_icon.* next to EXE
    * Supported file types: PNG, JPG/JPEG, WEBP, BMP, GIF, ICO. Reject others with a clear error.
* Square by Edge Replication (no solid-color padding)
  * Compute delta = max(width,height) − min(width,height)
  * Create a square canvas of size max(width,height) in 32bpp ARGB
  * Draw the source centered
  * If portrait (height > width):
    * Fill left margin by stretching the leftmost 1px column of the drawn image to the canvas edge
    * Fill right margin by stretching the rightmost 1px column of the drawn image to the canvas edge
  * If landscape (width > height):
    * Fill top margin by stretching the topmost 1px row to the canvas edge
    * Fill bottom margin by stretching the bottommost 1px row to the canvas edge
  * Note: If delta is odd, place the extra 1px on right/bottom to make it square
  * Result: a square image with replicated edges; no solid-color bars; no subject distortion
  * Finally, if the result not an even number of pixels vertically then make it an even numbered square
    * Edge replicate 1 additional bottommost row and 1 rightmost column of pixels to make an even numbered square image
* Then if necessary scale the resulting squared image for:
  * Window image: scale the squared image so it is 512px (configurable via a global variable) using high-quality resampling
* Build one multi-size **Icon** from the scaled squared image in memory (sizes=[(16,16),(20,20),(24,24),(32,32),(40,40),(48,48),(64,64),(128,128),(256,256)] PNG-compressed) for use both as
  * NotifyIcon in the windows system-tray
  * the app icon (ie when creating a shortcut to the app on the desktop) 

> For clarification, here is some pseudocode to square the image by edge replication:
```
loadOriginal(pathOrEmbedded) -> Bitmap src
if src.Width == src.Height:
    square = src
else:
    size = max(src.W, src.H)
    square = new Bitmap(size, size, PixelFormat32ARGB)
    using g = Graphics.FromImage(square):
        g.InterpolationMode = HighQualityBicubic
        // draw centered
        x = (size - src.W) / 2
        y = (size - src.H) / 2
        g.DrawImage(src, x, y, src.W, src.H)
        if src.W < src.H: // portrait -> replicate left/right columns
            // left strip
            leftSrc = Rectangle(x, y, 1, src.H)
            leftDst = Rectangle(0, y, x, src.H)
            g.DrawImage(square, leftDst, leftSrc, Unit.Pixel)
            // right strip
            rightSrc = Rectangle(x+src.W-1, y, 1, src.H)
            rightDst = Rectangle(x+src.W, y, size-(x+src.W), src.H)
            g.DrawImage(square, rightDst, rightSrc, Unit.Pixel)
        else: // landscape -> replicate top/bottom rows
            topSrc = Rectangle(x, y, src.W, 1)
            topDst = Rectangle(x, 0, src.W, y)
            g.DrawImage(square, topDst, topSrc, Unit.Pixel)
            botSrc = Rectangle(x, y+src.H-1, src.W, 1)
            botDst = Rectangle(x, y+src.H, src.W, size-(y+src.H))
            g.DrawImage(square, botDst, botSrc, Unit.Pixel)
iconSizes = [16,20,24,32,40,48,64,128,256]
icons = [ resize(square, s, s) for s in iconSizes ]
ico = buildIcoContainer(icons, pngFor256=true)
return square, ico
```

#### 4.3.1 Multi-image ICO (no external dependencies)

**Objective:** From one arbitrary input image (PNG/JPG/JPEG/BMP/GIF/ICO), produce:

* A **squared master bitmap** using *edge replication* (no solid padding).
* A **multi-image .ico** containing these frames (all PNG inside the ICO):
  **sizes = \[16, 20, 24, 32, 40, 48, 64, 128, 256]** (pixels, square).

**Rationale:**

* Keeps the project **dependency-free** (no ImageSharp).
* Windows 10/11 fully support **PNG frames** in ICOs.
* One clean implementation path (no DIB/AND-mask quirks).

##### A) Responsibilities (3 tiny helpers)

1. **ImageLoader** (input orchestration)

   * **Inputs:** CLI `--icon` path (preferred), embedded base64 (optional), `Stay_Awake_icon.*` next to EXE (fallback), internal glyph (last resort).
   * **Outputs:** `Bitmap original` (32bpp ARGB).
   * **Rules:**
     * Supported extensions (v1): `.png`, `.jpg/.jpeg`, `.bmp`, `.gif`, `.ico`.
       WEBP: **reject with a clear message** (documented). (Optional future: WIC interop.)
     * For GIF: first frame only.
     * For ICO input: pick the **largest** frame in the file as `original`.
     * Validate file exists and is readable; else fail with `Fatal()`.

2. **ImageSquareReplicator** (edge replication, no distortion)

   * **Input:** `Bitmap original` (any WxH).
   * **Output:** `Bitmap square` (SxS where `S = max(W, H)`, 32bpp ARGB).
   * **Algorithm (paint-friendly, no per-pixel loops):**
     1. Create a new **square canvas** `S × S` (32bpp ARGB).
     2. Draw the source **centered** (high-quality resampling **off** here—this draw is 1:1).
     3. If portrait (`H > W`): fill the left and right margins by **stretching** the **leftmost** and **rightmost 1-pixel columns** of the drawn image, respectively, to the canvas edges.
        If landscape (`W > H`): likewise stretch the **topmost** and **bottommost 1-pixel rows** to fill margins.
     4. If the difference is **odd**, put the extra pixel on **right** (horizontal) or **bottom** (vertical) for determinism.
   * **Quality:** use 32bpp ARGB surfaces; preserve alpha; dispose `Graphics` and `Bitmap` with `using`.

3. **IconWriter** (multi-image, all-PNG ICO composer)

   * **Inputs:** `Bitmap square`, `int[] sizes = {16,20,24,32,40,48,64,128,256}`.
   * **Outputs:** `Icon multiImageIcon` (usable for **NotifyIcon** and as **Application Icon**).
   * **Process:**
     1. **For each** size in `sizes`:
        * Resample **directly from `square`** (never chain resizes) with **HighQualityBicubic**.
        * Encode the result as **PNG bytes** into a `MemoryStream` (`bitmap.Save(ms, ImageFormat.Png)`).
        * Record: width, height (cap at 255 for ICO directory fields; special-case 256 -> write 0 per ICO spec), bit depth (use 32), data length, and a placeholder for the data offset.
     2. Write ICO container into a new `MemoryStream`:
        * `ICONDIR` header (type=1 icon, count=frames).
        * `ICONDIRENTRY` array: one entry per size, **with data offsets computed after the directory**.
        * Append each PNG payload sequentially; patch offsets/sizes as needed.
     3. Construct an `Icon` from the stream (keep the stream alive as needed), or copy to a new stream for an independent `Icon`.
   * **Policy:** **All frames as PNG** (including 16–128). This is fully supported on Win10/11; performance impact is negligible.

##### B) DPI & runtime selection

* **Multi-image ICO lets Windows pick the best frame** for the current DPI automatically (Explorer/taskbar/tray).
* Sizes chosen cover common DPI scales:
  * 100% -> 16, 125% -> 20, 150% -> 24, 200% -> 32, 250% -> 40, 300% -> 48, 400% -> 64, etc.
* You can still query DPI (Per-Monitor V2) if you want to **verify** which frame is used, but it’s not required.

##### C) Memory & lifetime (important)

* `NotifyIcon.Icon` should be assigned an `Icon` whose backing stream stays alive **until dispose** (if constructing from a stream).
* If you ever use `Icon.FromHandle(hIcon)` (not required here), you **must** call `DestroyIcon(hIcon)` when done to avoid leaking GDI handles.
* Always `Dispose()` of:
  * All temporary `Bitmap` instances,
  * All temporary `Graphics`,
  * The `NotifyIcon` at shutdown.

##### D) Edge cases & validation

* **Tiny images** (e.g., 12×12): square them, then allow upscale—cap excessive upscale (e.g., ≤ 4×) for the **window** image to avoid visible blur; for **icons**, you still generate all sizes (the small source will blur at larger frames—acceptable for v1).
* **Huge images**: consider a **max source size** (e.g., downscale to ≤ 1024×1024) before squaring to keep memory bounded.
* **Color profile/EXIF**: System.Drawing ignores most profiles; acceptable for utility use. (Document this.)
* **Alpha**: ensure backgrounds remain transparent—no premultiplied color fringes (use ARGB canvases only).
* **GIF/WEBP**: first frame only; WEBP -> **reject with a clear message** in v1.

##### E) Public APIs (no code, just contracts)

* `class ImageLoader`
  * `Bitmap LoadOriginalFromSources(string? cliPathOrNull)`
    *Resolves the priority chain (CLI -> embedded base64 -> sidecar file -> fallback glyph), validates extension, loads and returns a 32bpp ARGB bitmap. Throws on error.*
* `class ImageSquareReplicator`
  * `Bitmap MakeSquareByEdgeReplication(Bitmap original)`
    *Returns a new ARGB bitmap (S×S) with replicated edges; the caller owns disposal.*
* `class IconWriter`
  * `Icon BuildMultiImageIconFromSquare(Bitmap square, IReadOnlyList<int> sizes)`
    *Returns an in-memory `Icon` containing **PNG frames** at the specified sizes. The caller disposes the returned `Icon`.*
* **Optional convenience**:
  * `Icon BuildDefaultMultiImageIcon(Bitmap original)` -> internally calls `MakeSquareByEdgeReplication()` then `BuildMultiImageIconFromSquare()` with the default sizes array.

##### F) Application integration points

* **Tray**:
  `notifyIcon.Icon = multiImageIcon;`
  `notifyIcon.Text = "Stay Awake — running (ETA 12:34)";` *(tooltip updated by timers)*
* **Window title & form icon** (optional):
  `this.Icon = multiImageIcon;` *(WinForms window chrome icon)*
* **Application Icon** (Explorer/shortcuts):
  * At **build time** you can still pick a design-time ICO in Project Properties; or
  * At **runtime** you can also save the memory ICO to disk once (e.g., `%LocalAppData%`) and set it for shortcuts you create programmatically (if any).
  * For publishing a static EXE, it’s typical to set a **design-time ICO** in Project Properties that matches what you build at runtime.

##### G) Tests (what “done” looks like)

1. **Load**: PNG/JPG/BMP/GIF/ICO source paths load; non-existent path -> fatal with clear message; WEBP -> rejected with specific message.
2. **Square**: non-square inputs produce perfectly square outputs with **replicated edges**, no solid bars, no distortion.
3. **Icon**: resulting `.ico` has frames at exactly `[16,20,24,32,40,48,64,128,256]`.
4. **Visual**:
   * On 100%/125%/150%/200% DPI monitors, tray and taskbar icons look **crisp** (no fuzzy scaling).
   * Explorer shows a sharp **256×256 thumbnail** for the app if you set it as Application Icon.
5. **Resource hygiene**: pin a breakpoint in `FormClosing` and confirm `NotifyIcon.Dispose()` is called; no GDI handle leaks.

##### H) Future options

* **DIB for small frames** (hybrid encoding): match historical toolchains (≤48 as DIB + AND mask, 256 as PNG). Not necessary for Win10/11; only if you need maximum cross-tool compatibility.

### 4.4 Stay-Awake logic (Win32)

* Use **`SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)`** when armed, and call again with `ES_CONTINUOUS` on **quit** to clear.
* Verify these states with what is used in the working example python program
* In testing, verify requests with `powercfg -requests` (docs mention this in Python README).

### 4.5 Timers & cadence

* Calculate a **deadline** using a **monotonic** clock concept (`Stopwatch`/`Environment.TickCount64`) to avoid system clock jumps, while also maintaining a **wall-clock ETA** for display.
* Adaptive cadence (GUI update frequency), e.g. 10 min cadence (GUI update frequency) far out -> 1 sec cadence (GUI update frequency) near the end
  * When far from the deadline, align (snap) the next tick to a clean boundary (eg the nearest 00 or 30 seconds) to avoid visual jitter
  * Throttle the cadence (GUI update frequency) when the main window is hidden - parity with the example working Python program’s behavior.

### 4.6 Conditional (per a global boolean variable) Single-instance guard

* Named `SyayAwakeMutex` per a global variable. 
* Conditionally, if another instance exists:
  * Try to **find the window** of the existing instance (e.g., via a named **Win32 message** or **mutex+named pipe** handshake) and **restore/activate** it.
  * Fallback: show a MessageBox in the second instance (“already running”) and exit.

### 4.7 Error handling & `Fatal()` policy

* A single `Fatal(string msg, Exception? ex = null)`:
  * Writes to Debug + optional log path from CLI.
  * Shows `MessageBox` with helpful text.
  * If stay-awake is armed, **clears** it .
  * Possibly calls `Environment.Exit(1)`.

### 4.8 QuitMode enum

Define and use a simple enum to clarify flow:

```csharp
enum QuitMode
{
    None,
    ForDuration,
    UntilDateTime
}
```

### 4.9 AppState Globals

```csharp
internal static class AppState
{
    public static string AppName = "Stay_Awake";
    public static bool DEBUG_IS_ON = false;
    public static bool SINGLE_INSTANCE_IS_ON = false;

    public static string? ImagePath;
    public static string? LogPath;

    public static QuitMode QuitMode = QuitMode.None;
    public static DateTimeOffset? TargetLocal;
    public static TimeSpan? ForDuration;

    public static string InstanceMutexName =
        "StayAwake_Mutex_GUID-CHANGE-THIS";

    // and, I suppose, any other necessary global variables here ?
    // and, I suppose, a few to query:
    // ? long? TargetMonotonicTicks (deadline for stable countdown)
    // ? Icon/Image buffers : keep resized variants cached in memory to avoid repeated work.
}
```

### 4.10 ImageAssets struct

```csharp
struct ImageAssets
{
    public Bitmap Original;
    public Bitmap Squared;
    public Icon MultiSizeIcon;
}
```

---

## 5) Testing plan (iterative)

### Iteration 1 (Setup/Init only)

* `--help` prints usage.
* `--icon C:\badpath.png` -> error.
* `--for 2h`, `--for 90m`, `--for 0` all valid.
* `--for nonsense` -> error.
* `--until "2025-1-2 3:2:1"` accepted.
* `--until "2025-02-30 12:00:00"` rejected.
* Launch twice -> second exits with message.

### Iteration 2+

* Tray icon displays.
* Tooltip updates with ETA.
* Timers tick at adaptive cadence.
* Stay-Awake state toggled.

### DST tests

* Pass nonexistent local time (spring forward) -> reject.
* Pass ambiguous local time (fall back) -> reject.

---

## 6) Development Environment & Toolchain (Hyper-V VM)

### 6.1 Baseline

* **Hyper-V VM**: Windows 11 Enterprise Evaluation (Gen2).
* **Visual Studio 2022 Community (latest)** with workload: **.NET desktop development**.
* **.NET 8 SDK** + Windows 11 SDK installed.
* Project targets `net8.0-windows`.
* Manifest enables `PerMonitorV2` DPI awareness.

### 6.2 Publish profile (for portable EXE)

* Visual Studio -> **Publish...** -> **Folder** profile:
   * **Mode**: Folder.
  * **Target runtime**: **win-x64**
  * **Deployment mode**: **Self-contained**
  * **Produce single file** = on
  * **Trim** = **off** initially (safer for WinForms)
  * **ReadyToRun** = on (faster startup, larger file)
  * **Configuration**: Release

### 6.3 Exporting/copying things

* **Export VS settings**: *Tools -> Import and Export Settings -> Export selected environment settings* -> save `.vssettings`. Copy to host via shared folder/ISO/OneDrive/etc.

* **Share/copy solution**:
  * Zip the solution folder (exclude `.vs` if you like) and copy to host.

* **Copy published EXE from VM to host**:
  * Use Hyper-V **Enhanced Session** to access `\\tsclient\<drive>` (clipboard/drive redirection), or
  * Create a **shared folder** via SMB on the host and map it from VM, or
  * Use cloud drive (OneDrive/Dropbox), or
  * Mount a temporary **VHDX** as a transfer volume.

* **VM hygiene**:
  * Use **Checkpoints** before major installs.
  * Keep a **“golden” VM** (fresh VS + SDKs + Windows updated) and clone for experiments.

---

## 7) Developer guidance (novice-friendly)

* **Think like a maintainer**: assume the next dev is a beginner.
* **Prefer clarity over performance**.
* **Name things verbosely but with clarity of purpose**
* **Never skip comments**: no code should rely solely on context/content.
* **Avoid premature optimization**: instead favor **clarity** and **comments**.
* **Encapsulate** tray logic in a helper class - don’t bloat `Form1.cs`.
* **Keep all cross-cutting logic in one place** to avoid leaks. (mutex, fatal, stay-awake on/off) 
* **Prefer pure methods** for parsing/formatting (easy to unit test later).
* **Unit-test parsing functions separately** (e.g., ForDuration parser).
* **Iterate**: implement, run, and test small slices before proceeding ; after each step, **F5** and verify in the Output window.

---

## 8) Appendix - Behavior examples (CLI)

Assuming we define global constants along the lines:
```csharp
MIN_AUTO_QUIT_SECS = 10         // 10 seconds
MAX_AUTO_QUIT_SECS = 31557600   // (=365.25 days * 24 * 60 * 60)
```
then the Bounds below are controlled by constants MIN_AUTO_QUIT_SECS and MAX_AUTO_QUIT_SECS.
```text
--icon PATH
    Use a specific image file for the window/tray icon.
    Supports: PNG, JPG/JPEG, WEBP, BMP, GIF, ICO.

--for DURATION
    Keep awake for a fixed time, then quit gracefully.
    DURATION accepts days/hours/minutes/seconds in one token (no spaces):
      3d4h5s, 2h, 90m, 3600s, 1h30m
    A bare number means minutes. 0 disables auto-quit.
    Bounds: >= MIN_AUTO_QUIT_SECS and <= MAX_AUTO_QUIT_SECS.
    Mutually exclusive with --until.

--until "YYYY-MM-DD HH:MM:SS"
    Local 24-hour timestamp. Relaxed spacing & 1–2 digit parts accepted:
      "2025-01-02 23:22:21"
      "2025- 1- 2  3: 2: 1"
      "2025-1-2 3:2:1"
    Honors DST rules; rejects nonexistent/ambiguous local times.
    Bounds: >= MIN_AUTO_QUIT_SECS and <= MAX_AUTO_QUIT_SECS.
    Mutually exclusive with --for.
```


(These mirror the documented Python app and source logic.)

---

