@echo off
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

DEL /F ".\tmp.py" >NUL 2>&1
echo import sys, PIL, PIL.Image as I >>".\tmp.py"
echo print^("Python:", sys.version^) >>".\tmp.py"
echo print^("Pillow:", PIL.__version__^) >>".\tmp.py"
echo print^("PIL.Image from:", I.__file__^) >>".\tmp.py"
echo try: >>".\tmp.py"
echo     from PIL import IcoImagePlugin >>".\tmp.py"
echo     print^("IcoImagePlugin from:", IcoImagePlugin.__file__^) >>".\tmp.py"
echo except Exception as e: >>".\tmp.py"
echo     print^("IcoImagePlugin import failed:", e^) >>".\tmp.py"
echo.
REM echo type ".\tmp.py"
REM type ".\tmp.py"
REM echo.
REM echo python ".\tmp.py"
python ".\tmp.py"
echo.
echo list all installed Pythons
py -0p            
echo.

REM ---------- Create ICO from Image (if found) ----------
:create_icons_from_image
echo Creating ICO from image if found...
set "root=%~dp0"
set "targetIcon=%root%Stay_Awake_icon.ico"
set "targetIcon_option="
set "sourceImage="
del /f "!targetIcon!" >NUL 2>&1
REM Check for image files in order of preference
for %%f in ("Stay_Awake_icon.png" "Stay_Awake_icon.jpg" "Stay_Awake_icon.jpeg" "Stay_Awake_icon.webp" "Stay_Awake_icon.bmp" "Stay_Awake_icon.gif") do (
    if exist "%root%%%~f" (
        set "sourceImage=%root%%%~f"
        echo Create ICON from PNG: Found source image: !sourceImage!
        goto :found_image
    )
)
:found_image
set "targetIcon_option="
if defined sourceImage (
    set "sourceImage_python=!sourceImage:\=/!"
    set "targetIcon_python=!targetIcon:\=/!"
    REM echo sourceImage='!sourceImage!'  targetIcon='!targetIcon!'
    REM echo sourceImage_python='!sourceImage_python!'  targetIcon_python='!targetIcon_python!'
    set "tmp_icon_creator=.\tmp_icon_creator.py"
    DEL /F "!tmp_icon_creator!" >NUL 2>&1
    REM
    call :create_t3
    REM
    REM echo.
    REM echo type "!tmp_icon_creator!"
    REM type "!tmp_icon_creator!"
    REM echo.
    REM echo python "!tmp_icon_creator!"
    python "!tmp_icon_creator!"
    set "EL=!ERRORLEVEL!"
    DEL /F "!tmp_icon_creator!" >NUL 2>&1
    if !EL! equ 0 (
        echo Create ICON from PNG: Successfully created ICO file !targetIcon!
        set "targetIcon_option=--icon "!targetIcon!""
    ) else (
        echo Create ICON from PNG: Failed to create ICO file '!targetIcon!'
    )
) else (
    echo Create ICON from PNG: No source image found for ICON creation.
)
REM
set "tmp_icon_info_displayer=.\tmp_icon_info_displayer.py"
DEL /F "!tmp_icon_info_displayer!" >NUL 2>&1
REM
call :display_d3
REM
REM echo type "!tmp_icon_info_displayer!"
REM echo.
REM type "!tmp_icon_info_displayer!"
REM echo.
REM echo python "!tmp_icon_info_displayer!"
python "!tmp_icon_info_displayer!"
DEL /F "!tmp_icon_info_displayer!" >NUL 2>&1

REM ---------------------------------------------------------------------------
REM Build Stay_Awake.exe (onefile, no console window)
REM ---------------------------------------------------------------------------
:build_onefile
rmdir /s /q .\dist  >NUL 2>&1
rmdir /s /q .\build >NUL 2>&1
del /f      .\Stay_Awake.spec >NUL 2>&1
del /f      .\Stay_Awake.zip  >NUL 2>&1

if exist "!targetIcon!" (
    echo.
    echo pyinstaller --clean --onefile --windowed --noconsole --icon "!targetIcon!" --name "Stay_Awake" Stay_Awake.py
    echo.
    pyinstaller --clean --onefile --windowed --noconsole --icon "!targetIcon!" --name "Stay_Awake" Stay_Awake.py
    echo.
    echo ********** pyinstaller created onefile Stay_Awake WITH system tray .ico icon file
    echo.
) ELSE (
    echo.
    echo pyinstaller --clean --onefile --windowed --noconsole --name "Stay_Awake" Stay_Awake.py
    pyinstaller --clean --onefile --windowed --noconsole --name "Stay_Awake" Stay_Awake.py
    echo.
    echo ********** pyinstaller created onefile Stay_Awake WITHOUT system tray .ico icon file
    echo.
)
COPY /Y "!sourceImage!" ".\dist\" >NUL 2>&1
COPY /Y "!targetIcon!" ".\dist\" >NUL 2>&1
REM echo.
REM echo DIR /S /B ".\dist"
REM DIR /S /B ".\dist"
REM echo.
REM echo DIR /S /B ".\build"
REM DIR /S /B ".\build"
REM echo.

