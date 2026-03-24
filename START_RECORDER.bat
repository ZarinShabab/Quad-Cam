@echo off
title QUADCAM Recorder - Server
color 0A

echo.
echo  ======================================================
echo    QUADCAM RECORDER  -  Starting Local Server...
echo  ======================================================
echo.
echo  IMPORTANT:
echo    - Keep this window open while recording
echo    - Click ALLOW when browser asks for camera access
echo    - Connect all USB cameras BEFORE launching
echo    - Videos are saved to:  Recordings\Recording_DATE_TIME\
echo    - Press Ctrl+C in this window to stop the server
echo.
echo  ======================================================
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo  ERROR: Python not found on this computer.
    echo  Download from: https://www.python.org/downloads/
    echo  During install, check "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

python start_recorder.py
echo.
pause
