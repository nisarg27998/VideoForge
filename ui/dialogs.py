"""
Dialog Components for VideoForge
Custom dialogs for FFmpeg installation and other interactions
"""

from PyQt5.QtWidgets import (
    QMessageBox, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QDialog, QLabel, QProgressBar, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class FFmpegInstallDialog(QMessageBox):
    """Custom dialog for FFmpeg installation"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("FFmpeg Required")
        self.setIcon(QMessageBox.Warning)
        self.setText("FFmpeg Not Found")
        self.setInformativeText(
            "VideoForge requires FFmpeg to function properly.\n\n"
            "FFmpeg is not installed or not found in your system PATH.\n"
            "Would you like to install it automatically using Windows Package Manager?"
        )
        
        # Custom buttons
        self.install_btn = self.addButton("Install FFmpeg", QMessageBox.YesRole)
        self.manual_btn = self.addButton("Manual Install", QMessageBox.NoRole)
        self.exit_btn = self.addButton("Exit Application", QMessageBox.RejectRole)
        
        self.setDefaultButton(self.install_btn)
        
        # Style the dialog
        self.setStyleSheet("""
            QMessageBox {
                background-color: #2b2b2b;
                color: #ffffff;
                min-width: 400px;
            }
            QMessageBox QPushButton {
                background-color: #404040;
                border: 1px solid #555;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
                color: #ffffff;
            }
            QMessageBox QPushButton:hover {
                background-color: #505050;
            }
            QMessageBox QPushButton:default {
                background-color: #00A8E8;
                color: white;
                font-weight: bold;
            }
        """)


class ProgressDialog(QDialog):
    """Custom progress dialog with cancel functionality"""
    cancelled = pyqtSignal()
    
    def __init__(self, title: str, message: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(500, 300)
        
        layout = QVBoxLayout(self)
        
        # Title label
        title_label = QLabel(message)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Progress text area
        self.progress_text = QTextEdit()
        self.progress_text.setReadOnly(True)
        self.progress_text.setFont(QFont("Consolas", 9))
        layout.addWidget(self.progress_text)
        
        # Cancel button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.on_cancel)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.apply_dark_style()
    
    def append_text(self, text: str):
        """Append text to the progress display"""
        self.progress_text.append(text.rstrip())
        # Auto-scroll to bottom
        scrollbar = self.progress_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def on_cancel(self):
        """Handle cancel button click"""
        self.cancelled.emit()
        self.close()
    
    def apply_dark_style(self):
        """Apply dark theme to dialog"""
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #555;
                border-radius: 3px;
                color: #ffffff;
            }
            QPushButton {
                background-color: #404040;
                border: 1px solid #555;
                padding: 8px 16px;
                border-radius: 4px;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)


class AboutDialog(QDialog):
    """About dialog for the application"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About VideoForge")
        self.setModal(True)
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("VideoForge")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #00A8E8; margin: 20px;")
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Professional FFmpeg Frontend")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 14px; color: #888; margin-bottom: 20px;")
        layout.addWidget(subtitle)
        
        # Version info
        version_info = QLabel(
            "Version 1.0\n\n"
            "A modern, user-friendly interface for FFmpeg\n"
            "video and audio processing.\n\n"
            "Features:\n"
            "• Convert between video/audio formats\n"
            "• Compress and optimize videos\n"
            "• Trim and merge video files\n"
            "• Drag & drop support\n"
            "• Batch processing\n"
            "• Custom FFmpeg commands"
        )
        version_info.setAlignment(Qt.AlignCenter)
        version_info.setWordWrap(True)
        layout.addWidget(version_info)
        
        layout.addStretch()
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        self.apply_dark_style()
    
    def apply_dark_style(self):
        """Apply dark theme to dialog"""
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #00A8E8;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                color: white;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #007BB8;
            }
        """)


class ManualInstallDialog(QMessageBox):
    """Dialog showing manual FFmpeg installation instructions"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manual FFmpeg Installation")
        self.setIcon(QMessageBox.Information)
        self.setText("Manual FFmpeg Installation Required")
        self.setInformativeText(
            "To install FFmpeg manually:\n\n"
            "Method 1 - Official Download:\n"
            "1. Go to https://ffmpeg.org/download.html\n"
            "2. Download FFmpeg for Windows\n"
            "3. Extract to a folder (e.g., C:\\ffmpeg)\n"
            "4. Add the 'bin' folder to your system PATH\n"
            "5. Restart VideoForge\n\n"
            "Method 2 - Package Managers:\n"
            "• Chocolatey: choco install ffmpeg\n"
            "• Scoop: scoop install ffmpeg\n\n"
            "Method 3 - Portable:\n"
            "• Download portable version\n"
            "• Place ffmpeg.exe in VideoForge folder"
        )
        
        # Custom buttons
        self.retry_btn = self.addButton("Check Again", QMessageBox.YesRole)
        self.exit_btn = self.addButton("Exit Application", QMessageBox.RejectRole)
        
        self.setDefaultButton(self.retry_btn)
        
        # Style the dialog
        self.setStyleSheet("""
            QMessageBox {
                background-color: #2b2b2b;
                color: #ffffff;
                min-width: 500px;
            }
            QMessageBox QPushButton {
                background-color: #404040;
                border: 1px solid #555;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
                color: #ffffff;
            }
            QMessageBox QPushButton:hover {
                background-color: #505050;
            }
            QMessageBox QPushButton:default {
                background-color: #00A8E8;
                color: white;
                font-weight: bold;
            }
        """)


class ConfirmDialog(QMessageBox):
    """Custom confirmation dialog"""
    def __init__(self, title: str, message: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setIcon(QMessageBox.Question)
        self.setText(title)
        self.setInformativeText(message)
        
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        self.setDefaultButton(QMessageBox.Yes)
        
        # Apply dark theme
        self.setStyleSheet("""
            QMessageBox {
                background-color: #2b2b2b;
                color: #ffffff;
                min-width: 300px;
            }
            QMessageBox QPushButton {
                background-color: #404040;
                border: 1px solid #555;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 80px;
                color: #ffffff;
            }
            QMessageBox QPushButton:hover {
                background-color: #505050;
            }
        """)