set "target_zip_file=.\Stay_Awake_onefile.zip"
echo powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Sta -NonInteractive  -Command "Compress-Archive -Path '.\dist\*' -DestinationPath '!target_zip_file!' -Force -CompressionLevel Optimal" 
powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Sta -NonInteractive  -Command "Compress-Archive -Path '.\dist\*' -DestinationPath '!target_zip_file!' -Force -CompressionLevel Optimal" 
set "ERR=%ERRORLEVEL%"
echo ==== onefile Compress-Archive exit code: %ERR%

REM ---------------------------------------------------------------------------
REM Build Stay_Awake (onedir, no console window)
REM ---------------------------------------------------------------------------
:build_onedir
rmdir /s /q .\dist  >NUL 2>&1
rmdir /s /q .\build >NUL 2>&1
del /f      .\Stay_Awake.spec >NUL 2>&1
del /f      .\Stay_Awake.zip  >NUL 2>&1
if exist "!targetIcon!" (
    echo.
    echo pyinstaller --clean --onedir --windowed --noconsole --icon "!targetIcon!" --name "Stay_Awake" Stay_Awake.py
    echo.
    pyinstaller --clean --onedir --windowed --noconsole --icon "!targetIcon!" --name "Stay_Awake" Stay_Awake.py
    echo.
    echo ********** pyinstaller created onedir Stay_Awake WITH system tray .ico icon file
    echo.
) ELSE (
    echo.
    echo pyinstaller --clean --onedir --windowed --noconsole --name "Stay_Awake" Stay_Awake.py
    echo.
    pyinstaller --clean --onedir --windowed --noconsole --name "Stay_Awake" Stay_Awake.py
    echo.
    echo ********** pyinstaller created onedir Stay_Awake WITHOUT system tray .ico icon file
    echo.
)
REM Place optional icon images next to the EXE (inside the app folder):
COPY /Y "!sourceImage!" ".\dist\Stay_Awake\" >NUL 2>&1
COPY /Y "!targetIcon!"  ".\dist\Stay_Awake\" >NUL 2>&1

REM ---------------------------------------------------------------------------
REM Zip the onedir output (PowerShell 5.1 compatible)
REM   - Using the contents of dist\Stay_Awake so the ZIP root is the app itself
REM ---------------------------------------------------------------------------
set "target_zip_file=.\Stay_Awake_onedir.zip"
echo powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Sta -NonInteractive -Command "Compress-Archive -Path '.\dist\Stay_Awake\*' -DestinationPath '!target_zip_file!' -Force -CompressionLevel Optimal"
powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Sta -NonInteractive -Command "Compress-Archive -Path '.\dist\Stay_Awake\*' -DestinationPath '!target_zip_file!' -Force -CompressionLevel Optimal"
set "ERR=%ERRORLEVEL%"
echo ==== onedir Compress-Archive exit code: %ERR%

rmdir /s /q .\dist  >NUL 2>&1
rmdir /s /q .\build >NUL 2>&1
del /f      .\Stay_Awake.spec >NUL 2>&1

set "target_zip_file=.\Stay_Awake_onefile.zip"
echo.
echo Content of root folder in "!target_zip_file!" :
call :zip_top_folder_lister "!target_zip_file!"
echo.

set "target_zip_file=.\Stay_Awake_onedir.zip"
echo.
echo Content of root folder in "!target_zip_file!" :
call :zip_top_folder_lister "!target_zip_file!"
echo.

echo Press any key to continue . . .
pause >NUL

endlocal
exit /b

