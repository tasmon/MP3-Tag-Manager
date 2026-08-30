@echo off
title MP3 Tag Manager
cd /d "%~dp0"

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.10+ from https://www.python.org
    pause
    exit /b 1
)

echo Checking dependencies...
python -c "import mutagen, customtkinter, PIL" 2>nul
if %errorlevel% neq 0 (
    echo Installing required packages...
    pip install -r requirements.txt
)

echo Starting MP3 Tag Manager...
python mp3_tag_manager.py
if %errorlevel% neq 0 pause
