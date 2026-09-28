import base64

with open('Chess.jar', 'rb') as f:
    jar_data = f.read()

b64 = base64.b64encode(jar_data).decode('ascii')
lines = [b64[i:i+76] for i in range(0, len(b64), 76)]
payload = '\r\n'.join(lines)

bat_code = '''@echo off
setlocal enabledelayedexpansion
title "Chess Game - Installer & Launcher"

echo ========================================================
echo             CHESS GAME - ONE-CLICK INSTALLER
echo ========================================================
echo.
echo [*] Setting up Chess Game on your computer...

set "APP_DIR=%LOCALAPPDATA%\\ChessApp"
if not exist "%APP_DIR%" mkdir "%APP_DIR%"

:: 1. Extract embedded Chess.jar directly from this file
echo [*] Unpacking game files...
set "TARGET_JAR=%APP_DIR%\\Chess.jar"
certutil -decode "%~f0" "%TARGET_JAR%" >nul 2>&1

if not exist "%TARGET_JAR%" (
    echo [ERROR] Failed to unpack game files.
    pause
    exit /b 1
)

:: 2. Check for an existing working Java runtime
set "JAVA_BIN="

if exist "%APP_DIR%\\jre\\bin\\javaw.exe" (
    set "JAVA_BIN=%APP_DIR%\\jre\\bin\\javaw.exe"
    goto :java_ready
)
for /d %%D in ("%APP_DIR%\\jre\\*") do (
    if exist "%%~D\\bin\\javaw.exe" (
        set "JAVA_BIN=%%~D\\bin\\javaw.exe"
        goto :java_ready
    )
)

if exist "C:\\Program Files\\BlueJ\\jdk\\bin\\javaw.exe" (
    set "JAVA_BIN=C:\\Program Files\\BlueJ\\jdk\\bin\\javaw.exe"
    goto :java_ready
)

if defined JAVA_HOME (
    if exist "%JAVA_HOME%\\bin\\javaw.exe" (
        set "JAVA_BIN=%JAVA_HOME%\\bin\\javaw.exe"
        goto :java_ready
    )
)

where javaw >nul 2>&1
if %errorlevel% equ 0 (
    set "JAVA_BIN=javaw"
    goto :java_ready
)

where java >nul 2>&1
if %errorlevel% equ 0 (
    set "JAVA_BIN=java"
    goto :java_ready
)

:: 3. Java not found -> Download lightweight portable OpenJDK JRE
echo.
echo [!] Java runtime was not found on your computer.
echo [*] Automatically downloading portable OpenJDK JRE (Adoptium Temurin 21)...
echo     (No administrator privileges needed, this is only downloaded once)
echo.

set "JRE_ZIP=%TEMP%\\temurin_jre.zip"
set "JRE_DIR=%APP_DIR%\\jre"
if not exist "%JRE_DIR%" mkdir "%JRE_DIR%"

powershell -NoProfile -ExecutionPolicy Bypass -Command "Write-Host 'Downloading portable Java runtime... Please wait.' -ForegroundColor Cyan; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $url = 'https://api.adoptium.net/v3/binary/latest/21/ga/windows/x64/jre/hotspot/normal/eclipse'; Invoke-WebRequest -Uri $url -OutFile $env:JRE_ZIP -UseBasicParsing; Write-Host 'Extracting Java runtime...' -ForegroundColor Cyan; Expand-Archive -Path $env:JRE_ZIP -DestinationPath $env:JRE_DIR -Force; Remove-Item $env:JRE_ZIP -Force -ErrorAction SilentlyContinue;"

if exist "%APP_DIR%\\jre\\bin\\javaw.exe" (
    set "JAVA_BIN=%APP_DIR%\\jre\\bin\\javaw.exe"
    goto :java_ready
)
for /d %%D in ("%APP_DIR%\\jre\\*") do (
    if exist "%%~D\\bin\\javaw.exe" (
        set "JAVA_BIN=%%~D\\bin\\javaw.exe"
        goto :java_ready
    )
)

if "%JAVA_BIN%"=="" (
    echo [ERROR] Could not set up Java runtime automatically.
    echo Please make sure you have an active internet connection.
    pause
    exit /b 1
)

:java_ready
echo [*] Java runtime detected: %JAVA_BIN%

:: 4. Create launcher script
echo [*] Setting up launcher script...
(
    echo @echo off
    echo start "" "%JAVA_BIN%" -jar "%TARGET_JAR%"
) > "%APP_DIR%\\Launch-Chess.bat"

:: 5. Create Desktop shortcut
echo [*] Creating Desktop shortcut...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$wsh = New-Object -ComObject WScript.Shell; $desktop = [Environment]::GetFolderPath('Desktop'); $shortcut = $wsh.CreateShortcut(\\"$desktop\\Chess Game.lnk\\"); $shortcut.TargetPath = '$env:APP_DIR\\Launch-Chess.bat'; $shortcut.WorkingDirectory = '$env:APP_DIR'; $shortcut.Description = 'Play Chess Game'; $shortcut.Save();"

echo.
echo ========================================================
echo             Installation Successful!
echo    A 'Chess Game' shortcut has been added to Desktop.
echo    Starting the game now...
echo ========================================================
echo.

start "" "%JAVA_BIN%" -jar "%TARGET_JAR%"

timeout /t 3 >nul
exit /b 0

-----BEGIN CERTIFICATE-----
''' + payload + '''
-----END CERTIFICATE-----
'''

with open('Install-Chess-Windows.bat', 'w', encoding='ascii') as f:
    f.write(bat_code)

print('Install-Chess-Windows.bat built successfully!')
