# VideoForge - Modular Project Structure

## 📁 Project Directory Structure

```
VideoForge/
├── main.py                     # Main entry point
├── requirements.txt            # Python dependencies
├── build.bat                   # Windows build script
├── build.spec                  # PyInstaller spec file
├── README.md                   # Project documentation
│
├── assets/                     # Application assets
│   └── logo.ico               # Application icon (auto-generated)
│
├── core/                       # Core application logic
│   ├── __init__.py
│   ├── ffmpeg_manager.py       # FFmpeg operations and threads
│   └── command_builder.py      # FFmpeg command construction
│
├── ui/                         # User interface components
│   ├── __init__.py
│   ├── main_window.py          # Main application window
│   ├── simple_mode.py          # Simple mode interface
│   ├── advanced_mode.py        # Advanced mode interface
│   ├── widgets.py              # Custom widgets
│   └── dialogs.py              # Dialog components
│
└── utils/                      # Utility modules
    ├── __init__.py
    ├── icon_generator.py       # Icon creation utility
    └── styles.py               # Application theming
```

## 📋 Additional Files Needed

Create these empty `__init__.py` files:

### core/__init__.py
```python
"""
VideoForge Core Module
Contains the main application logic and FFmpeg integration
"""
```

### ui/__init__.py
```python
"""
VideoForge UI Module
Contains all user interface components and widgets
"""
```

### utils/__init__.py
```python
"""
VideoForge Utilities Module
Contains utility functions and helper classes
"""
```

## 🔧 PyInstaller Spec File

### build.spec
```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/logo.ico', 'assets'),
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui', 
        'PyQt5.QtWidgets',
        'PIL.Image',
        'PIL.ImageDraw'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VideoForge',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    cofile_version_info=None,
    icon='assets/logo.ico'
)
```

## 🚀 Enhanced Build Script

### build.bat
```batch
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
```

## 📖 Setup Instructions

### 1. Create Project Structure
```bash
mkdir VideoForge
cd VideoForge

# Create subdirectories
mkdir assets core ui utils

# Create __init__.py files
echo. > core/__init__.py
echo. > ui/__init__.py  
echo. > utils/__init__.py
```

### 2. Copy Code Files
Save each code module to its respective file:
- `main.py` → Root directory
- `core/ffmpeg_manager.py` → FFmpeg operations
- `core/command_builder.py` → Command building
- `ui/main_window.py` → Main window
- `ui/simple_mode.py` → Simple interface
- `ui/advanced_mode.py` → Advanced interface  
- `ui/widgets.py` → Custom widgets
- `ui/dialogs.py` → Dialog components
- `utils/icon_generator.py` & `utils/styles.py` → Utilities

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Development Version
```bash
python main.py
```

### 5. Build Executable
```bash
# Using build script
build.bat

# Or manually
pyinstaller build.spec
```

## 🎯 Key Benefits of Modular Structure

### ✅ **Better Organization**
- Clear separation of concerns
- Easy to locate specific functionality
- Logical file grouping

### ✅ **Easier Debugging** 
- Isolated modules for targeted troubleshooting
- Clear error traces to specific files
- Independent testing of components

### ✅ **Maintainability**
- Update individual components without affecting others
- Add new features in dedicated modules
- Clean code architecture

### ✅ **Scalability**
- Easy to add new modes/features
- Modular widget system
- Extensible command building

### ✅ **Collaboration Ready**
- Multiple developers can work on different modules
- Clear interfaces between components
- Version control friendly

## 🐛 Debugging Guide

### Common Issues & Solutions

1. **Import Errors**
   - Ensure all `__init__.py` files exist
   - Check Python path includes project root
   - Verify module names match file names

2. **PyQt5 Issues**
   - Install: `pip install PyQt5`
   - Check version compatibility
   - Ensure proper signal/slot connections

3. **Build Failures**
   - Check `build.spec` paths are correct
   - Verify all dependencies in requirements.txt
   - Ensure icon file exists before building

4. **Runtime Errors**
   - Check FF