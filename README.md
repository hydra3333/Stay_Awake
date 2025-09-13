Here’s a fresh, drop-in **README.md** that matches the current app (v1.3.3), including the new `--icon` override, image priority, native button style, About-window behavior, and your build/zip notes. It supersedes the previous README you shared.&#x20;

---

# Stay\_Awake

A lightweight system-tray utility that keeps your computer **awake** (no automatic sleep/hibernation) while still allowing the **display to sleep** if you want power savings. Built with Python + tkinter and packaged with PyInstaller for simple distribution.

## Highlights

* **Keeps the system awake** for long tasks; cleans up on exit
* **System tray** icon with a simple menu (Show Window / About / Quit)
* **Native Windows look** via `ttk` (no custom “gaudy” colors)
* **Main window**: centered image + buttons along the bottom

  * **X** closes the app (graceful exit)
  * **Minimize to System Tray** hides the window; app keeps running
  * **Quit** exits the app
* **About window** (modal): X / OK close it; **Minimize** behaves like X
* **Icon/Image selection with priority** (see below) and **auto-scaling** to fit
* Uses `wakepy` under the hood to request “stay awake” from the OS efficiently (Windows internally calls `SetThreadExecutionState`).&#x20;

---

## Icon / Image Sources & Scaling

**Priority (first usable wins):**

1. **CLI override**: `--icon "PATH\to\image"` (PNG/JPG/JPEG/WEBP/BMP/GIF/ICO)
2. **Embedded base64**: `EYE_IMAGE_BASE64` (if present and decodes)
3. **Files next to the app** (script folder or EXE folder), in this order:
   `Stay_Awake_icon.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`, `.gif`, `.ico`
4. **Drawn fallback**: a simple glyph (never crashes)

**Scaling**

* Window image is proportionally resized so max side ≤ **`MAX_DISPLAY_PX`** (default **512**).
* Tray icon is reduced to \~64px with a tiny transparent border to avoid clipping in some trays.

---

## Installation

### Option A — Run the EXE (no Python needed)

* Use the packaged `Stay_Awake.exe` (one-file) or the onedir folder build.
* If Defender/AV flags it, that’s typically a **false positive** for unsigned, new executables; allow it or report a false positive (see “Security / Defender notes” below).&#x20;

### Option B — Run from source (Python 3.13+ recommended)

```bash
pip install wakepy --no-cache-dir --upgrade --check-build-dependencies --upgrade-strategy eager --verbose
pip install pystray --no-cache-dir --upgrade --check-build-dependencies --upgrade-strategy eager --verbose
pip install Pillow --no-cache-dir --upgrade --check-build-dependencies --upgrade-strategy eager --verbose
```

Run it:

```bash
python Stay_Awake.py
# or pick an icon explicitly:
python Stay_Awake.py --icon "C:\Path\to\EyeOfHorus.png"
```

---

## Usage

* **Main window**: image centered; buttons at bottom.

  * **Minimize to System Tray** → hides main window (still running)
  * **About** → opens modal About dialog
  * **Quit** → exits the app
  * **Close (X)** → exits the app (same as Quit)
* **System tray**:

  * **Left-click / double-click**: Show Window
  * **Right-click**: menu (Show Window / About / Quit)

---

## Build & Package (PyInstaller)

> Windows `.pyw` runs with **pythonw\.exe** (no console). Some tray environments render alpha a bit differently; a 1–2px transparent border is added around the tray bitmap.

### One-file EXE (no console window)

```bat
rmdir /s /q .\dist
rmdir /s /q .\build
pyinstaller --clean --onefile --windowed --noconsole --name "Stay_Awake" Stay_Awake.py
copy /Y ".\dist\Stay_Awake.exe" ".\Stay_Awake.exe"
```

### One-dir app folder (no console window)

```bat
rmdir /s /q .\dist
rmdir /s /q .\build
pyinstaller --clean --onedir --windowed --noconsole --name "Stay_Awake" Stay_Awake.py

rem (Optional) Place icon images next to the EXE inside the app folder:
copy /Y Stay_Awake_icon.* ".\dist\Stay_Awake\"
```

### Zip the build (PowerShell)

**PS 5.1 (contents of `dist/` at ZIP root):**

```powershell
powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Sta -NonInteractive -WindowStyle Hidden -Command "Compress-Archive -Path '.\dist\*' -DestinationPath '.\Stay_Awake.zip' -Force -CompressionLevel Optimal"
```

**PS 7+ (strongest compression):**

```powershell
pwsh -NoLogo -NoProfile -Command "Compress-Archive -Path '.\dist\*' -DestinationPath '.\Stay_Awake.zip' -Force -CompressionLevel SmallestSize"
```

**Include `dist` as a top-level folder inside the ZIP:**

```powershell
powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Sta -NonInteractive -WindowStyle Hidden -Command "Compress-Archive -Path '.\dist' -DestinationPath '.\Stay_Awake.zip' -Force -CompressionLevel Optimal"
```

---

## Security / Defender notes

* Unsigned, newly built utilities can trigger **machine-learning** detections in Windows Defender.
* The code is simple and open; if flagged, **allow** the file, add an **exclusion**, or submit a **false-positive** report to Microsoft.&#x20;

---

## How it works (under the hood)

* Uses the `wakepy` library to request an **awake** state from the OS efficiently (low CPU, automatically released on exit).
* GUI is standard `tkinter` + `ttk`; tray integration by `pystray`; imaging by Pillow.&#x20;

---

## Troubleshooting

* **Tray icon not visible**: ensure your tray is set to show app icons; the icon may be grouped/hidden.&#x20;
* **Doesn’t prevent sleep**: check other sleep managers, and confirm power plan isn’t overriding.
* **About won’t close**: fixed long ago—ensure you’re on the **latest version**.&#x20;

---

## System requirements

* **Windows 10+** (primary target)
* **RAM** \~10–20 MB; negligible CPU when idle
* **From source**: Python **3.13+** recommended

---

## Command-line options

```
--icon "PATH"   Path to an image file used for the app window and tray icon.
                Absolute paths are safest (shortcuts may set a custom “Start in”).
```

