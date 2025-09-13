@echo on
@setlocal ENABLEDELAYEDEXPANSION
@setlocal enableextensions

REM Install python dependencies for Stay_Awake
pip install wakepy --no-cache-dir --upgrade --check-build-dependencies --upgrade-strategy eager --verbose
pip install pystray --no-cache-dir --upgrade --check-build-dependencies --upgrade-strategy eager --verbose
pip install Pillow --no-cache-dir --upgrade --check-build-dependencies --upgrade-strategy eager --verbose

REM Install PyInstaller if not already installed
pip install pyinstaller --no-cache-dir --upgrade --check-build-dependencies --upgrade-strategy eager --verbose

REM Build Stay_Awake onedir with no console window
rmdir /s /q .\dist >NUL 2>&1
del /f      .\Stay_Awake.zip >NUL 2>&1

pyinstaller --onefile --windowed --noconsole --name "Stay_Awake" Stay_Awake.py

REM  Powershell 5.1 compatible - Inside the zip dist is the top level it is not a subfolder
copy /y Stay_Awake_icon.* .\dist
powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Sta -NonInteractive -WindowStyle Hidden -Command "Compress-Archive -Path '.\dist\*' -DestinationPath '.\Stay_Awake.zip' -Force -CompressionLevel Optimal"

REM powershell 7+ only - Inside the zip dist is the top level it is not a subfolder
REM   powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Sta -NonInteractive -WindowStyle Hidden -Command "Compress-Archive -Path '.\dist\*' -DestinationPath '.\Stay_Awake.zip' -Force -CompressionLevel SmallestSize"
REM Inside the zip dist is a subfolder
REM   powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Sta -NonInteractive -WindowStyle Hidden -Command "Compress-Archive -Path '.\dist' -DestinationPath '.\Stay_Awake.zip' -Force -CompressionLevel Optimal"

pause
exit
