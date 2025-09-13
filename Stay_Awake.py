#!/usr/bin/env python3

__version__ = "1.3.3"
__author__ = "Open Source"
__description__ = "System tray application to prevent sleep"

# Stay_Awake System Tray Application
# Keeps system awake, runs in system tray with minimal GUI
# 
# .pyw runs with pythonw.exe (no console window).
# pythonw.exe doesn't create a console window
# Drawback: You lose all the print() messages, but the app works silently.                                                                                  
#
# ------------------------------------------------------------------------------
# CLI summary:
#   --icon "PATH"  -> highest priority image source (PNG/JPG/JPEG/WEBP/BMP/GIF/ICO)
#   Fallbacks      -> base64 -> Stay_Awake_icon.* (ordered list) -> drawn glyph
#   All images are auto-scaled to fit (<= MAX_DISPLAY_PX), aspect ratio preserved.
# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------
# Stay_Awake – Requirements / Behavior Spec (v1.3.2)
# ------------------------------------------------------------------------------
# Purpose
#   Keep the system awake with a minimal GUI and a system-tray icon.
#
# CLI
#   python Stay_Awake.py [--icon "PATH"]
#     --icon "PATH"  Optional quoted path to an image file used for both
#                    the tray icon and the window image.
#                    Relative paths are resolved from the current working dir.
#
# Image Source Priority (first usable wins)
#   1) CLI override:      --icon "PATH"
#   2) Internal base64:   EYE_IMAGE_BASE64 (if non-empty and decodes)
#   3) File fallbacks (in the script folder, in this order):
#        Stay_Awake_icon.png
#        Stay_Awake_icon.jpg
#        Stay_Awake_icon.jpeg
#        Stay_Awake_icon.webp
#        Stay_Awake_icon.bmp
#        Stay_Awake_icon.gif
#        Stay_Awake_icon.ico
#   4) Drawn fallback:    a simple vector-like Eye glyph (never crashes)
#
# Supported Image Formats
#   PNG, JPG/JPEG, WEBP, BMP, GIF, ICO (loaded via Pillow; alpha supported).
#
# Image Scaling (non-square friendly)
#   - The window image is proportionally resized so the longest side <= MAX_DISPLAY_PX.
#   - MAX_DISPLAY_PX is an internal constant (default 512) – change if needed.
#   - The tray icon is scaled down to ~64 px (with a tiny transparent border to
#     avoid edge clipping in some tray implementations).
#
# Main Window (native/vanilla look via ttk)
#   - Title: "Stay_Awake"
#   - Layout: centered image (auto-scaled), horizontal separator, buttons along
#     the bottom.
#   - Buttons:
#       • Minimize to System Tray  -> hides the main window (app keeps running)
#       • About                    -> opens modal About dialog
#       • Quit                     -> exits the app gracefully
#   - Window close (X): exits the app gracefully (same as Quit).
#
# About Window (modal dialog)
#   - Shown centered, transient to the main window, grab-set (modal).
#   - Displays a smaller, auto-scaled version of the image, product text, and
#     OK/Minimize buttons.
#   - OK:        closes the About window.
#   - Minimize:  behaves like the window X (closes the About window).
#   - Window close (X): closes the About window.
#   - Keyboard:  Esc/Enter both close the About window.
#
# System Tray
#   - Right-click menu: Show Window (default action), About, Quit.
#   - Default (double-click/left): Show Window (bring main window to front).
#
# Keep-Awake Lifecycle
#   - Uses wakepy.keep.running() context to inhibit system sleep/hibernation.
#   - On Quit or process signals (SIGINT/SIGTERM), the context is exited and
#     normal power management is restored.
#
# Error Handling / Robustness
#   - Missing/bad image sources never crash the app: it falls back to a simple
#     drawn glyph.
#   - Base64 decode errors are logged and skipped (fallback continues).
#   - All exits attempt to clean up the keep-awake context and tray icon.
#
# Look & Feel
#   - Uses ttk widgets for native/vanilla Windows styling.
#   - Buttons are placed at the bottom; no “gaudy” manual colors.
#   - Windows are centered on open.
#
# Configuration Knobs
#   - MAX_DISPLAY_PX (default 512): max long-side for displayed image.
#   - EYE_IMAGE_BASE64: paste your base64 here (leave empty to prefer files/CLI).
#   - IMAGE_CANDIDATES: ordered list of fallback filenames (in script dir).
#
# Dependencies
#   - Python 3.13+ recommended
#   - pip install these:
#         pip install wakepy --no-cache-dir --upgrade --check-build-dependencies --upgrade-strategy eager --verbose
#         pip install pystray --no-cache-dir --upgrade --check-build-dependencies --upgrade-strategy eager --verbose
#         pip install Pillow --no-cache-dir --upgrade --check-build-dependencies --upgrade-strategy eager --verbose
#         pip install pyinstaller --no-cache-dir --upgrade --check-build-dependencies --upgrade-strategy eager --verbose
#
# Packaging / Notes
#   - Running as .pyw uses pythonw.exe (no console) on Windows.
#   - Some tray environments render transparency slightly differently; a 1–2 px
#     transparent border is added around the tray bitmap to avoid clipping.
#
# Building  (Build Stay_Awake.exe with no console window)
#   rmdir /s /q .\dist
#   rmdir /s /q .\build
#   pyinstaller --clean --onefile --windowed --noconsole --name "Stay_Awake" Stay_Awake.py
#   copy /Y ".\dist\Stay_Awake.exe" ".\Stay_Awake.exe"
#
# Build Stay_Awake 'onedir' with no console window
#   rmdir /s /q .\dist
#   rmdir /s /q .\build
#   pyinstaller --clean --onedir --windowed --noconsole --name "Stay_Awake" Stay_Awake.py
#   rem Place optional icon images next to the EXE (inside the app folder):
#   copy /Y Stay_Awake_icon.* ".\dist\Stay_Awake\"
#
# Zip (PowerShell 5.1 compatible)
#   # ZIP contains the CONTENTS of dist (no top-level 'dist' folder inside):
#   powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Sta -NonInteractive -WindowStyle Hidden -Command "Compress-Archive -Path '.\dist\*' -DestinationPath '.\Stay_Awake.zip' -Force -CompressionLevel Optimal"
#
# Zip (PowerShell 7+ only; strongest compression)
#   # ZIP contains the CONTENTS of dist (no top-level 'dist' folder inside):
#   pwsh -NoLogo -NoProfile -Command "Compress-Archive -Path '.\dist\*' -DestinationPath '.\Stay_Awake.zip' -Force -CompressionLevel SmallestSize"
#
# Zip (include 'dist' as a top-level folder inside the ZIP)
#   powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Sta -NonInteractive -WindowStyle Hidden -Command "Compress-Archive -Path '.\dist' -DestinationPath '.\Stay_Awake.zip' -Force -CompressionLevel Optimal"
#
# ------------------------------------------------------------------------------ 

