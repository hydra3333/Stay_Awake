# Stay\_Awake — Specification for Re-implementation into C# WinForms

---

## 0) Context and Goal

We are re-imagining and re-developing the **Stay\_Awake** utility
originally written in Python (tkinter + Pillow + pystray + wakepy) into **C# (.NET 8, WinForms)**.

* **From → To**:
  * From: Python, script-based, interpreted, depends on Pillow, wakepy, tkinter.
  * To: C#, compiled, standalone portable EXE for Windows 10/11 (x64).
* **Not** a direct translation: instead, a **clear and novice-friendly rewrite**, leveraging C# idioms and WinForms while preserving all *functional behavior* (GUI, tray icon, stay-awake logic, CLI options).
* **Deliverable**: A single `.exe` that can be copied to any folder and run without installer or external dependencies.

* **Primary feature parity:**
  * Prevent **system sleep/hibernation** while the app runs; **display monitor sleep remains allowed**. Restores defaults on exit.
  * **System tray** icon with Show/Hide/Quit; main window hosts an image + labels + optional countdown.
  * CLI options `--icon`, `--for`, `--until`, with the same parsing rules, bounds, and mutual exclusivity.
  * **Low-cpu timer/cadence** behavior near/far from deadline (adaptive, throttled when hidden).

---

## 1) Coding Rules (Style, Safety, Debugging)

These rules are **non-negotiable** to ensure clarity for novice developers:

1. **Verbosity over brevity**:

   * Every method/function must have a block comment describing its *purpose, inputs, outputs, and side-effects*.
   * Variable names must be **long and descriptive** (`remainingSecondsUntilQuit` not `remSec`).
   * The program must be comprehensively commented - the code must be extremely well-commented and clarifying
   (eg including purpose and commandline options and examples etc at the top of the program)
   specifically to assist novice developers/maintainers who are unfamiliar with C#.



2. **Debugging traces**:

   * Use `System.Diagnostics.Debug.WriteLine` (visible in VS Output window).
   * Also allow optional `Console.WriteLine` for when run from CMD.
   * Use a **global flag** `AppState.DEBUG_IS_ON` (defaults `false` in Release builds; toggled true if `--verbose` supplied).
   * All debug traces must be wrapped in `if (AppState.DEBUG_IS_ON)`.

   Examples of required messages:

   ```
   Entered function ParseArguments ...
   Start of timer callback TRY
   Function SetupStayAwake: Variable state changed value from Inactive to Active
   Caught MainLoop CATCH: System.IO.IOException: Access denied
   Exiting function InitializeTrayIcon ...
   ```

3. **Error handling (Python-style try/except equivalent)**:

   * Wrap meaningful blocks in `try/catch`.
   * Always call centralized `Fatal()` if recovery is not possible.
   * In `catch`, always log **exception type, message, and stack trace** if debug is on.

4. **Fatal() policy**:

   * Show a modal `MessageBox` with error details.
   * Clear stay-awake state (if set).
   * Exit with code 1.
   * Also log to file if `--log` supplied.

5. **Consistency**:

   * Use PascalCase for methods, properties, and class names.
   * Use camelCase for local variables.
   * Enums and constants must be all-caps (`QuitMode.ForDuration`).

---

## 2) Requirements

### 2.1 Purpose

* Prevent **system sleep/hibernation** while running.
* Allow **monitor/display sleep**.
* Exit cleanly when requested or when timer expires, restoring system defaults.

### 2.2 CLI Semantics

* **`--icon PATH`**

  * Explicit icon file for window + tray.
  * Supported: `.png`, `.jpg/.jpeg`, `.webp`, `.bmp`, `.gif`, `.ico`.
  * Validation:

    * File must exist.
    * Extension must be one of above (case-insensitive).
    * If unsupported: fatal error listing supported types.

