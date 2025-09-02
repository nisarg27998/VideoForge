"""
Custom Widgets for VideoForge
Drag & drop components and specialized UI elements
"""

import os
from pathlib import Path
from typing import List

from PyQt5.QtWidgets import (
    QLineEdit, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QFrame, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QFont


class DragDropLineEdit(QLineEdit):
    """QLineEdit with enhanced drag and drop support"""
    file_dropped = pyqtSignal(str)
    
    def __init__(self, parent=None, accept_folders=False, placeholder_text=""):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.accept_folders = accept_folders
        
        if placeholder_text:
            self.setPlaceholderText(placeholder_text)
        elif accept_folders:
            self.setPlaceholderText("Drag folder here or click Browse...")
        else:
            self.setPlaceholderText("Drag files here or click Browse...")
        
        self.apply_default_style()
    
    def apply_default_style(self):
        """Apply default drag-drop styling"""
        self.setStyleSheet("""
            QLineEdit {
                border: 2px dashed #555;
                padding: 8px;
                border-radius: 4px;
                background-color: #404040;
                color: #ffffff;
            }
            QLineEdit:focus {
                border-color: #00A8E8;
                border-style: solid;
            }
        """)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                if self.accept_folders:
                    if os.path.isdir(file_path) or os.path.isfile(file_path):
                        event.accept()
                        self.setStyleSheet("""
                            QLineEdit {
                                border: 2px dashed #00A8E8;
                                background-color: #505050;
                                padding: 8px;
                                border-radius: 4px;
                                color: #ffffff;
                            }
                        """)
                    else:
                        event.ignore()
                else:
                    if os.path.isfile(file_path):
                        event.accept()
                        self.setStyleSheet("""
                            QLineEdit {
                                border: 2px dashed #00A8E8;
                                background-color: #505050;
                                padding: 8px;
                                border-radius: 4px;
                                color: #ffffff;
                            }
                        """)
                    else:
                        event.ignore()
        else:
            event.ignore()
    
    def dragLeaveEvent(self, event):
        self.apply_default_style()
    
    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.setText(file_path)
            self.file_dropped.emit(file_path)
        
        # Reset style
        self.apply_default_style()


class DragDropWidget(QWidget):
    """Main drag and drop overlay for the entire application"""
    files_dropped = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        
        # Create overlay for drag feedback
        self.drag_overlay = QLabel(self)
        self.drag_overlay.setText(
            "📁 Drop media files here\n\n"
            "Supported formats:\n"
            "Videos: MP4, MKV, AVI, MOV, WebM, FLV\n"
            "Audio: MP3, AAC, WAV, FLAC, M4A, OGG"
        )
        self.drag_overlay.setAlignment(Qt.AlignCenter)
        self.drag_overlay.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 168, 232, 0.95);
                color: white;
                font-size: 18px;
                font-weight: bold;
                border: 3px dashed white;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        self.drag_overlay.hide()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Center the overlay
        overlay_size = self.drag_overlay.sizeHint()
        x = (self.width() - overlay_size.width()) // 2
        y = (self.height() - overlay_size.height()) // 2
        self.drag_overlay.move(max(0, x), max(0, y))
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            # Check if at least one file has a supported extension
            supported_exts = {'.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv', 
                            '.mp3', '.aac', '.wav', '.flac', '.m4a', '.ogg'}
            
            has_supported = False
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if Path(file_path).suffix.lower() in supported_exts:
                    has_supported = True
                    break
            
            if has_supported:
                event.accept()
                self.drag_overlay.show()
                self.drag_overlay.raise_()  # Bring to front
            else:
                event.ignore()
        else:
            event.ignore()
    
    def dragLeaveEvent(self, event):
        self.drag_overlay.hide()
    
    def dropEvent(self, event: QDropEvent):
        self.drag_overlay.hide()
        
        urls = event.mimeData().urls()
        files = []
        for url in urls:
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                files.append(file_path)
        
        if files:
            self.files_dropped.emit(files)


