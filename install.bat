@echo off
REM =====================================================================
REM OmniLoader Studio - One-Click Installer for Windows
REM Production-grade local-first AI model manager
REM =====================================================================
setlocal enabledelayedexpansion

title OmniLoader Studio - Installer

REM Colors and ASCII Art
echo.
echo  ========================================================
echo   ___  __  __ _   _ ___ _     ___    _    ____  _____ ____  
echo  / _ \|  \/  ^| \ ^| ^|_ _^| ^|   / _ \  / \  ^|  _ \^| ____^|  _ \ 
echo ^| ^| ^| ^| ^|\/^| ^|  \^| ^|^|^| ^|^|  ^| ^| ^| ^|/ _ \ ^| ^| ^| ^|  _^| ^| ^|_) ^|
echo ^| ^|_^| ^| ^|  ^| ^| ^|\  ^|^|^| ^|^| ^|__^| ^|_^| / ___ \^| ^|_^| ^| ^|___^|  _ ^< 
echo  \___/^|_^|  ^|_^|_^| \_^|___^|_____\___/_/   \_\____/^|_____^|_^| \_\
echo.
echo  ONE-CLICK INSTALLER
echo  ========================================================
echo.

REM Get installation directory
set "INSTALL_DIR=%~dp0"
cd /d "%INSTALL_DIR%"

echo [1/6] Checking system requirements...
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    echo After installing Python, run this installer again.
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo    Python %PYVER% found
echo.

REM Check pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not installed
    echo.
    echo Please ensure pip is installed with Python.
    echo.
    pause
    exit /b 1
)
echo    pip is available
echo.

echo [2/6] Creating virtual environment...
if not exist "venv\" (
    echo    Creating new virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo    Virtual environment created successfully
) else (
    echo    Virtual environment already exists
)
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo [3/6] Installing dependencies...
echo    This may take 5-15 minutes depending on your internet connection...
echo.
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if errorlevel 1 (
    echo WARNING: Some dependencies may have failed to install
    echo The installation will continue, but some features may not work.
    echo.
) else (
    echo    All dependencies installed successfully
)
echo.

echo [4/6] Validating installation...
python validate_install.py
if errorlevel 1 (
    echo.
    echo WARNING: Installation validation failed
    echo Some features may not work correctly.
    echo.
    pause
)
echo.

echo [5/6] Creating shortcuts...
echo.

REM Create shortcut on Desktop
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\OmniLoader Studio.lnk"

REM Use PowerShell to create shortcut
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = '%INSTALL_DIR%OmniLoader.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.IconLocation = 'imageres.dll,14'; $Shortcut.Description = 'OmniLoader Studio - Production-grade local-first AI model manager'; $Shortcut.Save()"

if exist "%SHORTCUT%" (
    echo    Desktop shortcut created: %SHORTCUT%
) else (
    echo    WARNING: Could not create desktop shortcut
)

REM Create Start Menu shortcut
set "STARTMENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"
if not exist "%STARTMENU%\OmniLoader Studio\" mkdir "%STARTMENU%\OmniLoader Studio"
set "STARTSHORTCUT=%STARTMENU%\OmniLoader Studio\OmniLoader Studio.lnk"

powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTSHORTCUT%'); $Shortcut.TargetPath = '%INSTALL_DIR%OmniLoader.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.IconLocation = 'imageres.dll,14'; $Shortcut.Description = 'OmniLoader Studio - Production-grade local-first AI model manager'; $Shortcut.Save()"

if exist "%STARTSHORTCUT%" (
    echo    Start Menu shortcut created: %STARTSHORTCUT%
) else (
    echo    WARNING: Could not create Start Menu shortcut
)

REM Create Uninstall shortcut in Start Menu
set "UNINSTALLSHORTCUT=%STARTMENU%\OmniLoader Studio\Uninstall OmniLoader.lnk"
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%UNINSTALLSHORTCUT%'); $Shortcut.TargetPath = '%INSTALL_DIR%uninstall.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.IconLocation = 'imageres.dll,84'; $Shortcut.Description = 'Uninstall OmniLoader Studio'; $Shortcut.Save()"

echo.

echo [6/6] Finalizing installation...
echo.

REM Create quick launch script in installation directory
echo @echo off > "%INSTALL_DIR%Quick-Launch.bat"
echo cd /d "%%~dp0" >> "%INSTALL_DIR%Quick-Launch.bat"
echo call OmniLoader.bat >> "%INSTALL_DIR%Quick-Launch.bat"

echo.
echo  ========================================================
echo  INSTALLATION COMPLETE!
echo  ========================================================
echo.
echo  OmniLoader Studio has been installed successfully!
echo.
echo  Shortcuts created:
echo    - Desktop: OmniLoader Studio
echo    - Start Menu: OmniLoader Studio
echo.
echo  To launch OmniLoader Studio:
echo    1. Double-click the "OmniLoader Studio" shortcut on your desktop
echo    2. OR search for "OmniLoader Studio" in Start Menu
echo    3. OR run OmniLoader.bat in this directory
echo.
echo  Access URLs after launch:
echo    - Studio UI: http://localhost:8501
echo    - API Docs: http://localhost:8000/docs
echo.
echo  Documentation:
echo    - README.md - Complete feature documentation
echo    - SETUP.md - Detailed setup guide
echo.
echo  To uninstall:
echo    - Run uninstall.bat or use Start Menu shortcut
echo.
echo  ========================================================
echo.

REM Ask if user wants to launch now
set /p LAUNCH="Do you want to launch OmniLoader Studio now? (y/n): "
if /i "%LAUNCH%"=="y" (
    echo.
    echo Launching OmniLoader Studio...
    start "" "%INSTALL_DIR%OmniLoader.bat"
    exit /b 0
)

echo.
echo Installation complete. You can launch OmniLoader Studio anytime using the desktop shortcut.
echo.
pause