:create_t3
echo In create_t3
    echo import os >>"!tmp_icon_creator!"
    echo from PIL import Image, ImageOps >>"!tmp_icon_creator!"
    echo def pad_to_square_edge_stretch^(im: Image.Image^) -^> Image.Image: >>"!tmp_icon_creator!"
    echo     im = ImageOps.exif_transpose^(im^).convert^("RGBA"^) >>"!tmp_icon_creator!"
    echo     w, h = im.size >>"!tmp_icon_creator!"
    echo     if w == h: >>"!tmp_icon_creator!"
    echo         return im >>"!tmp_icon_creator!"
    echo     side = max^(w, h^) >>"!tmp_icon_creator!"
    echo     lp = ^(side - w^) // 2 >>"!tmp_icon_creator!"
    echo     rp = side - w - lp >>"!tmp_icon_creator!"
    echo     tp = ^(side - h^) // 2 >>"!tmp_icon_creator!"
    echo     bp = side - h - tp >>"!tmp_icon_creator!"
    echo     sq = Image.new^("RGBA", ^(side, side^), ^(0, 0, 0, 0^)^) >>"!tmp_icon_creator!"
    echo     if tp: >>"!tmp_icon_creator!"
    echo         strip = im.crop^(^(0, 0, w, 1^)^).resize^(^(w, tp^), Image.NEAREST^) >>"!tmp_icon_creator!"
    echo         sq.paste^(strip, ^(lp, 0^)^) >>"!tmp_icon_creator!"
    echo     if bp: >>"!tmp_icon_creator!"
    echo         strip = im.crop^(^(0, h-1, w, h^)^).resize^(^(w, bp^), Image.NEAREST^) >>"!tmp_icon_creator!"
    echo         sq.paste^(strip, ^(lp, tp + h^)^) >>"!tmp_icon_creator!"
    echo     if lp: >>"!tmp_icon_creator!"
    echo         strip = im.crop^(^(0, 0, 1, h^)^).resize^(^(lp, h^), Image.NEAREST^) >>"!tmp_icon_creator!"
    echo         sq.paste^(strip, ^(0, tp^)^) >>"!tmp_icon_creator!"
    echo     if rp: >>"!tmp_icon_creator!"
    echo         strip = im.crop^(^(w-1, 0, w, h^)^).resize^(^(rp, h^), Image.NEAREST^) >>"!tmp_icon_creator!"
    echo         sq.paste^(strip, ^(lp + w, tp^)^) >>"!tmp_icon_creator!"
    echo     sq.paste^(im, ^(lp, tp^), im^) >>"!tmp_icon_creator!"
    echo     return sq >>"!tmp_icon_creator!"
    echo src = Image.open^('!sourceImage_python!'^).convert^('RGBA'^) >>"!tmp_icon_creator!"
    echo sq  = pad_to_square_edge_stretch^(src^) >>"!tmp_icon_creator!"
    echo sq.save^('!targetIcon_python!', sizes=[^(16,16^),^(20,20^),^(24,24^),^(32,32^),^(40,40^),^(48,48^),^(64,64^),^(128,128^),^(256,256^)]) >>"!tmp_icon_creator!"
    echo print^("Successfully created multi-size ICO file '!targetIcon_python!' the short way"^) >>"!tmp_icon_creator!"
goto :eof

:display_d3
echo In display_d3
    echo # tmp_icon_info_displayer.py ^(version that works with your Pillow^) >>"!tmp_icon_info_displayer!"
    echo import os, io, struct >>"!tmp_icon_info_displayer!"
    echo from PIL import Image >>"!tmp_icon_info_displayer!"
    echo ico_path = '!targetIcon_python!' >>"!tmp_icon_info_displayer!"
    echo def list_dir_entries^(fp^): >>"!tmp_icon_info_displayer!"
    echo     # ICONDIR >>"!tmp_icon_info_displayer!"
    echo     hdr = fp.read^(6^) >>"!tmp_icon_info_displayer!"
    echo     if not ^(len^(hdr^) == 6^): >>"!tmp_icon_info_displayer!"
    echo         raise ValueError^("Bad ICO header"^) >>"!tmp_icon_info_displayer!"
    echo     reserved, typ, count = struct.unpack^('^<HHH', hdr^) >>"!tmp_icon_info_displayer!"
    echo     if ^(not ^(reserved == 0^)^) or ^(not ^(typ == 1^)^): >>"!tmp_icon_info_displayer!"
    echo         raise ValueError^(f"Not an ICO ^(reserved={reserved}, type={typ}^)"^) >>"!tmp_icon_info_displayer!"
    echo     entries = [] >>"!tmp_icon_info_displayer!"
    echo     for _ in range^(count^): >>"!tmp_icon_info_displayer!"
    echo         b = fp.read^(16^) >>"!tmp_icon_info_displayer!"
    echo         ^(w,h,cc,_rsv,planes,bitcount,bytesinres,offset^) = struct.unpack^('^<BBBBHHLL', b^) >>"!tmp_icon_info_displayer!"
    echo         w = 256 if w == 0 else w >>"!tmp_icon_info_displayer!"
    echo         h = 256 if h == 0 else h >>"!tmp_icon_info_displayer!"
    echo         entries.append^({'w': w, 'h': h, 'planes': planes, 'bitcount': bitcount, >>"!tmp_icon_info_displayer!"
    echo                         'bytes': bytesinres, 'off': offset}^) >>"!tmp_icon_info_displayer!"
    echo     return entries >>"!tmp_icon_info_displayer!"
    echo def load_exact_with_pillow^(ico_file, w, h^): >>"!tmp_icon_info_displayer!"
    echo     # Legacy-supported trick: set .size before load^(^) >>"!tmp_icon_info_displayer!"
    echo     im = Image.open^(ico_file^) >>"!tmp_icon_info_displayer!"
    echo     im.size = ^(w, h^) >>"!tmp_icon_info_displayer!"
    echo     im.load^(^)                   # pulls that exact rendition if present >>"!tmp_icon_info_displayer!"
    echo     return im >>"!tmp_icon_info_displayer!"
    echo if not os.path.exists^(ico_path^): >>"!tmp_icon_info_displayer!"
    echo     print^("ICO file not found"^) >>"!tmp_icon_info_displayer!"
    echo else: >>"!tmp_icon_info_displayer!"
    echo     print^("File:", ico_path, "^(", os.path.getsize^(ico_path^), "bytes ^)"^) >>"!tmp_icon_info_displayer!"
    echo     with open^(ico_path, 'rb'^) as f: >>"!tmp_icon_info_displayer!"
    echo         entries = list_dir_entries^(f^) >>"!tmp_icon_info_displayer!"
    echo     print^("Embedded sizes ^(directory^):", [^(e['w'], e['h']^) for e in entries]^) >>"!tmp_icon_info_displayer!"
    echo     # Prove we can load each embedded rendition with Pillow >>"!tmp_icon_info_displayer!"
    echo     for e in entries: >>"!tmp_icon_info_displayer!"
    echo         w, h = e['w'], e['h'] >>"!tmp_icon_info_displayer!"
    echo         im = load_exact_with_pillow^(ico_path, w, h^) >>"!tmp_icon_info_displayer!"
    echo         print^(f"Loaded via Pillow size-hint {w}x{h}  - decoded: {im.size}, mode={im.mode}, format={im.format}"^) >>"!tmp_icon_info_displayer!"