import sys
import os
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from wakepy import keep
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw, ImageTk
import atexit
import signal
import base64
import io
from pathlib import Path
import argparse

# --------------------------------------------------------------------
# Config
# --------------------------------------------------------------------
MAX_DISPLAY_PX = 512  # max long-side pixels for images in windows

# --------------------------------------------------------------------
# PASTE YOUR BASE64 HERE (leave empty to use file/CLI fallback)
# --------------------------------------------------------------------
EYE_IMAGE_BASE64 = ("")  # e.g. ("iVBORw0KGgoAAA..." "more...")

# Candidate file names (same folder as this script) in this order
IMAGE_CANDIDATES = [
    "Stay_Awake_icon.png",
    "Stay_Awake_icon.jpg",
    "Stay_Awake_icon.jpeg",
    "Stay_Awake_icon.webp",
    "Stay_Awake_icon.bmp",
    "Stay_Awake_icon.gif",
    "Stay_Awake_icon.ico",
]


class Stay_AwakeTrayApp:
    def __init__(self, icon_override_path: str | None = None):
        self.running = False
        self.icon = None
        self.main_window = None
        self.keep_awake_context = None
        self.window_visible = True

        self._cached_photo_main = None  # keep reference to prevent GC
        self._cached_photo_about = None

        # NEW: optional CLI override path
        self.icon_override_path = icon_override_path

        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    # -------------------- Image helpers --------------------

    def _script_dir(self) -> Path:
        # When frozen by PyInstaller:
        #   - onefile/onedir: sys.executable is the bundled EXE; use its folder
        try:
            import sys as _sys
            if getattr(_sys, "frozen", False):
                return Path(_sys.executable).resolve().parent
            return Path(__file__).resolve().parent
        except Exception:
            return Path(os.getcwd())


    def _try_decode_base64(self):
        """Return PIL.Image from base64 or None if not decodable/empty."""
        raw = "".join(EYE_IMAGE_BASE64) if isinstance(EYE_IMAGE_BASE64, (list, tuple)) else str(EYE_IMAGE_BASE64 or "")
        if not raw.strip():
            return None
        try:
            return Image.open(io.BytesIO(base64.b64decode(raw))).convert("RGBA")
        except Exception as e:
            print(f"Base64 image decode failed, will try file fallback: {e}")
            return None

    def _try_load_override_file(self):
        """If --icon PATH was provided, try to load it first."""
        if not self.icon_override_path:
            return None
        try:
            p = Path(self.icon_override_path).expanduser()
            # If not absolute, resolve relative to current working dir
            if not p.is_absolute():
                p = (Path.cwd() / p).resolve()
            if p.exists():
                print(f"Loading icon from CLI override: {p}")
                return Image.open(p).convert("RGBA")
            else:
                print(f"CLI override not found: {p}")
        except Exception as e:
            print(f"Failed to load CLI override image: {e}")
        return None

    def _try_load_from_files(self):
        """Try the candidate filenames in order; return PIL.Image or None."""
        folder = self._script_dir()
        for name in IMAGE_CANDIDATES:
            p = folder / name
            if p.exists():
                try:
                    print(f"Loading icon from file: {p.name}")
                    return Image.open(p).convert("RGBA")
                except Exception as e:
                    print(f"Failed to load {p.name}: {e}")
        return None

    def _fallback_draw_eye(self, size=(640, 490)):
        """Last-resort symbolic drawing so the app never crashes."""
        image = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        w, h = size
        draw.arc([10, h//3, w-10, h-40], start=200, end=-20, width=18, fill="black")
        draw.arc([10, 40, w-10, h//1.7], start=30, end=160, width=18, fill="black")
        draw.line([w//3.2, h//1.9, w//2.3, h-10], width=18, fill="black")
        cx, cy = int(w*0.82), int(h*0.83)
        r = int(min(w, h)*0.12)
        draw.arc([cx-r, cy-r, cx+r, cy+r], 60, 370, width=18, fill="black")
        pr = int(min(w, h)*0.11)
        pcx, pcy = int(w*0.48), int(h*0.55)
        draw.ellipse([pcx-pr, pcy-pr, pcx+pr, pcy+pr], fill="black", outline="black")
        draw.ellipse([pcx-12, pcy-12, pcx+3, pcy+3], fill="white", outline="white")
        return image

    def _load_eye_image(self) -> Image.Image:
        """
        Load image using priority:
        1) CLI override (--icon path)
        2) internal base64
        3) files in IMAGE_CANDIDATES
        4) drawn fallback
        """
        img = self._try_load_override_file()
        if img is None:
            img = self._try_decode_base64()
        if img is None:
            img = self._try_load_from_files()
        if img is None:
            img = self._fallback_draw_eye()
        return img.convert("RGBA")

    @staticmethod
    def _resize_keep_aspect(img: Image.Image, max_px: int) -> Image.Image:
        w, h = img.size
        scale = min(max_px / max(w, 1), max_px / max(h, 1), 1.0)
        new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
        return img if new_size == img.size else img.resize(new_size, Image.LANCZOS)

    def get_display_image_tk(self, max_px=MAX_DISPLAY_PX):
        pil = self._load_eye_image()
        pil = self._resize_keep_aspect(pil, max_px)
        return ImageTk.PhotoImage(pil)

    # -------------------- UI creation --------------------

    def create_image(self):
        """Create tray icon image (down-sized from loaded Eye image)."""
        pil = self._load_eye_image()
        icon_pil = self._resize_keep_aspect(pil, 64)
        # Add small transparent border so rounded icons don't clip
        bordered = Image.new("RGBA", (icon_pil.width + 2, icon_pil.height + 2), (0, 0, 0, 0))
        bordered.paste(icon_pil, (1, 1))
        return bordered

    def _center_window(self, win):
        win.update_idletasks()
        w, h = win.winfo_width(), win.winfo_height()
        sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
        x, y = (sw - w) // 2, (sh - h) // 2
        win.geometry(f"+{x}+{y}")

    def create_main_window(self):
        """Main control window (native look)."""
        self.main_window = tk.Tk()
        self.main_window.title("Stay_Awake")
        self.main_window.resizable(True, True)

        # Main window “X” should EXIT the app (gracefully)
        self.main_window.protocol("WM_DELETE_WINDOW", self.quit_from_window)

        # Layout
        container = ttk.Frame(self.main_window, padding=(16, 16, 16, 16))
        container.pack(fill=tk.BOTH, expand=True)

        # Image centered, scaled to <= 512 px
        self._cached_photo_main = self.get_display_image_tk(MAX_DISPLAY_PX)
        ttk.Label(container, image=self._cached_photo_main, anchor="center").pack(side=tk.TOP, pady=(0, 12))

        ttk.Separator(container, orient="horizontal").pack(fill="x", pady=(0, 8))

        # Buttons at bottom (vanilla style)
        btns = ttk.Frame(container)
        btns.pack(side=tk.BOTTOM, fill=tk.X, pady=(8, 0))

        ttk.Button(btns, text="Minimize to System Tray", command=self.minimize_to_tray).pack(
            side=tk.LEFT, padx=(0, 8)
        )
        ttk.Button(btns, text="About", command=self.show_about).pack(side=tk.LEFT)
        ttk.Button(btns, text="Quit", command=self.quit_from_window).pack(side=tk.RIGHT, padx=(8, 0))

        # Status hint
        ttk.Label(container, text="Right-click the tray icon for options.", foreground="gray").pack(
            side=tk.BOTTOM, pady=(8, 0)
        )

        self._center_window(self.main_window)

    # -------------------- About window --------------------

    def show_about(self, icon=None, item=None):
        """A real modal About dialog. X/OK close it. Minimizing acts like close."""
        parent = self.main_window if self.main_window else None

        # Create About Toplevel
        about = tk.Toplevel(parent) if parent else tk.Tk()
        about.title("About – Stay_Awake")
        about.resizable(False, False)
        if parent:
            about.transient(parent)
            about.grab_set()  # modal over parent

        def _close():
            try:
                about.grab_release()
            except Exception:
                pass
            about.destroy()

        about.protocol("WM_DELETE_WINDOW", _close)
        about.bind("<Escape>", lambda e: _close())
        about.bind("<Return>", lambda e: _close())

        # If user clicks minimize on the title bar, treat it like close
        def _on_unmap(event):
            if about.state() == "iconic":
                _close()
        about.bind("<Unmap>", _on_unmap)

        frame = ttk.Frame(about, padding=(16, 16, 16, 12))
        frame.pack(fill=tk.BOTH, expand=True)

        # Smaller image on About
        self._cached_photo_about = self.get_display_image_tk(min(320, MAX_DISPLAY_PX))
        ttk.Label(frame, image=self._cached_photo_about).pack(pady=(0, 8))

        ttk.Label(
            frame,
            text=(f"Stay_Awake v{__version__}\n"
                  "Prevents system sleep & hibernation.\n"
                  "Display sleep is allowed."),
            justify="center",
        ).pack(pady=(0, 8))

        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=(0, 8))

        # Buttons
        btns = ttk.Frame(frame)
        btns.pack(side=tk.BOTTOM, fill=tk.X)

        # “Minimize” should behave like the window X (i.e., close the About window)
        ttk.Button(btns, text="Minimize", command=_close).pack(side=tk.LEFT)
        ttk.Button(btns, text="OK", command=_close).pack(side=tk.RIGHT)

        self._center_window(about)

    # -------------------- Window controls --------------------

    def minimize_to_tray(self):
        if self.main_window:
            self.main_window.withdraw()
            self.window_visible = False

    def show_main_window(self, icon=None, item=None):
        if self.main_window:
            self.main_window.deiconify()
            self.main_window.lift()
            self.main_window.focus_force()
            self.window_visible = True

    def quit_from_window(self):
        self.quit_application(None, None)

    # -------------------- Core / lifecycle --------------------

    def start_Stay_Awake(self):
        try:
            self.keep_awake_context = keep.running()
            self.keep_awake_context.__enter__()
            self.running = True
            print("Stay_Awake activated")
        except Exception as e:
            if self.main_window:
                messagebox.showerror("Error", f"Failed to activate Stay_Awake: {e}")
            sys.exit(1)

    def cleanup(self):
        if self.running and self.keep_awake_context:
            print("Cleaning up - restoring normal power management.")
            try:
                self.keep_awake_context.__exit__(None, None, None)
                self.running = False
                self.keep_awake_context = None
                print("Normal power management restored")
            except Exception as e:
                print(f"Error during cleanup: {e}")

    def signal_handler(self, signum, frame):
        print(f"Received signal {signum}, cleaning up.")
        self.cleanup()
        if self.icon:
            try:
                self.icon.visible = False
                self.icon.stop()
            except Exception:
                pass
        sys.exit(0)

    def quit_application(self, icon, item):
        print("User requested quit")
        self.cleanup()
        if self.main_window:
            try:
                self.main_window.quit()
                self.main_window.destroy()
            except Exception:
                pass
        if self.icon:
            try:
                self.icon.visible = False
                self.icon.stop()
            except Exception:
                pass
        time.sleep(0.1)
        sys.exit(0)

    # -------------------- Tray --------------------

    def create_tray_icon(self):
        image = self.create_image()
        menu = pystray.Menu(
            item("Show Window", self.show_main_window, default=True),
            item("About", self.show_about),
            pystray.Menu.SEPARATOR,
            item("Quit", self.quit_application),
        )
        self.icon = pystray.Icon("Stay_Awake", image, "Stay_Awake - System Awake", menu)
        self.icon.default_action = self.show_main_window
        self.icon.run()

    def run(self):
        self.start_Stay_Awake()
        self.create_main_window()
        tray_thread = threading.Thread(target=self.create_tray_icon, daemon=True)
        tray_thread.start()
        self.main_window.mainloop()


def main():
    # ---------- CLI parsing (NEW) ----------
    parser = argparse.ArgumentParser(description="Stay_Awake system tray tool")
    parser.add_argument(
        "--icon",
        dest="icon_path",
        metavar="PATH",
        help="Path to an image file (PNG/JPG/JPEG/WEBP/BMP/GIF/ICO) used for the app icon & window image.",
    )
    args = parser.parse_args()

    try:
        app = Stay_AwakeTrayApp(icon_override_path=args.icon_path)
        app.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        print("Final cleanup...")
        sys.exit(1)


if __name__ == "__main__":
    main()
