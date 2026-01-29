@echo off
echo ============================================
echo PDF Toolkit - Quick Setup
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

echo [1/4] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [4/4] Setting up project structure...
python setup_project.py

echo.
echo ============================================
echo Setup complete!
echo ============================================
echo.
echo To run the application:
echo   1. Open PowerShell in this folder
echo   2. Run: .\venv\Scripts\Activate
echo   3. Run: python src\main.py
echo.
echo Or simply run: run.bat
echo.
pause
