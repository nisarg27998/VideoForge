"""
Advanced Mode Interface for VideoForge
Custom command interface and batch processing
"""

from pathlib import Path
from typing import List, Tuple

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QGroupBox, QFileDialog, QMessageBox
)
from PyQt5.QtCore import pyqtSignal, QSettings
from PyQt5.QtGui import QFont

from .widgets import BatchListWidget
from ..core.command_builder import CommandBuilder


class AdvancedModeWidget(QWidget):
    """Advanced mode interface widget"""
    
    start_processing = pyqtSignal()
    start_batch = pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings("VideoForge", "Settings")
        self.command_builder = CommandBuilder()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the advanced mode UI"""
        layout = QVBoxLayout(self)
        
        # Custom command section
        cmd_group = self.create_command_section()
        layout.addWidget(cmd_group)
        
        # Batch processing section
        batch_group = self.create_batch_section()
        layout.addWidget(batch_group)
        
        layout.addStretch()
    
    def create_command_section(self) -> QWidget:
        """Create custom command section"""
        cmd_group = QGroupBox("⚙️ Custom FFmpeg Command")
        cmd_layout = QVBoxLayout(cmd_group)
        
        # Command text area
        self.custom_cmd_edit = QTextEdit()
        self.custom_cmd_edit.setMaximumHeight(120)
        self.custom_cmd_edit.setFont(QFont("Consolas", 10))
        self.custom_cmd_edit.setPlaceholderText(
            "Enter custom FFmpeg arguments here...\n\n"
            "Examples:\n"
            "• -i input.mp4 -c:v libx264 -crf 23 output.mp4\n"
            "• -i input.mov -c:v libx265 -preset slow output.mkv\n"
            "• -i video.mp4 -vn -c:a mp3 -b:a 192k audio.mp3"
        )
        cmd_layout.addWidget(self.custom_cmd_edit)
        
        # Helper buttons
        helper_layout = QHBoxLayout()
        
        input_btn = QPushButton("📂 Add Input (-i)")
        input_btn.clicked.connect(self.add_input_to_command)
        helper_layout.addWidget(input_btn)
        
        output_btn = QPushButton("💾 Set Output")
        output_btn.clicked.connect(self.add_output_to_command)
        helper_layout.addWidget(output_btn)
        
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.clicked.connect(self.custom_cmd_edit.clear)
        helper_layout.addWidget(clear_btn)
        
        helper_layout.addStretch()
        
        # Common presets
        presets_btn = QPushButton("📋 Common Commands")
        presets_btn.clicked.connect(self.show_command_presets)
        helper_layout.addWidget(presets_btn)
        
        cmd_layout.addLayout(helper_layout)
        
        return cmd_group
    
    def create_batch_section(self) -> QWidget:
        """Create batch processing section"""
        batch_group = QGroupBox("📊 Batch Processing")
        batch_layout = QVBoxLayout(batch_group)
        
        # Batch list
        self.batch_list = BatchListWidget()
        batch_layout.addWidget(self.batch_list)
        
        # Batch controls
        batch_controls = QHBoxLayout()
        
        add_batch_btn = QPushButton("➕ Add to Batch")
        add_batch_btn.clicked.connect(self.add_to_batch)
        batch_controls.addWidget(add_batch_btn)
        
        remove_batch_btn = QPushButton("➖ Remove Selected")
        remove_batch_btn.clicked.connect(self.remove_from_batch)
        batch_controls.addWidget(remove_batch_btn)
        
        clear_batch_btn = QPushButton("🗑️ Clear All")
        clear_batch_btn.clicked.connect(self.clear_batch)
        batch_controls.addWidget(clear_batch_btn)
        
        batch_controls.addStretch()
        
        process_batch_btn = QPushButton("🚀 Process Batch")
        process_batch_btn.clicked.connect(self.process_batch)
        process_batch_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        batch_controls.addWidget(process_batch_btn)
        
        batch_layout.addLayout(batch_controls)
        
        return batch_group
    
    def add_input_to_command(self):
        """Add input file to custom command"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Input File",
            self.settings.value("last_input_dir", ""),
            "Media Files (*.mp4 *.mkv *.avi *.mov *.webm *.flv *.mp3 *.aac *.wav *.flac);;All Files (*.*)"
        )
        
        if file_path:
            self.settings.setValue("last_input_dir", str(Path(file_path).parent))
            current_text = self.custom_cmd_edit.toPlainText()
            new_text = current_text + f' -i "{file_path}"'
            self.custom_cmd_edit.setPlainText(new_text)
    
    def add_output_to_command(self):
        """Add output file to custom command"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Output File",
            self.settings.value("last_output_dir", ""),
            "Media Files (*.mp4 *.mkv *.avi *.mov *.mp3 *.aac *.wav *.flac);;All Files (*.*)"
        )
        
        if file_path:
            self.settings.setValue("last_output_dir", str(Path(file_path).parent))
            current_text = self.custom_cmd_edit.toPlainText()
            new_text = current_text + f' "{file_path}"'
            self.custom_cmd_edit.setPlainText(new_text)
    
    def show_command_presets(self):
        """Show common command presets"""
        from PyQt5.QtWidgets import QDialog, QListWidget, QVBoxLayout, QHBoxLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Common FFmpeg Commands")
        dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Preset list
        preset_list = QListWidget()
        presets = [
            ("Convert to MP4 (H.264)", "-i input.mp4 -c:v libx264 -crf 23 -c:a aac output.mp4"),
            ("High Quality MP4", "-i input.avi -c:v libx264 -crf 18 -preset slow -c:a aac output.mp4"),
            ("Compress Video", "-i input.mp4 -c:v libx264 -crf 28 -preset fast output.mp4"),
            ("Extract Audio MP3", "-i input.mp4 -vn -c:a libmp3lame -b:a 192k output.mp3"),
            ("Convert to WebM", "-i input.mp4 -c:v libvpx-vp9 -crf 30 -c:a libvorbis output.webm"),
            ("Resize Video 720p", "-i input.mp4 -vf scale=1280:720 -c:v libx264 -crf 23 output.mp4"),
            ("Trim Video", "-i input.mp4 -ss 00:01:00 -t 00:02:30 -c copy output.mp4"),
            ("Convert to GIF", "-i input.mp4 -vf fps=10,scale=320:-1 -t 10 output.gif"),
            ("Audio Normalization", "-i input.mp4 -af loudnorm -c:v copy output.mp4"),
            ("Remove Audio", "-i input.mp4 -an -c:v copy output.mp4")
        ]
        
        for name, command in presets:
            preset_list.addItem(f"{name}: {command}")
        
        layout.addWidget(preset_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        use_btn = QPushButton("Use Command")
        use_btn.clicked.connect(lambda: self.use_preset_command(preset_list, dialog))
        button_layout.addWidget(use_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.close)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec_()
    
    def use_preset_command(self, preset_list, dialog):
        """Use selected preset command"""
        current_item = preset_list.currentItem()
        if current_item:
            command_text = current_item.text()
            # Extract command part after the colon
            if ': ' in command_text:
                command = command_text.split(': ', 1)[1]
                self.custom_cmd_edit.setPlainText(command)
            dialog.close()
    
    def add_to_batch(self):
        """Add current command to batch list"""
        command_text = self.custom_cmd_edit.toPlainText().strip()
        
        if not command_text:
            QMessageBox.warning(self, "Empty Command", "Please enter a command first.")
            return
        
        # Validate command
        try:
            cmd = self.command_builder.build_custom_command(command_text)
            valid, message = self.command_builder.validate_command(cmd)
            
            if not valid:
                QMessageBox.warning(self, "Invalid Command", f"Command validation failed:\n{message}")
                return
                
        except Exception as e:
            QMessageBox.warning(self, "Invalid Command", f"Command syntax error:\n{str(e)}")
            return
        
        # Add to batch
        self.batch_list.add_command(command_text)
        QMessageBox.information(self, "Added", "Command added to batch successfully!")
    
    def remove_from_batch(self):
        """Remove selected item from batch"""
        current_row = self.batch_list.currentRow()
        if current_row >= 0:
            self.batch_list.takeItem(current_row)
        else:
            QMessageBox.information(self, "No Selection", "Please select a command to remove.")
    
    def clear_batch(self):
        """Clear all batch items"""
        if self.batch_list.count() > 0:
            reply = QMessageBox.question(
                self, "Clear Batch",
                f"Are you sure you want to clear all {self.batch_list.count()} commands?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.batch_list.clear_all()
        else:
            QMessageBox.information(self, "Empty Batch", "Batch list is already empty.")
    
    def process_batch(self):
        """Process batch commands"""
        commands = self.batch_list.get_all_commands()
        
        if not commands:
            QMessageBox.warning(self, "Empty Batch", "No commands in batch to process.")
            return
        
        reply = QMessageBox.question(
            self, "Process Batch",
            f"Process {len(commands)} commands in batch?\n\n"
            "This may take a long time depending on the operations.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.start_batch.emit(commands)
    
    def handle_dropped_files(self, files: List[str]):
        """Handle files dropped on advanced mode"""
        if not files:
            return
        
        # Add first file as input to current command
        file_path = files[0]
        current_text = self.custom_cmd_edit.toPlainText()
        
        if not current_text.strip():
            # Start new command
            self.custom_cmd_edit.setPlainText(f'-i "{file_path}"')
        else:
            # Append to existing command
            new_text = current_text + f' -i "{file_path}"'
            self.custom_cmd_edit.setPlainText(new_text)
    
    def add_input_file(self, file_path: str):
        """Add input file programmatically"""
        current_text = self.custom_cmd_edit.toPlainText()
        new_text = current_text + f' -i "{file_path}"'
        self.custom_cmd_edit.setPlainText(new_text)
    
    def build_command(self) -> Tuple[List[str], float]:
        """Build FFmpeg command from custom input"""
        command_text = self.custom_cmd_edit.toPlainText().strip()
        
        if not command_text:
            raise ValueError("Please enter a custom FFmpeg command")
        
        try:
            cmd = self.command_builder.build_custom_command(command_text)
            valid, message = self.command_builder.validate_command(cmd)
            
            if not valid:
                raise ValueError(f"Invalid command: {message}")
            
            return cmd, 0.0  # No duration estimation for custom commands
            
        except Exception as e:
            raise ValueError(f"Command error: {str(e)}")