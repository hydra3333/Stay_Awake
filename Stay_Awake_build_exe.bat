@echo on
@setlocal ENABLEDELAYEDEXPANSION
@setlocal enableextensions

REM Install python dependencies for Stay_Awake
pip install wakepy --no-cache-dir --upgrade --check-build-dependencies --upgrade-strategy eager --verbose
pip install pystray --no-cache-dir --upgrade --check-build-dependencies --upgrade-strategy eager --verbose
pip install Pillow --no-cache-dir --upgrade --check-build-dependencies --upgrade-strategy eager --verbose

REM Install PyInstaller if not already installed
pip install pyinstaller --no-cache-dir --upgrade --check-build-dependencies --upgrade-strategy eager --verbose

REM Build Stay_Awake.exe with no console window
pyinstaller --onefile --windowed --noconsole --name "Stay_Awake" Stay_Awake.py

REM Copy the executable to current directory for easy access
copy /Y "dist\Stay_Awake.exe" ".\Stay_Awake.exe"

echo.
echo Build complete! Stay_Awake.exe created.
echo You can now double-click Stay_Awake.exe to run without console.
echo.

pause
exit