* **`--for DURATION`**

  * Run for fixed duration, then quit gracefully.
  * Token form: **no spaces**.
  * Allowed syntax:

    * `3d4h5s`, `2h`, `90m`, `3600s`, `1h30m`.
    * Bare number means **minutes**.
    * Mixed units allowed (`1h30m15s`).
    * Duplicate units forbidden (`1h2h`).
  * Bounds: **≥ 10 seconds**, **≤ \~366 days** (configurable constants).
  * Value `0` disables auto-quit (runs indefinitely).
  * Mutually exclusive with `--until`.

* **`--until "YYYY-MM-DD HH:MM:SS"`**

  * Local timestamp in **24-hour** format.
  * Quoted string, tolerant of extra spaces and 1–2 digit parts:

    * `"2025-01-02 23:22:21"`
    * `"2025- 1- 2  3: 2: 1"`
    * `"2025-1-2 3:2:1"`
  * Validation:

    * Date must exist (reject Feb 30, etc.).
    * Time must be ≥ 10s in future, ≤ \~366 days.
    * Reject DST *nonexistent* times (spring forward gap).
    * Reject DST *ambiguous* times (fall back overlap).
  * Mutually exclusive with `--for`.

* **Other options**:

  * `--log PATH`: append log messages here. Create directory if needed. Fatal if unwritable.
  * `--verbose`: toggles `DEBUG_IS_ON`.
  * `--help`: show usage and exit.

* **Exit codes**:

  * `0` = normal.
  * Non-zero = validation or runtime error.

### 2.3 UI & Behavior

* **Single instance**:

  * Acquire named Mutex.
  * If already running: attempt to bring existing window to foreground or show tray balloon. If not possible, show modal and exit.

* **Main Window**:

  * Fixed size, DPI-aware.
  * Contains:

    * Centered **image**.
    * Labels for: blurb, ETA, remaining time, cadence.
  * Resizing disabled (via `FormBorderStyle.FixedSingle`, `MaximizeBox=false`).

* **Tray Icon**:

  * Built from loaded/squared image.
  * Tooltip shows countdown/ETA.
  * Context menu: Show Window / Minimize to Tray / Quit.

* **Image logic**:

  * Load via priority:

    1. CLI `--icon`.
    2. Embedded base64.
    3. `Stay_Awake_icon.*` in program dir.
    4. Tiny internal fallback glyph.
  * Manipulate: **edge replication** to square.
  * Scale for: window (up to 512px) and tray icon sizes (16/20/24/32).

* **Timers**:

  * Use `System.Windows.Forms.Timer`.
  * Adaptive cadence: 10min ticks far out → 1s near end.
  * Snap first tick to a boundary when far away.
  * Throttle updates when window is hidden.

* **Stay-Awake logic**:

  * On ready: call `SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)`.
  * On quit: call `SetThreadExecutionState(ES_CONTINUOUS)` to clear.

---

## 3) Architecture Outline

### High-Level Flow

1. **Setup/Init**

   * Parse CLI.
   * Validate inputs.
   * Acquire Mutex.
   * Fatal() on error.
   * Initialize timezone helpers.
   * Load and prepare image/icon.

2. **GUI + Tray**

   * Initialize WinForms.
   * Build window and controls.
   * Build NotifyIcon and context menu.

3. **Insert Image**

   * Insert squared image into PictureBox.
   * Build in-memory multi-size Icon for tray.

4. **Timers & Updates**

   * Arm countdown timer based on `--for` or `--until`.
   * Update labels and tray tooltip.
   * Adaptive cadence.

5. **Stay-Awake**

   * Set thread execution state.
   * Ensure revert on quit.

6. **Cleanup**

   * Dispose tray icon.
   * Release Mutex.
   * Exit application.

---

## 4) Technical Clarifications

### Timezone handling

* Use `TimeZoneInfo.Local` for most logic.
* For DST edge validation:

  * Convert candidate local time → UTC twice (pretend STD vs DST).
  * If neither maps: nonexistent → reject.
  * If both map to valid but different UTC: ambiguous → reject.
