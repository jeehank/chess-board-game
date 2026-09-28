import base64

with open('Chess.jar', 'rb') as f:
    jar_data = f.read()

b64 = base64.b64encode(jar_data).decode('ascii')
lines = [b64[i:i+76] for i in range(0, len(b64), 76)]
payload = '\n'.join(lines)

bat_template = '''@echo off
setlocal enabledelayedexpansion
title "Chess Game - Installer & Launcher"

echo ========================================================
echo             CHESS GAME - ONE-CLICK INSTALLER
echo ========================================================
echo.
echo [*] Setting up Chess Game on your computer...

set "APP_DIR=%LOCALAPPDATA%\\ChessApp"
if not exist "%APP_DIR%" mkdir "%APP_DIR%"

:: 1. Extract embedded Chess.jar
echo [*] Extracting game files...
set "PAYLOAD_B64=%TEMP%\\chess_payload.b64"
set "TARGET_JAR=%APP_DIR%\\Chess.jar"

powershell -NoProfile -ExecutionPolicy Bypass -Command "$c=[System.IO.File]::ReadAllText('%~f0'); $s=$c.IndexOf('-----BEGIN CERTIFICATE-----'); $e=$c.IndexOf('-----END CERTIFICATE-----')+25; if($s -ge 0 -and $e -gt $s){ [System.IO.File]::WriteAllText($env:PAYLOAD_B64, $c.Substring($s, $e-$s)); }"

if exist "%PAYLOAD_B64%" (
    certutil -decode "%PAYLOAD_B64%" "%TARGET_JAR%" >nul 2>&1
    del "%PAYLOAD_B64%" >nul 2>&1
)

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
echo [!] Java runtime was not found on your system.
echo [*] Automatically downloading portable OpenJDK JRE (Adoptium Temurin 21)...
echo     (No administrator rights needed, this is only done once)
echo.

set "JRE_ZIP=%TEMP%\\temurin_jre.zip"
set "JRE_DIR=%APP_DIR%\\jre"
if not exist "%JRE_DIR%" mkdir "%JRE_DIR%"

powershell -NoProfile -ExecutionPolicy Bypass -Command "Write-Host 'Downloading portable Java runtime... Please wait.' -ForegroundColor Cyan; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $url = 'https://api.adoptium.net/v3/binary/latest/21/ga/windows/x64/jre/hotspot/normal/eclipse'; Invoke-WebRequest -Uri $url -OutFile $env:JRE_ZIP -UseBasicParsing; Write-Host 'Extracting Java runtime...' -ForegroundColor Cyan; Expand-Archive -Path $env:JRE_ZIP -DestinationPath $env:JRE_DIR -Force; Remove-Item $env:JRE_ZIP -Force -ErrorAction SilentlyContinue;"

for /r "%JRE_DIR%" %%F in (javaw.exe) do (
    if exist "%%F" (
        set "JAVA_BIN=%%F"
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

:: 4. Create Launch script
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
__PAYLOAD__
-----END CERTIFICATE-----
'''

bat_content = bat_template.replace('__PAYLOAD__', payload)

with open('Install-Chess-Windows.bat', 'w', encoding='utf-8') as f:
    f.write(bat_content)

print('Install-Chess-Windows.bat created successfully!')
