@echo off
echo Compiling Chess.java...
"C:\Program Files\BlueJ\jdk\bin\javac.exe" --release 8 -d . Chess.java
if %errorlevel% equ 0 (
    echo Compilation successful! Starting game...
    java Chess
) else (
    echo Compilation failed.
    pause
)
