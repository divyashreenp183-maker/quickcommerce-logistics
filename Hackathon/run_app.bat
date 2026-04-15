@echo off
echo Quick Commerce Logistics System - Local Server
echo ========================================
echo.
echo Checking for Python installation...

REM Try different Python commands
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo Found Python! Starting application...
    python app.py
    goto :end
)

py --version >nul 2>&1
if %errorlevel% == 0 (
    echo Found Python Launcher! Starting application...
    py app.py
    goto :end
)

python3 --version >nul 2>&1
if %errorlevel% == 0 (
    echo Found Python3! Starting application...
    python3 app.py
    goto :end
)

echo.
echo ERROR: Python not found!
echo.
echo Please install Python from https://www.python.org/downloads/
echo Or use one of the alternatives in LOCAL_SETUP.md
echo.
pause

:end
echo.
echo Server stopped.
