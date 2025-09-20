@echo off
@setlocal ENABLEDELAYEDEXPANSION
@setlocal enableextensions

REM test Stay_Awake

goto :AAA

echo.
echo !TIME!
echo python Stay_Awake.py
python Stay_Awake.py
set "EL=!ERRORLEVEL!"
echo !TIME!

pause

REM 4.1. **Too soon / too far:**
REM # expect min bound error (10s)
echo python .\Stay_Awake.py --for 5s
python .\Stay_Awake.py --for 5s

pause

echo.
echo !TIME!
echo python Stay_Awake.py --for 45s
python Stay_Awake.py --for 45s

pause

REM 2. **`--for` typical:**
REM    * Console: `--for: will auto-quit after 75 seconds (00:01:15).`
REM    * Countdown should tick with your cadence bands and quit \~75s later.
echo python .\Stay_Awake.py --for 75s
python .\Stay_Awake.py --for 75s

pause

:AAA


echo TEST past datetime
echo !TIME!
set "UNTIL_STRING=2025-09-20 05:20:37"
echo python ".\Stay_Awake.py" --until "!UNTIL_STRING!"
python ".\Stay_Awake.py" --until "!UNTIL_STRING!"

pause

echo TEST 3. **`--until` in \~1 minute:**
REM  * Console: `--until: will auto-quit at <local time> (00:01:xx from now).`
REM  * Countdown shows the ETA and remaining time; quits at that wall-clock instant.
set "P_MINS=1"
for /f "usebackq delims=" %%T in (`powershell -NoProfile -Command "(Get-Date).AddMinutes(!P_MINS!).ToString('yyyy-MM-dd HH:mm:ss')"`) do (
set "UNTIL_STRING=%%T"
)
echo !TIME!
echo python ".\Stay_Awake.py" --until "!UNTIL_STRING!"
python ".\Stay_Awake.py" --until "!UNTIL_STRING!"

pause

echo TEST 3. **`--until` in \~2 minutes:**
REM  * Console: `--until: will auto-quit at <local time> (00:01:xx from now).`
REM  * Countdown shows the ETA and remaining time; quits at that wall-clock instant.
set "P_MINS=2"
for /f "usebackq delims=" %%T in (`powershell -NoProfile -Command "(Get-Date).AddMinutes(!P_MINS!).ToString('yyyy-MM-dd HH:mm:ss')"`) do (
set "UNTIL_STRING=%%T"
)
echo !TIME!
echo python ".\Stay_Awake.py" --until "!UNTIL_STRING!"
python ".\Stay_Awake.py" --until "!UNTIL_STRING!"

pause

echo TEST 4.2. **Too soon / too far:**
REM # expect max bound error
echo !TIME!
echo python .\Stay_Awake.py --until "2099-01-01 00:00:00"  
python .\Stay_Awake.py --until "2099-01-01 00:00:00"  

pause

REM 5. **Invalid calendar / format:**

echo TEST 5.1 invalid date
echo !TIME!
echo python .\Stay_Awake.py --until "2025-02-31 10:00:00"
python .\Stay_Awake.py --until "2025-02-31 10:00:00"

pause

echo TEST 5.2 missing seconds
echo !TIME!
echo python .\Stay_Awake.py --until "2025-1-2 3:2"            
python .\Stay_Awake.py --until "2025-1-2 3:2"            

pause

echo TEST 7. **Final re-ceil check:**
REM Run with small values (e.g., `--for 11s`) and watch the first countdown value. 
REM It should align tightly to whole seconds without starting at e.g. `00:00:10`.
echo !TIME!
echo python .\Stay_Awake.py --for 01s
python .\Stay_Awake.py --for 09s

pause
exit
