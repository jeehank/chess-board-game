@echo off
title "Chess AI Model Trainer & Deployer"
cd /d "%~dp0"
echo ========================================================
echo        STARTING CHESS AI MODEL TRAINER & DEPLOYER
echo ========================================================
echo.
python chess_trainer_gui.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Could not start trainer. Make sure Python and numpy are installed.
    echo Run: pip install numpy
    pause
)
