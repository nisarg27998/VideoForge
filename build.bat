@echo off
echo ========================================
echo VideoForge Build Script
echo ========================================

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo 1. Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo.
echo 2. Installing dependencies...
pip install -r requirements.txt

echo.
echo 3. Creating directory structure...
if not exist "assets" mkdir assets
if not exist "core" mkdir core
if not exist "ui" mkdir ui  
if not exist "utils" mkdir utils

echo.
echo 4. Creating __init__.py files...
echo. > core\__init__.py
echo. > ui\__init__.py
echo. > utils\__init__.py

echo.
echo 5. Creating application icon...
python -c "from utils.icon_generator import create_icon; create_icon('assets/logo.ico')"

echo.
echo 6. Building executable...
pyinstaller build.spec

echo.
echo 7. Testing executable...
if exist "dist\VideoForge.exe" (
    echo SUCCESS: VideoForge.exe created successfully!
    echo.
    echo File details:
    dir "dist\VideoForge.exe"
    echo.
    echo Location: %CD%\dist\VideoForge.exe
    echo.
    echo Would you like to run the application now? (y/n)
    set /p choice=
    if /i "%choice%"=="y" (
        echo Launching VideoForge...
        start "" "dist\VideoForge.exe"
    )
) else (
    echo ERROR: Build failed! VideoForge.exe not found.
    echo Check the console output above for errors.
)

echo.
echo 8. Cleaning up...
if exist "__pycache__" rmdir /s /q __pycache__
if exist "core\__pycache__" rmdir /s /q core\__pycache__
if exist "ui\__pycache__" rmdir /s /q ui\__pycache__
if exist "utils\__pycache__" rmdir /s /q utils\__pycache__

echo.
echo Build process complete!
echo.
pause