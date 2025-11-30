@echo off
REM =====================================================================
REM OmniLoader Studio - Unified Windows 10 Launcher
REM Production-grade local-first AI model manager
REM =====================================================================
setlocal enabledelayedexpansion

title OmniLoader Studio

REM Configuration
set "BACKEND_PORT=8000"
set "FRONTEND_PORT=8501"
set "VENV_DIR=venv"

REM Colors and ASCII Art (using PowerShell for colors)
echo.
echo  ========================================================
echo   ___  __  __ _   _ ___ _     ___    _    ____  _____ ____  
echo  / _ \|  \/  | \ | |_ _| |   / _ \  / \  |  _ \| ____|  _ \ 
echo | | | | |\/| |  \| || || |  | | | |/ _ \ | | | |  _| | |_) |
echo | |_| | |  | | |\  || || |__| |_| / ___ \| |_| | |___|  _ ^ 
echo  \___/|_|  |_|_| \_|___|_____\___/_/   \_\____/|_____|_| \_\
echo.
echo  Production-grade local-first AI model manager
echo  ========================================================
echo.

REM Check Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo    Python %PYVER% found

REM Check/Create Virtual Environment
echo.
echo [2/5] Setting up virtual environment...
if not exist "%VENV_DIR%\" (
    echo    Creating new virtual environment...
    python -m venv %VENV_DIR%
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo    Virtual environment created.
) else (
    echo    Using existing virtual environment.
)

REM Activate Virtual Environment
call %VENV_DIR%\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install Dependencies
echo.
echo [3/5] Checking dependencies...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo    Installing dependencies (this may take a few minutes)...
    pip install -q -r requirements.txt
    if errorlevel 1 (
        echo WARNING: Some dependencies may have failed to install
    )
) else (
    echo    Dependencies already installed.
)

REM Check for existing processes
echo.
echo [4/5] Checking for running instances...
netstat -ano 2>nul | findstr ":%BACKEND_PORT% " >nul
if not errorlevel 1 (
    echo    WARNING: Port %BACKEND_PORT% is already in use.
    echo    Another backend may be running.
    set /p CONTINUE="    Continue anyway? (y/n): "
    if /i not "!CONTINUE!"=="y" exit /b 0
)

REM Launch Services
echo.
echo [5/5] Launching OmniLoader Studio...
echo.
echo ========================================================
echo  Starting services:
echo    Backend API:  http://localhost:%BACKEND_PORT%
echo    API Docs:     http://localhost:%BACKEND_PORT%/docs
echo    Studio UI:    http://localhost:%FRONTEND_PORT%
echo ========================================================
echo.

REM Start backend in background
start "OmniLoader Backend" /min cmd /c "call %VENV_DIR%\Scripts\activate.bat && uvicorn app.main:app --host 0.0.0.0 --port %BACKEND_PORT%"

REM Wait for backend to start
echo Waiting for backend to start...
set /a WAIT=0
:wait_backend
timeout /t 1 /nobreak >nul
curl -s http://localhost:%BACKEND_PORT%/health >nul 2>&1
if errorlevel 1 (
    set /a WAIT+=1
    if !WAIT! lss 30 goto wait_backend
    echo WARNING: Backend may not have started correctly.
) else (
    echo Backend is ready!
)

REM Start frontend in new window
echo.
echo Starting Studio UI...
start "OmniLoader Studio" cmd /c "call %VENV_DIR%\Scripts\activate.bat && streamlit run ui/app.py --server.port %FRONTEND_PORT% --server.address 0.0.0.0 --server.headless true"

REM Wait and open browser
timeout /t 3 /nobreak >nul
echo.
echo Opening browser...
start http://localhost:%FRONTEND_PORT%

echo.
echo ========================================================
echo  OmniLoader Studio is running!
echo.
echo  To stop: Close this window and the terminal windows
echo           titled "OmniLoader Backend" and "OmniLoader Studio"
echo.
echo  Press any key to open the management menu...
echo ========================================================
pause >nul

:menu
cls
echo.
echo  OmniLoader Studio - Management Menu
echo  ====================================
echo.
echo  [1] Open Studio UI in browser
echo  [2] Open API Documentation
echo  [3] View Backend Status
echo  [4] Run Tests
echo  [5] View Logs
echo  [6] Stop All Services
echo  [7] Exit (keep services running)
echo.
set /p CHOICE="  Select option (1-7): "

if "%CHOICE%"=="1" (
    start http://localhost:%FRONTEND_PORT%
    goto menu
)
if "%CHOICE%"=="2" (
    start http://localhost:%BACKEND_PORT%/docs
    goto menu
)
if "%CHOICE%"=="3" (
    echo.
    echo Checking backend health...
    curl -s http://localhost:%BACKEND_PORT%/health
    echo.
    pause
    goto menu
)
if "%CHOICE%"=="4" (
    echo.
    echo Running tests...
    pytest tests/ -v
    pause
    goto menu
)
if "%CHOICE%"=="5" (
    echo.
    echo Logs are displayed in the respective terminal windows.
    echo - Backend: "OmniLoader Backend" window
    echo - Frontend: "OmniLoader Studio" window
    pause
    goto menu
)
if "%CHOICE%"=="6" (
    echo.
    echo Stopping services...
    taskkill /fi "WINDOWTITLE eq OmniLoader Backend*" /f >nul 2>&1
    taskkill /fi "WINDOWTITLE eq OmniLoader Studio*" /f >nul 2>&1
    echo Services stopped.
    pause
    exit /b 0
)
if "%CHOICE%"=="7" (
    echo.
    echo Exiting management menu. Services will continue running.
    exit /b 0
)
goto menu