* Optional: call Win32 `GetDynamicTimeZoneInformation` for extra diagnostics.

### Image handling

* Edge replication: extend last row/column outward until square.
* Use `System.Drawing` (GDI+) or ImageSharp.
* Build `Icon` with multiple embedded sizes for tray.

### QuitMode enum

Define a simple enum to clarify flow:

```csharp
enum QuitMode
{
    None,
    ForDuration,
    UntilDateTime
}
```

### AppState Globals

```csharp
internal static class AppState
{
    public static string AppName = "Stay Awake";
    public static bool DEBUG_IS_ON = false;
    public static bool SINGLE_INSTANCE_IS_ON = false;

    public static string? ImagePath;
    public static string? LogPath;

    public static QuitMode QuitMode = QuitMode.None;
    public static DateTimeOffset? TargetLocal;
    public static TimeSpan? ForDuration;

    public static string InstanceMutexName =
        "StayAwake_Mutex_GUID-CHANGE-THIS";
}
```

### ImageAssets struct

```csharp
struct ImageAssets
{
    public Bitmap Original;
    public Bitmap Squared;
    public Icon MultiSizeIcon;
}
```

---

## 5) Testing Plan

### Iteration 1 (Setup/Init only)

* `--help` prints usage.
* `--icon C:\badpath.png` → error.
* `--for 2h`, `--for 90m`, `--for 0` all valid.
* `--for nonsense` → error.
* `--until "2025-1-2 3:2:1"` accepted.
* `--until "2025-02-30 12:00:00"` rejected.
* Launch twice → second exits with message.

### Iteration 2+

* Tray icon displays.
* Tooltip updates with ETA.
* Timers tick at adaptive cadence.
* Stay-Awake state toggled.

### DST tests

* Pass nonexistent local time (spring forward) → reject.
* Pass ambiguous local time (fall back) → reject.

---

## 6) Environment & Toolchain

* **Hyper-V VM**: Windows 11 Enterprise Evaluation (Gen2).
* **Visual Studio 2022 Community (latest)** with workload: **.NET desktop development**.
* **.NET 8 SDK** + Windows 11 SDK installed.
* Project targets `net8.0-windows`.
* Manifest enables `PerMonitorV2` DPI awareness.

### Publish Profile

* Mode: Folder.
* Runtime: win-x64.
* Self-contained: true.
* Single file: true.
* Trim: false.
* ReadyToRun: optional.

### Export/Transfer

* Export VS settings: *Tools → Import/Export*.
* Transfer solution: zip and copy, or use host-VM shared folder.
* Copy EXE: publish → take from `bin\Release\net8.0-windows\publish\`.

### VM Hygiene

* Take checkpoint after setup.
* Use golden VM for experiments.

---

## 7) Developer Guidance

* **Think like a maintainer**: assume the next dev is a beginner.
* **Never skip comments** — no code should rely solely on context.
* **Prefer clarity over performance**.
* **Unit-test parsing functions separately** (e.g., ForDuration parser).
* **Encapsulate** tray logic in a helper class — don’t bloat `Form1.cs`.
* **Iterate**: always implement, run, and test small slices before proceeding.

---

## 8) Kickoff Checklist for Iteration 1

* [ ] Add `AppState` and `QuitMode`.
* [ ] Implement CLI parse + validation.
* [ ] Add `Fatal()`.
* [ ] Add Mutex guard.
* [ ] Debug traces visible in VS Output.
* [ ] Smoke-test form proving pipeline runs.

---

✔ I’ve checked line-by-line: no content from your prior spec has been dropped.
✔ Additions: stricter CLI validation, image struct, QuitMode enum, explicit debug rules, DST test cases, and environment hygiene details.

---

Would you like me to also **produce the Iteration 1 code skeleton** (Program.cs + Args.cs with all comments and debug scaffolding) updated to match *this* expanded spec? That way you’d be ready to run tests immediately.
