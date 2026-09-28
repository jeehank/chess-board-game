@echo off
setlocal
title "Chess Game"

cd /d "%~dp0"

:: 1. Prefer modern BlueJ bundled JDK if available
if exist "C:\Program Files\BlueJ\jdk\bin\javaw.exe" (
    start "" "C:\Program Files\BlueJ\jdk\bin\javaw.exe" -jar "%~dp0Chess.jar"
    exit /b 0
)

:: 2. Check if javaw is in PATH (runs smoothly in background)
where javaw >nul 2>&1
if %errorlevel% equ 0 (
    start "" javaw -jar "%~dp0Chess.jar"
    exit /b 0
)

:: 3. Check if java is in PATH
where java >nul 2>&1
if %errorlevel% equ 0 (
    start "" java -jar "%~dp0Chess.jar"
    exit /b 0
)

:: 4. Java runtime not found
echo.
echo ========================================================
echo   Java runtime was not found on your computer!
echo   Please run Install-Chess-Windows.bat to set up
echo   everything automatically with one click.
echo ========================================================
echo.
pause
endlocal