class QuickFormatButton(QPushButton):
    """Specialized button for quick format selection"""
    
    def __init__(self, label: str, format_type: str, color: str, parent=None):
        super().__init__(label, parent)
        self.format_type = format_type
        self.color = color
        
        self.setCheckable(True)
        self.setMinimumHeight(40)
        self.apply_style()
    
    def apply_style(self):
        """Apply custom styling"""
        self.setStyleSheet(f"""
            QPushButton {{
                padding: 10px 15px;
                border: 2px solid {self.color};
                border-radius: 8px;
                font-weight: bold;
                background-color: transparent;
                color: #ffffff;
            }}
            QPushButton:checked {{
                background-color: {self.color};
                color: white;
            }}
            QPushButton:hover {{
                background-color: {self.color}40;
            }}
            QPushButton:pressed {{
                background-color: {self.color}80;
            }}
        """)


class MediaInfoWidget(QFrame):
    """Widget to display media file information"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel)
        self.setMaximumHeight(150)
        
        layout = QVBoxLayout(self)
        
        # Title
        self.title_label = QLabel("File Information")
        self.title_label.setStyleSheet("font-weight: bold; color: #00A8E8; font-size: 12px;")
        layout.addWidget(self.title_label)
        
        # Info text
        self.info_label = QLabel("Select a file to view information...")
        self.info_label.setWordWrap(True)
        self.info_label.setAlignment(Qt.AlignTop)
        self.info_label.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 8px;
                color: #cccccc;
                font-family: 'Consolas', monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.info_label)
    
    def update_info(self, info_text: str):
        """Update the displayed information"""
        if info_text.strip():
            self.info_label.setText(info_text)
        else:
            self.info_label.setText("Unable to read file information")
    
    def clear_info(self):
        """Clear the information display"""
        self.info_label.setText("Select a file to view information...")


class ProcessingControlPanel(QFrame):
    """Control panel for processing operations"""
    start_processing = pyqtSignal()
    stop_processing = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel)
        self.setMaximumHeight(80)
        
        layout = QHBoxLayout(self)
        
        # Start button
        self.start_btn = QPushButton("🚀 Start Processing")
        self.start_btn.clicked.connect(self.start_processing.emit)
        self.start_btn.setMinimumHeight(50)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A8E8;
                color: white;
                border: none;
                padding: 15px 30px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #007BB8;
            }
            QPushButton:pressed {
                background-color: #005A87;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #999;
            }
        """)
        
        # Stop button
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.clicked.connect(self.stop_processing.emit)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setMinimumHeight(50)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 15px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #999;
            }
        """)
        
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)
        layout.addStretch()
    
    def set_processing_state(self, is_processing: bool):
        """Update button states based on processing status"""
        self.start_btn.setEnabled(not is_processing)
        self.stop_btn.setEnabled(is_processing)
        
        if is_processing:
            self.start_btn.setText("🔄 Processing...")
        else:
            self.start_btn.setText("🚀 Start Processing")


class BatchListWidget(QListWidget):
    """Custom list widget for batch operations"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumHeight(150)
        self.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #555;
                border-radius: 3px;
                color: #ffffff;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #333;
            }
            QListWidget::item:selected {
                background-color: #00A8E8;
            }
            QListWidget::item:hover {
                background-color: #404040;
            }
        """)
    
    def add_command(self, command: str):
        """Add a command to the batch list"""
        item = QListWidgetItem(command)
        item.setToolTip(command)  # Show full command on hover
        self.addItem(item)
    
    def get_all_commands(self) -> List[str]:
        """Get all commands in the list"""
        commands = []
        for i in range(self.count()):
            commands.append(self.item(i).text())
        return commands
    
    def clear_all(self):
        """Clear all items from the list"""
        self.clear()


class StatusInfoWidget(QFrame):
    """Widget to show current processing status and file info"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel)
        
        layout = QVBoxLayout(self)
        
        # Status line
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #00A8E8;
                font-weight: bold;
                font-size: 12px;
                padding: 5px;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Progress info
        self.progress_info = QLabel("")
        self.progress_info.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 11px;
                padding: 2px 5px;
            }
        """)
        layout.addWidget(self.progress_info)
        
    def set_status(self, status: str, color: str = "#00A8E8"):
        """Set the status text and color"""
        self.status_label.setText(status)
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-weight: bold;
                font-size: 12px;
                padding: 5px;
            }}
        """)
    
    def set_progress_info(self, info: str):
        """Set additional progress information"""
        self.progress_info.setText(info)
    
    def clear_progress_info(self):
        """Clear progress information"""
        self.progress_info.setText("")