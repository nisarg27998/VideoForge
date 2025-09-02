"""
Main Window for VideoForge
The primary application window containing all UI components
"""

import os
import sys
from pathlib import Path
from typing import List, Optional

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QMessageBox, QStatusBar, QProgressBar, QFileDialog, QApplication
)
from PyQt5.QtCore import QSettings, QTimer, pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QCloseEvent

# Import custom modules
from .widgets import DragDropWidget
from .simple_mode import SimpleModeWidget
from .advanced_mode import AdvancedModeWidget
from .dialogs import (
    FFmpegInstallDialog, ProgressDialog, ManualInstallDialog,
    ConfirmDialog, AboutDialog
)
from ..core.ffmpeg_manager import (
    FFmpegChecker, FFmpegInstaller, FFmpegWorker, get_video_info, format_file_info
)
from ..utils.styles import DarkTheme


class VideoForgeMainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VideoForge - Professional FFmpeg Frontend")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize components
        self.settings = QSettings("VideoForge", "Settings")
        self.worker = None
        self.installer = None
        self.ffmpeg_ready = False
        
        # Setup UI
        self.setup_ui()
        self.setup_menu_bar()
        self.load_settings()
        
        # Apply theme
        self.apply_theme()
        
        # Check FFmpeg on startup
        QTimer.singleShot(500, self.check_ffmpeg)  # Delay to show UI first
    
    def setup_ui(self):
        """Setup the main user interface"""
        # Create main drag-drop widget
        self.central_widget = DragDropWidget()
        self.central_widget.files_dropped.connect(self.handle_dropped_files)
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(self.central_widget)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Mode tabs
        self.tab_widget = QTabWidget()
        
        # Simple mode
        self.simple_mode = SimpleModeWidget()
        self.simple_mode.start_processing.connect(self.start_processing)
        self.simple_mode.file_info_requested.connect(self.update_file_info)
        self.tab_widget.addTab(self.simple_mode, "🎬 Simple Mode")
        
        # Advanced mode
        self.advanced_mode = AdvancedModeWidget()
        self.advanced_mode.start_processing.connect(self.start_processing)
        self.advanced_mode.start_batch.connect(self.start_batch_processing)
        self.tab_widget.addTab(self.advanced_mode, "⚙️ Advanced Mode")
        
        main_layout.addWidget(self.tab_widget)
        
        # Progress section
        progress_section = self.create_progress_section()
        main_layout.addWidget(progress_section)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Drag & drop files or use Browse buttons")
    
    def create_header(self) -> QWidget:
        """Create the application header"""
        from PyQt5.QtWidgets import QFrame, QLabel
        from PyQt5.QtGui import QFont
        
        header = QFrame()
        header.setFrameStyle(QFrame.StyledPanel)
        header.setMaximumHeight(80)
        
        layout = QHBoxLayout(header)
        
        # Title section
        title_label = QLabel("VideoForge")
        title_font = QFont()
        title_font.setPointSize(28)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #00A8E8;")
        
        subtitle_label = QLabel("Professional FFmpeg Frontend")
        subtitle_label.setStyleSheet("color: #888; font-size: 14px; font-style: italic;")
        
        title_layout = QVBoxLayout()
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        # Status indicator
        self.ffmpeg_status = QLabel("⚠️ Checking FFmpeg...")
        self.ffmpeg_status.setStyleSheet("""
            QLabel {
                background-color: #404040;
                border: 1px solid #555;
                border-radius: 15px;
                padding: 8px 15px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.ffmpeg_status)
        
        return header
    
    def create_progress_section(self) -> QWidget:
        """Create the progress and output section"""
        from PyQt5.QtWidgets import QSplitter, QGroupBox, QTextEdit
        from PyQt5.QtGui import QFont
        from .widgets import ProcessingControlPanel
        
        splitter = QSplitter(Qt.Vertical)
        
        # Control panel
        self.control_panel = ProcessingControlPanel()
        self.control_panel.start_processing.connect(self.start_processing)
        self.control_panel.stop_processing.connect(self.stop_processing)
        splitter.addWidget(self.control_panel)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #555;
                border-radius: 3px;
                text-align: center;
                background-color: #404040;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #00A8E8;
                border-radius: 2px;
            }
        """)
        
        # Add progress bar to control panel
        self.control_panel.layout().addWidget(self.progress_bar)
        
        # Log output
        log_group = QGroupBox("FFmpeg Output Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setPlaceholderText("FFmpeg output will appear here...")
        log_layout.addWidget(self.log_text)
        
        # Log controls
        log_controls = QHBoxLayout()
        from PyQt5.QtWidgets import QPushButton
        
        clear_log_btn = QPushButton("Clear Log")
        clear_log_btn.clicked.connect(self.log_text.clear)
        log_controls.addWidget(clear_log_btn)
        
        save_log_btn = QPushButton("Save Log")
        save_log_btn.clicked.connect(self.save_log)
        log_controls.addWidget(save_log_btn)
        
        log_controls.addStretch()
        log_layout.addLayout(log_controls)
        
        splitter.addWidget(log_group)
        splitter.setSizes([120, 300])
        
        return splitter
    
    def setup_menu_bar(self):
        """Setup the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        # Open file action
        open_action = file_menu.addAction("Open File...")
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file_dialog)
        
        file_menu.addSeparator()
        
        # Settings action
        settings_action = file_menu.addAction("Settings...")
        settings_action.triggered.connect(self.show_settings)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = file_menu.addAction("Exit")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        check_ffmpeg_action = tools_menu.addAction("Check FFmpeg")
        check_ffmpeg_action.triggered.connect(self.check_ffmpeg)
        
        install_ffmpeg_action = tools_menu.addAction("Install FFmpeg")
        install_ffmpeg_action.triggered.connect(self.show_ffmpeg_install_dialog)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = help_menu.addAction("About VideoForge")
        about_action.triggered.connect(self.show_about)
        
        help_action = help_menu.addAction("FFmpeg Documentation")
        help_action.triggered.connect(self.open_ffmpeg_docs)
    
    def apply_theme(self):
        """Apply the dark theme"""
        theme = DarkTheme()
        self.setStyleSheet(theme.get_stylesheet())
    
    def check_ffmpeg(self):
        """Check if FFmpeg is installed"""
        self.ffmpeg_status.setText("⚠️ Checking...")
        self.ffmpeg_status.setStyleSheet("""
            QLabel {
                background-color: #FFA500;
                color: black;
                border: 1px solid #FF8C00;
                border-radius: 15px;
                padding: 8px 15px;
                font-weight: bold;
            }
        """)
        
        self.ffmpeg_checker = FFmpegChecker()
        self.ffmpeg_checker.status_update.connect(self.status_bar.showMessage)
        self.ffmpeg_checker.finished_check.connect(self.on_ffmpeg_check_complete)
        self.ffmpeg_checker.show_install_dialog.connect(self.show_ffmpeg_install_dialog)
        self.ffmpeg_checker.start()
        
        # Disable processing during check
        self.control_panel.set_processing_state(True)
    
    def on_ffmpeg_check_complete(self, success: bool):
        """Handle FFmpeg check completion"""
        if success:
            self.ffmpeg_ready = True
            self.ffmpeg_status.setText("✅ FFmpeg Ready")
            self.ffmpeg_status.setStyleSheet("""
                QLabel {
                    background-color: #4CAF50;
                    color: white;
                    border: 1px solid #45a049;
                    border-radius: 15px;
                    padding: 8px 15px;
                    font-weight: bold;
                }
            """)
            self.control_panel.set_processing_state(False)
            self.status_bar.showMessage("Ready - FFmpeg is available")
        else:
            self.ffmpeg_ready = False
            self.ffmpeg_status.setText("❌ FFmpeg Missing")
            self.ffmpeg_status.setStyleSheet("""
                QLabel {
                    background-color: #f44336;
                    color: white;
                    border: 1px solid #d32f2f;
                    border-radius: 15px;
                    padding: 8px 15px;
                    font-weight: bold;
                }
            """)
            self.status_bar.showMessage("FFmpeg is required but not found")
    
    def show_ffmpeg_install_dialog(self):
        """Show FFmpeg installation dialog"""
        dialog = FFmpegInstallDialog(self)
        result = dialog.exec_()
        
        clicked_button = dialog.clickedButton()
        
        if clicked_button == dialog.install_btn:
            self.install_ffmpeg_with_progress()
        elif clicked_button == dialog.manual_btn:
            self.show_manual_install_info()
        else:
            # User chose to exit
            self.close()
    
    def install_ffmpeg_with_progress(self):
        """Install FFmpeg with progress dialog"""
        self.install_progress_dialog = ProgressDialog(
            "Installing FFmpeg", 
            "Please wait while FFmpeg is being installed...",
            self
        )
        self.install_progress_dialog.cancelled.connect(self.cancel_ffmpeg_install)
        self.install_progress_dialog.show()
        
        # Start installer thread
        self.installer = FFmpegInstaller()
        self.installer.status_update.connect(self.status_bar.showMessage)
        self.installer.progress_update.connect(self.install_progress_dialog.append_text)
        self.installer.finished_install.connect(self.on_ffmpeg_install_complete)
        self.installer.start()
    
    def cancel_ffmpeg_install(self):
        """Cancel FFmpeg installation"""
        if self.installer:
            self.installer.terminate()
        
        # Show exit confirmation
        reply = QMessageBox.question(self, "Exit Application", 
                                   "FFmpeg installation was cancelled.\n\n"
                                   "VideoForge requires FFmpeg to function.\n"
                                   "Do you want to exit the application?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.close()
    
    def show_manual_install_info(self):
        """Show manual installation instructions"""
        dialog = ManualInstallDialog(self)
        result = dialog.exec_()
        
        clicked = dialog.clickedButton()
        
        if clicked == dialog.retry_btn:
            self.check_ffmpeg()
        else:
            self.close()
    
    def on_ffmpeg_install_complete(self, success: bool, message: str):
        """Handle FFmpeg installation completion"""
        if hasattr(self, 'install_progress_dialog'):
            self.install_progress_dialog.close()
        
        if success:
            QMessageBox.information(self, "Installation Complete", 
                                  f"FFmpeg installation successful!\n\n{message}")
            self.on_ffmpeg_check_complete(True)
        else:
            QMessageBox.critical(self, "Installation Failed", 
                               f"FFmpeg installation failed:\n\n{message}\n\n"
                               "Please try manual installation.")
            self.show_manual_install_info()
    
    def handle_dropped_files(self, files: List[str]):
        """Handle files dropped on the main window"""
        if not files:
            return
        
        current_tab = self.tab_widget.currentIndex()
        
        if current_tab == 0:  # Simple mode
            self.simple_mode.handle_dropped_files(files)
        else:  # Advanced mode
            self.advanced_mode.handle_dropped_files(files)
        
        self.status_bar.showMessage(f"Loaded {len(files)} file(s)")
    
    def update_file_info(self, file_path: str):
        """Update file information display"""
        if not file_path or not os.path.exists(file_path):
            return
        
        # Get file info asynchronously to avoid UI blocking
        QTimer.singleShot(100, lambda: self._load_file_info(file_path))
    
    def _load_file_info(self, file_path: str):
        """Load file information"""
        try:
            info = get_video_info(file_path)
            formatted_info = format_file_info(info)
            
            # Update the current tab's file info display
            current_tab = self.tab_widget.currentIndex()
            if current_tab == 0:  # Simple mode
                self.simple_mode.update_file_info(formatted_info)
        except Exception as e:
            print(f"Error loading file info: {e}")
    
    def start_processing(self):
        """Start FFmpeg processing"""
        if not self.ffmpeg_ready:
            QMessageBox.warning(self, "FFmpeg Not Ready", 
                              "FFmpeg is not available. Please install it first.")
            return
        
        try:
            current_tab = self.tab_widget.currentIndex()
            
            if current_tab == 0:  # Simple mode
                command, duration = self.simple_mode.build_command()
            else:  # Advanced mode
                command, duration = self.advanced_mode.build_command()
            
            if not command:
                QMessageBox.warning(self, "Invalid Command", 
                                  "Please check your settings and try again.")
                return
            
            self.log_text.clear()
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.control_panel.set_processing_state(True)
            
            # Start worker thread
            self.worker = FFmpegWorker(command, duration)
            self.worker.progress_update.connect(self.progress_bar.setValue)
            self.worker.log_update.connect(self.append_log)
            self.worker.status_update.connect(self.status_bar.showMessage)
            self.worker.finished.connect(self.on_processing_finished)
            self.worker.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start processing: {str(e)}")
            self.reset_ui_state()
    
    def start_batch_processing(self, commands: List[str]):
        """Start batch processing"""
        if not self.ffmpeg_ready:
            QMessageBox.warning(self, "FFmpeg Not Ready", 
                              "FFmpeg is not available. Please install it first.")
            return
        
        if not commands:
            QMessageBox.warning(self, "No Commands", 
                              "No batch commands to process.")
            return
        
        # Import BatchProcessor here to avoid circular import
        from ..core.ffmpeg_manager import BatchProcessor
        
        self.log_text.clear()
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.control_panel.set_processing_state(True)
        
        # Start batch processor
        self.worker = BatchProcessor(commands)
        self.worker.progress_update.connect(self.progress_bar.setValue)
        self.worker.log_update.connect(self.append_log)
        self.worker.status_update.connect(self.status_bar.showMessage)
        self.worker.finished.connect(self.on_processing_finished)
        self.worker.start()
    
    def stop_processing(self):
        """Stop FFmpeg processing"""
        if self.worker:
            self.worker.stop()
            self.worker.wait()
        self.reset_ui_state()
        self.status_bar.showMessage("Processing stopped by user")
    
    def on_processing_finished(self, success: bool, message: str = ""):
        """Handle processing completion"""
        self.reset_ui_state()
        
        if success:
            # Check if user wants to open output folder
            current_tab = self.tab_widget.currentIndex()
            if current_tab == 0:  # Simple mode
                if self.simple_mode.should_open_output_folder():
                    output_path = self.simple_mode.get_output_path()
                    if output_path:
                        self.open_output_folder(str(Path(output_path).parent))
            
            self.status_bar.showMessage("Processing completed successfully!")
            
            # Show completion notification
            QMessageBox.information(self, "Success", 
                                  "Processing completed successfully!\n\n"
                                  "Check the output folder for your processed file(s).")
        else:
            self.status_bar.showMessage(f"Processing failed: {message}")
            QMessageBox.critical(self, "Processing Failed", 
                               f"Processing failed:\n\n{message}\n\n"
                               "Check the log for more details.")
    
    def reset_ui_state(self):
        """Reset UI to ready state"""
        self.control_panel.set_processing_state(False)
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
    
    def append_log(self, text: str):
        """Append text to log"""
        self.log_text.append(text.rstrip())
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def save_log(self):
        """Save log to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Log File", "ffmpeg_log.txt",
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.toPlainText())
                self.status_bar.showMessage(f"Log saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save log: {str(e)}")
    
    def open_file_dialog(self):
        """Open file selection dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Media File",
            self.settings.value("last_input_dir", str(Path.home())),
            "Media Files (*.mp4 *.mkv *.avi *.mov *.webm *.flv *.mp3 *.aac *.wav *.flac *.m4a *.ogg);;All Files (*.*)"
        )
        
        if file_path:
            self.settings.setValue("last_input_dir", str(Path(file_path).parent))
            
            # Pass to current tab
            current_tab = self.tab_widget.currentIndex()
            if current_tab == 0:  # Simple mode
                self.simple_mode.set_input_file(file_path)
            else:  # Advanced mode
                self.advanced_mode.add_input_file(file_path)
    
    def open_output_folder(self, folder_path: str):
        """Open output folder in file explorer"""
        try:
            if sys.platform == "win32":
                os.startfile(folder_path)
            elif sys.platform == "darwin":
                os.system(f"open '{folder_path}'")
            else:
                os.system(f"xdg-open '{folder_path}'")
        except Exception as e:
            print(f"Could not open folder: {e}")
    
    def show_settings(self):
        """Show settings dialog"""
        # Placeholder for settings dialog
        QMessageBox.information(self, "Settings", 
                              "Settings dialog will be implemented in a future update.")
    
    def show_about(self):
        """Show about dialog"""
        dialog = AboutDialog(self)
        dialog.exec_()
    
    def open_ffmpeg_docs(self):
        """Open FFmpeg documentation"""
        import webbrowser
        webbrowser.open("https://ffmpeg.org/documentation.html")
    
    def load_settings(self):
        """Load application settings"""
        # Restore window geometry
        geometry = self.settings.value("window_geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        # Restore window state
        state = self.settings.value("window_state")
        if state:
            self.restoreState(state)
        
        # Load last used directories
        self.last_input_dir = self.settings.value("last_input_dir", str(Path.home()))
        self.last_output_dir = self.settings.value("last_output_dir", str(Path.home() / "Desktop"))
    
    def save_settings(self):
        """Save application settings"""
        self.settings.setValue("window_geometry", self.saveGeometry())
        self.settings.setValue("window_state", self.saveState())
        self.settings.setValue("last_input_dir", getattr(self, 'last_input_dir', ''))
        self.settings.setValue("last_output_dir", getattr(self, 'last_output_dir', ''))
    
    def closeEvent(self, event: QCloseEvent):
        """Handle application close"""
        # Check if processing is running
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(self, "Confirm Exit", 
                                       "FFmpeg is still processing. Do you want to stop it and exit?",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.worker.stop()
                self.worker.wait()
            else:
                event.ignore()
                return
        
        # Save settings
        self.save_settings()
        
        # Clean up temporary files
        temp_files = ["temp_concat_list.txt", "concat_list.txt"]
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
        
        event.accept()