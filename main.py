#!/usr/bin/env python3
"""
VideoForge - FFmpeg GUI Frontend
Main entry point for the application
"""

import sys
import os
from pathlib import Path

# Add the project directory to the Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon

from ui.main_window import VideoForgeMainWindow
from utils.icon_generator import create_icon


def main():
    """Main application entry point"""
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("VideoForge")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("VideoForge")
    
    # Set application properties
    app.setQuitOnLastWindowClosed(True)
    
    # Create icon if it doesn't exist
    icon_path = project_dir / 'assets' / 'logo.ico'
    icon_path.parent.mkdir(exist_ok=True)
    
    if not icon_path.exists():
        try:
            create_icon(str(icon_path))
            print("Application icon created successfully!")
        except Exception as e:
            print(f"Could not create icon: {e}")
    
    # Set application icon
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # Create and show main window
    try:
        window = VideoForgeMainWindow()
        window.show()
        
        # Start the event loop
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"Error starting VideoForge: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()