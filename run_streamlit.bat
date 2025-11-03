@echo off
REM OmniLoader Streamlit UI Startup Script for Windows
echo Starting OmniLoader UI...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install/upgrade dependencies
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo WARNING: Some dependencies may have failed to install
    echo Continuing anyway...
)

REM Check if backend is running
echo Checking if backend is running...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Backend API is not running!
    echo Please start the backend first by running run_backend.bat
    echo.
    pause
)

REM Start Streamlit UI
echo.
echo ========================================
echo OmniLoader UI Starting
echo URL: http://localhost:8501
echo ========================================
echo.
echo Press Ctrl+C to stop the UI
echo.

streamlit run ui/app.py --server.port 8501 --server.address 0.0.0.0

pause
