@echo off
setlocal
title "Chess Compiler & Packager"

cd /d "%~dp0"
echo ========================================================
echo               Compiling Chess Application
echo ========================================================
echo.

set "JAVAC_CMD="
set "JAR_CMD="

if exist "C:\Program Files\BlueJ\jdk\bin\javac.exe" (
    set "JAVAC_CMD=C:\Program Files\BlueJ\jdk\bin\javac.exe"
    set "JAR_CMD=C:\Program Files\BlueJ\jdk\bin\jar.exe"
    goto :found_javac
)

if defined JAVA_HOME (
    if exist "%JAVA_HOME%\bin\javac.exe" (
        set "JAVAC_CMD=%JAVA_HOME%\bin\javac.exe"
        set "JAR_CMD=%JAVA_HOME%\bin\jar.exe"
        goto :found_javac
    )
)

where javac >nul 2>&1
if %errorlevel% equ 0 (
    set "JAVAC_CMD=javac"
    set "JAR_CMD=jar"
    goto :found_javac
)

:no_javac
echo [ERROR] No Java compiler (javac) found on your system!
echo Please install a JDK or install BlueJ.
pause
exit /b 1

:found_javac
echo [1/3] Compiling Chess.java with Java 8 compatibility...
"%JAVAC_CMD%" --release 8 -d . Chess.java
if %errorlevel% neq 0 (
    echo [WARNING] Retrying standard compilation without release flag...
    "%JAVAC_CMD%" -d . Chess.java
    if %errorlevel% neq 0 (
        echo [ERROR] Compilation failed!
        pause
        exit /b 1
    )
)

echo [2/3] Building standalone executable Chess.jar...
if not "%JAR_CMD%"=="" (
    "%JAR_CMD%" cfe Chess.jar Chess *.class pieces
    echo [SUCCESS] Chess.jar packaged successfully!
)

echo [3/3] Ready!
echo.
echo Compilation completed successfully.
endlocal
