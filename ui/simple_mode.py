"""
Simple Mode Interface for VideoForge
User-friendly interface for common video operations
"""

import os
from pathlib import Path
from typing import List, Tuple, Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLabel, QPushButton, QComboBox, QSpinBox, QTimeEdit, QCheckBox,
    QGroupBox, QFileDialog, QLineEdit, QMessageBox
)
from PyQt5.QtCore import pyqtSignal, QTime, QSettings
from PyQt5.QtGui import QFont

from .widgets import DragDropLineEdit, QuickFormatButton, MediaInfoWidget
from ..core.command_builder import CommandBuilder, PresetManager
from ..core.ffmpeg_manager import get_video_duration


class SimpleModeWidget(QWidget):
    """Simple mode interface widget"""
    
    start_processing = pyqtSignal()
    file_info_requested = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings("VideoForge", "Settings")
        self.command_builder = CommandBuilder()
        self.preset_manager = PresetManager()
        
        self.setup_ui()
        self.connect_signals()
        
        # Initialize with default task
        self.on_task_changed("Convert Video Format")
    
    def setup_ui(self):
        """Setup the simple mode UI"""
        layout = QVBoxLayout(self)
        
        # Task selection
        task_group = self.create_task_selection()
        layout.addWidget(task_group)
        
        # Quick format buttons
        format_group = self.create_format_buttons()
        layout.addWidget(format_group)
        
        # Input/Output section
        io_group = self.create_io_section()
        layout.addWidget(io_group)
        
        # File information
        self.media_info = MediaInfoWidget()
        layout.addWidget(self.media_info)
        
        # Task-specific options
        self.options_group = QGroupBox("Task Options")
        self.options_layout = QFormLayout(self.options_group)
        layout.addWidget(self.options_group)
        
        # Presets section
        preset_group = self.create_preset_section()
        layout.addWidget(preset_group)
        
        # Smart options
        smart_group = self.create_smart_options()
        layout.addWidget(smart_group)
        
        layout.addStretch()
    
    def create_task_selection(self) -> QWidget:
        """Create task selection group"""
        task_group = QGroupBox("🎯 Select Task")
        task_layout = QVBoxLayout(task_group)
        
        self.task_combo = QComboBox()
        self.task_combo.addItems([
            "Convert Video Format",
            "Extract Audio", 
            "Compress Video",
            "Trim Video",
            "Merge Videos"
        ])
        self.task_combo.setMinimumHeight(40)
        self.task_combo.setStyleSheet("""
            QComboBox {
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        
        task_layout.addWidget(self.task_combo)
        return task_group
    
    def create_format_buttons(self) -> QWidget:
        """Create quick format selection buttons"""
        format_group = QGroupBox("🎬 Quick Format Selection")
        format_layout = QGridLayout(format_group)
        
        self.quick_format_buttons = []
        formats = [
            ("MP4 (Universal)", "mp4", "#00A8E8"),
            ("MKV (High Quality)", "mkv", "#4CAF50"), 
            ("AVI (Compatible)", "avi", "#FF9800"),
            ("MOV (Apple)", "mov", "#9C27B0"),
            ("WebM (Web)", "webm", "#607D8B"),
            ("MP3 Audio", "mp3", "#F44336")
        ]
        
        for i, (label, fmt, color) in enumerate(formats):
            btn = QuickFormatButton(label, fmt, color)
            btn.clicked.connect(lambda checked, f=fmt: self.select_quick_format(f))
            self.quick_format_buttons.append((btn, fmt))
            format_layout.addWidget(btn, i // 3, i % 3)
        
        return format_group
    
    def create_io_section(self) -> QWidget:
        """Create input/output section"""
        io_group = QGroupBox("📁 Files")
        io_layout = QFormLayout(io_group)
        
        # Input file
        self.input_edit = DragDropLineEdit(placeholder_text="Drag & drop files here or click Browse...")
        input_button = QPushButton("📂 Browse Files")
        input_button.clicked.connect(self.browse_input_file)
        
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_edit, 3)
        input_layout.addWidget(input_button, 1)
        io_layout.addRow("Input File:", input_layout)
        
        # Multiple input files (for merge)
        from .widgets import BatchListWidget
        self.input_list = BatchListWidget()
        self.input_list.setMaximumHeight(120)
        self.input_list.hide()
        
        input_list_layout = QHBoxLayout()
        input_list_layout.addWidget(self.input_list)
        
        input_list_buttons = QVBoxLayout()
        self.add_file_btn = QPushButton("➕ Add File")
        self.add_file_btn.clicked.connect(self.add_input_file)
        self.add_file_btn.hide()
        
        self.remove_file_btn = QPushButton("➖ Remove")
        self.remove_file_btn.clicked.connect(self.remove_input_file)
        self.remove_file_btn.hide()
        
        input_list_buttons.addWidget(self.add_file_btn)
        input_list_buttons.addWidget(self.remove_file_btn)
        input_list_buttons.addStretch()
        input_list_layout.addLayout(input_list_buttons)
        
        io_layout.addRow("Input Files:", input_list_layout)
        
        # Output folder
        self.output_dir_edit = DragDropLineEdit(accept_folders=True, 
                                              placeholder_text="Destination folder (auto-detected)")
        output_dir_button = QPushButton("📁 Browse Folder")
        output_dir_button.clicked.connect(self.browse_output_folder)
        
        output_dir_layout = QHBoxLayout()
        output_dir_layout.addWidget(self.output_dir_edit, 3)
        output_dir_layout.addWidget(output_dir_button, 1)
        io_layout.addRow("Destination:", output_dir_layout)
        
        # Output filename
        self.output_name_edit = QLineEdit()
        self.output_name_edit.setPlaceholderText("Filename (auto-generated)")
        io_layout.addRow("Output Name:", self.output_name_edit)
        
        # Preview full path
        self.output_preview = QLabel()
        self.output_preview.setStyleSheet("""
            QLabel {
                color: #888;
                font-style: italic;
                font-size: 11px;
                padding: 4px;
                background-color: #1e1e1e;
                border: 1px solid #555;
                border-radius: 3px;
            }
        """)
        self.output_preview.setWordWrap(True)
        io_layout.addRow("Full Path:", self.output_preview)
        
        return io_group
    
    def create_preset_section(self) -> QWidget:
        """Create preset selection section"""
        preset_group = QGroupBox("⚡ Presets")
        preset_layout = QHBoxLayout(preset_group)
        
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("🔧 Custom Settings")
        for preset_name in self.preset_manager.get_preset_names():
            self.preset_combo.addItem(f"📋 {preset_name}")
        
        self.preset_combo.setMinimumHeight(35)
        preset_layout.addWidget(self.preset_combo)
        
        return preset_group
    
    def create_smart_options(self) -> QWidget:
        """Create smart processing options"""
        smart_group = QGroupBox("🧠 Smart Options")
        smart_layout = QVBoxLayout(smart_group)
        
        self.auto_optimize_cb = QCheckBox("🌐 Optimize for web playback")
        self.auto_optimize_cb.setChecked(True)
        self.auto_optimize_cb.setToolTip("Adds web optimization flags for better streaming")
        smart_layout.addWidget(self.auto_optimize_cb)
        
        self.preserve_metadata_cb = QCheckBox("📄 Preserve original metadata")
        self.preserve_metadata_cb.setChecked(True)
        self.preserve_metadata_cb.setToolTip("Keep original file metadata like creation date")
        smart_layout.addWidget(self.preserve_metadata_cb)
        
        self.open_output_cb = QCheckBox("📂 Open output folder when complete")
        self.open_output_cb.setChecked(True)
        self.open_output_cb.setToolTip("Automatically open the destination folder")
        smart_layout.addWidget(self.open_output_cb)
        
        return smart_group
    
    def connect_signals(self):
        """Connect UI signals"""
        self.task_combo.currentTextChanged.connect(self.on_task_changed)
        self.input_edit.file_dropped.connect(self.on_input_file_changed)
        self.input_edit.textChanged.connect(self.on_input_file_changed)
        self.output_dir_edit.textChanged.connect(self.update_output_preview)
        self.output_name_edit.textChanged.connect(self.update_output_preview)
        self.preset_combo.currentTextChanged.connect(self.apply_preset)
    
    def on_task_changed(self, task: str):
        """Handle task selection change"""
        # Clear existing options
        for i in reversed(range(self.options_layout.count())):
            self.options_layout.itemAt(i).widget().setParent(None)
        
        # Reset input UI visibility
        if task == "Merge Videos":
            self.input_edit.hide()
            self.input_list.show()
            self.add_file_btn.show()
            self.remove_file_btn.show()
        else:
            self.input_edit.show()
            self.input_list.hide()
            self.add_file_btn.hide()
            self.remove_file_btn.hide()
        
        # Setup task-specific options
        if task == "Convert Video Format":
            self.setup_convert_options()
        elif task == "Extract Audio":
            self.setup_audio_options()
        elif task == "Compress Video":
            self.setup_compress_options()
        elif task == "Trim Video":
            self.setup_trim_options()
        elif task == "Merge Videos":
            self.setup_merge_options()
        
        # Update filename
        self.update_output_filename()
    
    def setup_convert_options(self):
        """Setup options for video conversion"""
        self.format_combo = QComboBox()
        self.format_combo.addItems(["mp4", "mkv", "avi", "mov", "webm", "flv"])
        self.options_layout.addRow("🎬 Output Format:", self.format_combo)
        
        self.video_codec_combo = QComboBox()
        self.video_codec_combo.addItems(["libx264", "libx265", "copy", "libvpx-vp9"])
        self.video_codec_combo.setToolTip("Video codec for encoding")
        self.options_layout.addRow("🎥 Video Codec:", self.video_codec_combo)
        
        self.audio_codec_combo = QComboBox()
        self.audio_codec_combo.addItems(["aac", "mp3", "copy", "libvorbis"])
        self.audio_codec_combo.setToolTip("Audio codec for encoding")
        self.options_layout.addRow("🔊 Audio Codec:", self.audio_codec_combo)
    
    def setup_audio_options(self):
        """Setup options for audio extraction"""
        self.audio_format_combo = QComboBox()
        self.audio_format_combo.addItems(["mp3", "aac", "wav", "flac", "ogg"])
        self.options_layout.addRow("🎵 Audio Format:", self.audio_format_combo)
        
        self.audio_quality_combo = QComboBox()
        self.audio_quality_combo.addItems(["128k", "192k", "256k", "320k"])
        self.audio_quality_combo.setCurrentText("192k")
        self.options_layout.addRow("🎚️ Audio Bitrate:", self.audio_quality_combo)
    
    def setup_compress_options(self):
        """Setup options for video compression"""
        self.crf_spin = QSpinBox()
        self.crf_spin.setRange(0, 51)
        self.crf_spin.setValue(23)
        self.crf_spin.setToolTip("Lower values = higher quality, larger file size (18-28 recommended)")
        self.options_layout.addRow("📊 CRF Quality:", self.crf_spin)
        
        self.preset_combo_compress = QComboBox()
        self.preset_combo_compress.addItems([
            "ultrafast", "superfast", "veryfast", "faster", 
            "fast", "medium", "slow", "slower", "veryslow"
        ])
        self.preset_combo_compress.setCurrentText("medium")
        self.preset_combo_compress.setToolTip("Encoding speed vs compression efficiency")
        self.options_layout.addRow("⚡ Encoding Speed:", self.preset_combo_compress)
        
        self.scale_combo = QComboBox()
        self.scale_combo.addItems(["Original", "1080p", "720p", "480p", "360p"])
        self.scale_combo.setToolTip("Output video resolution")
        self.options_layout.addRow("📐 Resolution:", self.scale_combo)
    
    def setup_trim_options(self):
        """Setup options for video trimming"""
        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setDisplayFormat("hh:mm:ss")
        self.start_time_edit.setToolTip("Start time for trimming")
        self.options_layout.addRow("▶️ Start Time:", self.start_time_edit)
        
        self.end_time_edit = QTimeEdit()
        self.end_time_edit.setDisplayFormat("hh:mm:ss")
        self.end_time_edit.setToolTip("End time for trimming")
        self.options_layout.addRow("⏹️ End Time:", self.end_time_edit)
        
        self.duration_edit = QTimeEdit()
        self.duration_edit.setDisplayFormat("hh:mm:ss")
        self.duration_edit.setToolTip("Duration (alternative to end time)")
        self.options_layout.addRow("⏱️ Duration:", self.duration_edit)
    
    def setup_merge_options(self):
        """Setup options for video merging"""
        self.merge_method_combo = QComboBox()
        self.merge_method_combo.addItems([
            "Fast Concat (same codecs)", 
            "Re-encode (different codecs)"
        ])
        self.merge_method_combo.setToolTip("Fast concat for same formats, re-encode for mixed formats")
        self.options_layout.addRow("🔗 Merge Method:", self.merge_method_combo)
        
        self.output_codec_combo = QComboBox()
        self.output_codec_combo.addItems(["libx264", "libx265", "copy"])
        self.output_codec_combo.setToolTip("Output video codec for re-encoding")
        self.options_layout.addRow("🎥 Output Codec:", self.output_codec_combo)
    
    def select_quick_format(self, format_type: str):
        """Handle quick format selection"""
        # Uncheck all other buttons
        for btn, fmt in self.quick_format_buttons:
            btn.setChecked(fmt == format_type)
        
        # Auto-select appropriate task
        if format_type in ['mp3', 'aac', 'wav', 'flac']:
            self.task_combo.setCurrentText("Extract Audio")
        else:
            self.task_combo.setCurrentText("Convert Video Format")
        
        # Update format combo if it exists
        if hasattr(self, 'format_combo') and format_type not in ['mp3', 'aac', 'wav', 'flac']:
            idx = self.format_combo.findText(format_type)
            if idx >= 0:
                self.format_combo.setCurrentIndex(idx)
        elif hasattr(self, 'audio_format_combo') and format_type in ['mp3', 'aac', 'wav', 'flac']:
            idx = self.audio_format_combo.findText(format_type)
            if idx >= 0:
                self.audio_format_combo.setCurrentIndex(idx)
        
        # Auto-generate filename
        self.update_output_filename()
    
    def on_input_file_changed(self, file_path: str = None):
        """Handle input file change"""
        if file_path is None:
            file_path = self.input_edit.text()
        
        if not file_path or not os.path.exists(file_path):
            self.media_info.clear_info()
            return
        
        # Request file info update
        self.file_info_requested.emit(file_path)
        
        # Auto-detect and suggest format/task
        self.auto_detect_settings(file_path)
        
        # Auto-generate filename and set output folder
        self.update_output_filename()
        self.auto_set_output_folder(file_path)
    
    def auto_detect_settings(self, file_path: str):
        """Auto-detect optimal settings for the file"""
        file_ext = Path(file_path).suffix.lower()
        
        # Auto-select task based on file type and size
        if file_ext in ['.mp3', '.aac', '.wav', '.flac', '.m4a', '.ogg']:
            # Audio file
            return  # Keep current task
        else:
            # Video file - check size for compression suggestion
            try:
                file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                if file_size_mb > 100:  # Large file
                    # Suggest compression
                    for btn, fmt in self.quick_format_buttons:
                        if fmt == 'mp4':
                            btn.setChecked(True)
                            break
                    if self.task_combo.currentText() != "Merge Videos":
                        self.task_combo.setCurrentText("Compress Video")
            except:
                pass
    
    def auto_set_output_folder(self, input_file: str):
        """Auto-set output folder if not specified"""
        if not self.output_dir_edit.text():
            input_folder = str(Path(input_file).parent)
            self.output_dir_edit.setText(input_folder)
    
    def update_output_filename(self):
        """Auto-generate output filename"""
        input_file = self.input_edit.text()
        if not input_file:
            self.output_preview.setText("")
            return
        
        input_path = Path(input_file)
        base_name = input_path.stem
        
        # Determine extension and suffix
        task = self.task_combo.currentText()
        ext, suffix = self.get_output_extension_and_suffix(task)
        
        # Generate filename
        new_filename = f"{base_name}{suffix}.{ext}"
        if not self.output_name_edit.text() or self.output_name_edit.text().endswith(f".{ext}"):
            self.output_name_edit.setText(new_filename)
        
        self.update_output_preview()
    
    def get_output_extension_and_suffix(self, task: str) -> Tuple[str, str]:
        """Get output extension and suffix based on task"""
        if task == "Extract Audio":
            ext = getattr(self, 'audio_format_combo', None)
            ext = ext.currentText() if ext else 'mp3'
            return ext, "_audio"
        elif task == "Compress Video":
            return 'mp4', "_compressed"
        elif task == "Trim Video":
            return 'mp4', "_trimmed"
        elif task == "Merge Videos":
            return 'mp4', "_merged"
        else:  # Convert Video Format
            ext = getattr(self, 'format_combo', None)
            ext = ext.currentText() if ext else 'mp4'
            return ext, "_converted"
    
    def update_output_preview(self):
        """Update output path preview"""
        folder = self.output_dir_edit.text()
        filename = self.output_name_edit.text()
        
        if not folder and self.input_edit.text():
            folder = str(Path(self.input_edit.text()).parent)
        
        if folder and filename:
            full_path = str(Path(folder) / filename)
            if len(full_path) > 60:
                # Truncate long paths
                preview = f"...{full_path[-60:]}"
            else:
                preview = full_path
            self.output_preview.setText(preview)
        else:
            self.output_preview.setText("Output path will be shown here")
    
    def apply_preset(self, preset_text: str):
        """Apply selected preset"""
        if not preset_text or "Custom" in preset_text:
            return
        
        # Extract preset name
        preset_name = preset_text.replace("📋 ", "")
        preset = self.preset_manager.get_preset(preset_name)
        
        if not preset:
            return
        
        # Apply preset values to current options
        current_task = self.task_combo.currentText()
        
        if current_task == "Convert Video Format" and hasattr(self, 'format_combo'):
            format_val = preset.get("format", "mp4")
            idx = self.format_combo.findText(format_val)
            if idx >= 0:
                self.format_combo.setCurrentIndex(idx)
        
        if current_task == "Compress Video":
            if hasattr(self, 'crf_spin'):
                self.crf_spin.setValue(preset.get("crf", 23))
            if hasattr(self, 'preset_combo_compress'):
                preset_val = preset.get("preset", "medium")
                idx = self.preset_combo_compress.findText(preset_val)
                if idx >= 0:
                    self.preset_combo_compress.setCurrentIndex(idx)
            if hasattr(self, 'scale_combo') and "scale" in preset:
                scale_val = preset["scale"]
                idx = self.scale_combo.findText(scale_val)
                if idx >= 0:
                    self.scale_combo.setCurrentIndex(idx)
    
    def handle_dropped_files(self, files: List[str]):
        """Handle files dropped on the widget"""
        if not files:
            return
        
        current_task = self.task_combo.currentText()
        
        if current_task == "Merge Videos" and len(files) > 1:
            # Add all files to merge list
            self.input_list.clear_all()
            for file_path in files:
                self.input_list.add_command(file_path)
        else:
            # Use first file as input
            self.input_edit.setText(files[0])
            
            if len(files) > 1:
                # Ask about merging
                from PyQt5.QtWidgets import QMessageBox
                reply = QMessageBox.question(
                    self, "Multiple Files", 
                    f"You dropped {len(files)} files.\n\n"
                    "Would you like to merge them into one video?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.task_combo.setCurrentText("Merge Videos")
                    self.input_list.clear_all()
                    for file_path in files:
                        self.input_list.add_command(file_path)
    
    def build_command(self) -> Tuple[List[str], float]:
        """Build FFmpeg command for current settings"""
        task = self.task_combo.currentText()
        
        try:
            if task == "Merge Videos":
                return self.build_merge_command()
            else:
                return self.build_single_file_command()
        except Exception as e:
            QMessageBox.critical(self, "Command Error", f"Failed to build command: {str(e)}")
            return [], 0.0
    
    def build_merge_command(self) -> Tuple[List[str], float]:
        """Build merge command"""
        input_files = self.input_list.get_all_commands()
        if len(input_files) < 2:
            raise ValueError("Please select at least 2 files to merge")
        
        output_path = self.get_output_path()
        if not output_path:
            raise ValueError("Please specify output file")
        
        method = getattr(self, 'merge_method_combo', None)
        method_text = method.currentText() if method else "fast"
        
        output_codec = getattr(self, 'output_codec_combo', None)
        codec = output_codec.currentText() if output_codec else "libx264"
        
        cmd = self.command_builder.build_merge_command(input_files, output_path, method_text, codec)
        
        # Add optimization flags
        cmd = self.command_builder.add_optimization_flags(
            cmd, 
            self.auto_optimize_cb.isChecked(),
            self.preserve_metadata_cb.isChecked()
        )
        
        # Estimate total duration
        total_duration = self.command_builder.get_estimated_duration(input_files)
        
        return cmd, total_duration
    
    def build_single_file_command(self) -> Tuple[List[str], float]:
        """Build command for single file operations"""
        input_file = self.input_edit.text()
        if not input_file:
            raise ValueError("Please select an input file")
        
        output_path = self.get_output_path()
        if not output_path:
            raise ValueError("Please specify output file")
        
        task = self.task_combo.currentText()
        
        if task == "Convert Video Format":
            cmd = self.build_convert_command(input_file, output_path)
        elif task == "Extract Audio":
            cmd = self.build_audio_command(input_file, output_path)
        elif task == "Compress Video":
            cmd = self.build_compress_command(input_file, output_path)
        elif task == "Trim Video":
            cmd = self.build_trim_command(input_file, output_path)
        else:
            raise ValueError(f"Unknown task: {task}")
        
        # Add optimization flags
        cmd = self.command_builder.add_optimization_flags(
            cmd,
            self.auto_optimize_cb.isChecked(),
            self.preserve_metadata_cb.isChecked()
        )
        
        # Get duration for progress tracking
        duration = get_video_duration(input_file)
        
        return cmd, duration
    
    def build_convert_command(self, input_file: str, output_file: str) -> List[str]:
        """Build convert command"""
        video_codec = getattr(self, 'video_codec_combo', None)
        video_codec = video_codec.currentText() if video_codec else "libx264"
        
        audio_codec = getattr(self, 'audio_codec_combo', None)
        audio_codec = audio_codec.currentText() if audio_codec else "aac"
        
        return self.command_builder.build_convert_command(
            input_file, output_file, video_codec, audio_codec
        )
    
    def build_audio_command(self, input_file: str, output_file: str) -> List[str]:
        """Build audio extraction command"""
        audio_format = getattr(self, 'audio_format_combo', None)
        audio_format = audio_format.currentText() if audio_format else "mp3"
        
        bitrate = getattr(self, 'audio_quality_combo', None)
        bitrate = bitrate.currentText() if bitrate else "192k"
        
        return self.command_builder.build_audio_extract_command(
            input_file, output_file, audio_format, bitrate
        )
    
    def build_compress_command(self, input_file: str, output_file: str) -> List[str]:
        """Build compression command"""
        crf = getattr(self, 'crf_spin', None)
        crf = crf.value() if crf else 23
        
        preset = getattr(self, 'preset_combo_compress', None)
        preset = preset.currentText() if preset else "medium"
        
        scale = getattr(self, 'scale_combo', None)
        scale = scale.currentText() if scale else "Original"
        
        return self.command_builder.build_compress_command(
            input_file, output_file, crf, preset, scale
        )
    
    def build_trim_command(self, input_file: str, output_file: str) -> List[str]:
        """Build trim command"""
        start_time = getattr(self, 'start_time_edit', None)
        start_time = start_time.time().toString("hh:mm:ss") if start_time else "00:00:00"
        
        end_time = getattr(self, 'end_time_edit', None)
        end_time = end_time.time().toString("hh:mm:ss") if end_time else "00:00:00"
        
        duration = getattr(self, 'duration_edit', None)
        duration = duration.time().toString("hh:mm:ss") if duration else "00:00:00"
        
        return self.command_builder.build_trim_command(
            input_file, output_file, start_time, end_time, duration
        )
    
    def get_output_path(self) -> str:
        """Get the complete output file path"""
        folder = self.output_dir_edit.text()
        filename = self.output_name_edit.text()
        
        if not folder and self.input_edit.text():
            folder = str(Path(self.input_edit.text()).parent)
        
        if not folder:
            folder = str(Path.home() / "Desktop")
        
        if not filename:
            self.update_output_filename()
            filename = self.output_name_edit.text()
        
        return str(Path(folder) / filename)
    
    def should_open_output_folder(self) -> bool:
        """Check if output folder should be opened after completion"""
        return self.open_output_cb.isChecked()
    
    def set_input_file(self, file_path: str):
        """Set input file programmatically"""
        self.input_edit.setText(file_path)
        self.on_input_file_changed(file_path)
    
    def browse_input_file(self):
        """Browse for input file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Input File",
            self.settings.value("last_input_dir", str(Path.home())),
            "Media Files (*.mp4 *.mkv *.avi *.mov *.webm *.flv *.mp3 *.aac *.wav *.flac *.m4a *.ogg);;All Files (*.*)"
        )
        
        if file_path:
            self.settings.setValue("last_input_dir", str(Path(file_path).parent))
            self.input_edit.setText(file_path)
            self.on_input_file_changed(file_path)
    
    def add_input_file(self):
        """Add file to merge list"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Video File",
            self.settings.value("last_input_dir", str(Path.home())),
            "Video Files (*.mp4 *.mkv *.avi *.mov *.webm *.flv);;All Files (*.*)"
        )
        
        if file_path:
            self.settings.setValue("last_input_dir", str(Path(file_path).parent))
            self.input_list.add_command(file_path)
            self.update_output_filename()
    
    def remove_input_file(self):
        """Remove selected file from merge list"""
        current_row = self.input_list.currentRow()
        if current_row >= 0:
            self.input_list.takeItem(current_row)
            self.update_output_filename()
    
    def browse_output_folder(self):
        """Browse for output folder"""
        folder_path = QFileDialog.getExistingDirectory(
            self, "Select Destination Folder",
            self.settings.value("last_output_dir", str(Path.home() / "Desktop"))
        )
        
        if folder_path:
            self.settings.setValue("last_output_dir", folder_path)
            self.output_dir_edit.setText(folder_path)
            self.update_output_preview()
    
    def update_file_info(self, info_text: str):
        """Update file information display"""
        self.media_info.update_info(info_text)