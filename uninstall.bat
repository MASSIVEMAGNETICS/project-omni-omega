@echo off
REM =====================================================================
REM OmniLoader Studio - Uninstaller for Windows
REM =====================================================================
setlocal enabledelayedexpansion

title OmniLoader Studio - Uninstaller

echo.
echo  ========================================================
echo   OmniLoader Studio - Uninstaller
echo  ========================================================
echo.

set /p CONFIRM="Are you sure you want to uninstall OmniLoader Studio? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo.
    echo Uninstall cancelled.
    pause
    exit /b 0
)

echo.
echo Starting uninstallation...
echo.

REM Stop any running processes
echo [1/4] Stopping services...
taskkill /fi "WINDOWTITLE eq OmniLoader Backend*" /f >nul 2>&1
taskkill /fi "WINDOWTITLE eq OmniLoader Studio*" /f >nul 2>&1
echo    Services stopped
echo.

REM Remove shortcuts
echo [2/4] Removing shortcuts...
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\OmniLoader Studio.lnk"
if exist "%SHORTCUT%" (
    del "%SHORTCUT%"
    echo    Desktop shortcut removed
)

set "STARTMENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs\OmniLoader Studio"
if exist "%STARTMENU%" (
    rmdir /s /q "%STARTMENU%"
    echo    Start Menu shortcuts removed
)
echo.

REM Remove virtual environment
echo [3/4] Removing virtual environment...
if exist "venv\" (
    rmdir /s /q venv
    echo    Virtual environment removed
)
echo.

REM Clean Python cache
echo [4/4] Cleaning cache files...
for /r %%i in (__pycache__) do @if exist "%%i" rmdir /s /q "%%i"
del /s /q *.pyc >nul 2>&1
echo    Cache files cleaned
echo.

echo  ========================================================
echo  Uninstallation Complete!
echo  ========================================================
echo.
echo  OmniLoader Studio has been removed from your system.
echo.
echo  Note: Your project files, models, and data remain intact.
echo  To completely remove the application, delete this folder.
echo.
pause
