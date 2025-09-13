@echo on
@setlocal ENABLEDELAYEDEXPANSION
@setlocal enableextensions

REM ---------------------------------------------------------------------------
REM Optional: skip pip installs (uncomment the next line to skip that section)
REM goto :after_pip_installs
REM ---------------------------------------------------------------------------

REM Install python dependencies for Stay_Awake
pip install wakepy --no-cache-dir --upgrade --check-build-dependencies --upgrade-strategy eager --verbose
pip install pystray --no-cache-dir --upgrade --check-build-dependencies --upgrade-strategy eager --verbose
pip install Pillow --no-cache-dir --upgrade --check-build-dependencies --upgrade-strategy eager --verbose

REM Install PyInstaller if not already installed
rmdir /s /q .\dist  >NUL 2>&1
rmdir /s /q .\build >NUL 2>&1
del /f      .\Stay_Awake.spec >NUL 2>&1
del /f      .\Stay_Awake.exe  >NUL 2>&1
pip install pyinstaller --no-cache-dir --upgrade --check-build-dependencies --upgrade-strategy eager --verbose

:after_pip_installs

REM ---------------------------------------------------------------------------
REM Build Stay_Awake.exe (onefile, no console window)
REM ---------------------------------------------------------------------------
rmdir /s /q .\dist  >NUL 2>&1
rmdir /s /q .\build >NUL 2>&1
del /f      .\Stay_Awake.spec >NUL 2>&1
del /f      .\Stay_Awake.zip  >NUL 2>&1

pyinstaller --clean --onefile --windowed --noconsole --name "Stay_Awake" Stay_Awake.py
copy /Y ".\dist\Stay_Awake.exe" ".\Stay_Awake.exe" >NUL

REM ---------------------------------------------------------------------------
REM Build Stay_Awake (onedir, no console window)
REM ---------------------------------------------------------------------------
rmdir /s /q .\dist  >NUL 2>&1
rmdir /s /q .\build >NUL 2>&1
del /f      .\Stay_Awake.spec >NUL 2>&1
del /f      .\Stay_Awake.zip  >NUL 2>&1

pyinstaller --clean --onedir --windowed --noconsole --name "Stay_Awake" Stay_Awake.py
REM Place optional icon images next to the EXE (inside the app folder):
copy /Y Stay_Awake_icon.* ".\dist\Stay_Awake\" >NUL 2>&1

REM ---------------------------------------------------------------------------
REM Zip the onedir output (PowerShell 5.1 compatible)
REM   - Using the contents of dist\Stay_Awake so the ZIP root is the app itself
REM ---------------------------------------------------------------------------
powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Sta -NonInteractive ^
  -Command "Compress-Archive -Path '.\dist\Stay_Awake\*' -DestinationPath '.\Stay_Awake.zip' -Force -CompressionLevel Optimal"

set "ERR=%ERRORLEVEL%"

rmdir /s /q .\dist  >NUL 2>&1
rmdir /s /q .\build >NUL 2>&1
del /f      .\Stay_Awake.spec >NUL 2>&1

echo.
echo ==== Compress-Archive exit code: %ERR%
echo Press any key to continue . . .
pause >NUL

endlocal
exit /b
