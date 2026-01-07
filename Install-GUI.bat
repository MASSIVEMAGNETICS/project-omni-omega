@echo off
REM =====================================================================
REM OmniLoader Studio - GUI Installer Launcher for Windows
REM Production-grade local-first AI model manager
REM =====================================================================

title OmniLoader Studio - GUI Installer

REM Check Python installation
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

REM Launch GUI Installer
python "%~dp0install_gui.py"

exit /b 0