goto :eof

:zip_top_folder_lister
REM p1 = name of the zip file
set "zipfile=%~dpnx1"
set "listzip=.\tmp_listzip.ps1"
del /f "%listzip%" >NUL 2>&1
>>"%listzip%" echo $zipPath = "!zipfile!"
>>"%listzip%" echo Write-Host "ZIP: $zipPath"
>>"%listzip%" echo Add-Type -AssemblyName System.IO.Compression.FileSystem
>>"%listzip%" echo $z = [System.IO.Compression.ZipFile]::OpenRead^($zipPath^)
>>"%listzip%" echo # Normalize path separators to forward slashes for consistent logic
>>"%listzip%" echo $entries = $z.Entries ^| ForEach-Object {
>>"%listzip%" echo   [pscustomobject]@{
>>"%listzip%" echo     Name = $_.FullName
>>"%listzip%" echo     Norm = ^($_.FullName -replace '\\','/'^)
>>"%listzip%" echo     Len  = $_.Length
>>"%listzip%" echo     Comp = $_.CompressedLength
>>"%listzip%" echo   }
>>"%listzip%" echo }
>>"%listzip%" echo # Files at ZIP root: no slash at all
>>"%listzip%" echo $rootFiles = $entries ^| Where-Object { $_.Norm -notmatch '/' }
>>"%listzip%" echo "{0,12} {1,12}  {2}" -f "Size","CompSize","Name"
>>"%listzip%" echo "{0,12} {1,12}  {2}" -f "----","--------","----"
>>"%listzip%" echo $rootFiles ^| ForEach-Object {
>>"%listzip%" echo "{0,12:N0} {1,12:N0}  {2}" -f $_.Len, $_.Comp, $_.Name
>>"%listzip%" echo }
>>"%listzip%" echo # List top-level directory names ^(no recursion^)
>>"%listzip%" echo # Top-level dir names: first segment of any entry that has a slash
>>"%listzip%" echo $rootDirs = $entries ^|
>>"%listzip%" echo   Where-Object { $_.Norm -match '/' } ^|
>>"%listzip%" echo   ForEach-Object { ($_.Norm -replace '/$','') -split '/' ^| Select-Object -First 1 } ^|
>>"%listzip%" echo   Sort-Object -Unique
>>"%listzip%" echo if ^($rootDirs^) {
>>"%listzip%" echo   Write-Host "Top-level directories:"
>>"%listzip%" echo   $rootDirs ^| ForEach-Object { Write-Host " - $_/" }
>>"%listzip%" echo }
>>"%listzip%" echo $z.Dispose^(^)
REM echo type "%listzip%"
REM type "%listzip%"
REM echo powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Sta -NonInteractive -File "%listzip%" 
powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Sta -NonInteractive -File "%listzip%" 
del /f "%listzip%" >NUL 2>&1
goto :eof
