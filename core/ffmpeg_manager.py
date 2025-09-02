"""
FFmpeg Management Module
Handles FFmpeg detection, installation, and execution
"""

import subprocess
import time
import json
import re
import shlex
from pathlib import Path
from typing import List, Optional, Dict, Any

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox, QTextEdit, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class FFmpegChecker(QThread):
    """Thread to check FFmpeg installation"""
    status_update = pyqtSignal(str)
    finished_check = pyqtSignal(bool)
    show_install_dialog = pyqtSignal()
    
    def run(self):
        self.status_update.emit("Checking FFmpeg installation...")
        
        # Check if FFmpeg is available
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.status_update.emit("FFmpeg found and ready!")
                self.finished_check.emit(True)
                return
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
            pass
        
        # FFmpeg not found - signal to show dialog
        self.show_install_dialog.emit()


class FFmpegInstaller(QThread):
    """Thread to install FFmpeg with progress updates"""
    status_update = pyqtSignal(str)
    progress_update = pyqtSignal(str)
    finished_install = pyqtSignal(bool, str)
    
    def run(self):
        self.status_update.emit("Installing FFmpeg...")
        self.progress_update.emit("Checking Windows Package Manager...")
        
        # First check if winget is available
        try:
            result = subprocess.run(['winget', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                self.finished_install.emit(False, "Windows Package Manager (winget) is not available")
                return
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.finished_install.emit(False, "Windows Package Manager (winget) is not available")
            return
        
        self.progress_update.emit("Windows Package Manager found. Installing FFmpeg...")
        
        # Install FFmpeg
        try:
            process = subprocess.Popen(
                ['winget', 'install', 'Gyan.FFmpeg', '--accept-package-agreements', '--accept-source-agreements'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True
            )
            
            # Read output line by line
            for line in iter(process.stdout.readline, ''):
                if line.strip():
                    self.progress_update.emit(line.strip())
            
            process.wait()
            
            if process.returncode == 0:
                self.progress_update.emit("FFmpeg installation completed!")
                time.sleep(2)  # Wait for PATH to update
                
                # Verify installation
                self.progress_update.emit("Verifying FFmpeg installation...")
                try:
                    result = subprocess.run(['ffmpeg', '-version'], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        self.finished_install.emit(True, "FFmpeg installed and verified successfully!")
                    else:
                        self.finished_install.emit(False, "FFmpeg installed but verification failed. You may need to restart the application.")
                except Exception:
                    self.finished_install.emit(False, "FFmpeg installed but verification failed. You may need to restart the application.")
            else:
                self.finished_install.emit(False, "FFmpeg installation failed. Please try manual installation.")
                
        except Exception as e:
            self.finished_install.emit(False, f"Installation error: {str(e)}")


class FFmpegWorker(QThread):
    """Worker thread for FFmpeg operations"""
    progress_update = pyqtSignal(int)
    log_update = pyqtSignal(str)
    status_update = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, command: List[str], total_duration: float = 0):
        super().__init__()
        self.command = command
        self.total_duration = total_duration
        self.process = None
        self.should_stop = False
        
    def run(self):
        try:
            self.status_update.emit("Starting FFmpeg process...")
            self.log_update.emit(f"Command: {' '.join(self.command)}\n")
            
            self.process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            current_time = 0
            for line in iter(self.process.stdout.readline, ''):
                if self.should_stop:
                    self.process.terminate()
                    break
                    
                if not line:
                    break
                    
                self.log_update.emit(line)
                
                # Parse progress from FFmpeg output
                if self.total_duration > 0:
                    time_match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', line)
                    if time_match:
                        hours, minutes, seconds = time_match.groups()
                        current_time = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
                        progress = min(int((current_time / self.total_duration) * 100), 100)
                        self.progress_update.emit(progress)
            
            self.process.wait()
            
            if self.should_stop:
                self.status_update.emit("Process stopped by user")
                self.finished.emit(False, "Stopped by user")
            elif self.process.returncode == 0:
                self.progress_update.emit(100)
                self.status_update.emit("Task completed successfully!")
                self.finished.emit(True, "Success")
            else:
                self.status_update.emit("Task failed!")
                self.finished.emit(False, "FFmpeg process failed")
                
        except Exception as e:
            self.status_update.emit(f"Error: {str(e)}")
            self.finished.emit(False, str(e))
    
    def stop(self):
        """Stop the FFmpeg process"""
        self.should_stop = True
        if self.process:
            try:
                self.process.terminate()
                # Give it a moment to terminate gracefully
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't terminate
                self.process.kill()


class BatchProcessor(QThread):
    """Thread for batch processing multiple commands"""
    progress_update = pyqtSignal(int)
    log_update = pyqtSignal(str)
    status_update = pyqtSignal(str)
    finished = pyqtSignal(bool)
    
    def __init__(self, commands: List[str]):
        super().__init__()
        self.commands = commands
        self.should_stop = False
    
    def run(self):
        total_commands = len(self.commands)
        
        for i, cmd_str in enumerate(self.commands):
            if self.should_stop:
                break
                
            self.status_update.emit(f"Processing command {i+1} of {total_commands}")
            self.log_update.emit(f"\n{'='*50}\nCommand {i+1}: {cmd_str}\n{'='*50}\n")
            
            try:
                cmd = ["ffmpeg", "-y"] + shlex.split(cmd_str)
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    universal_newlines=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
                
                for line in iter(process.stdout.readline, ''):
                    if self.should_stop:
                        process.terminate()
                        break
                    self.log_update.emit(line)
                
                process.wait()
                
                if process.returncode == 0:
                    self.log_update.emit(f"Command {i+1} completed successfully!\n")
                else:
                    self.log_update.emit(f"Command {i+1} failed!\n")
                
                # Update progress
                progress = int(((i + 1) / total_commands) * 100)
                self.progress_update.emit(progress)
                
            except Exception as e:
                self.log_update.emit(f"Error in command {i+1}: {str(e)}\n")
        
        if not self.should_stop:
            self.status_update.emit("Batch processing completed!")
        else:
            self.status_update.emit("Batch processing stopped")
        
        self.finished.emit(True)
    
    def stop(self):
        """Stop batch processing"""
        self.should_stop = True


def get_video_info(file_path: str) -> Dict[str, Any]:
    """Get video file information using ffprobe"""
    try:
        result = subprocess.run([
            "ffprobe", "-v", "quiet", "-print_format", "json", 
            "-show_format", "-show_streams", file_path
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception as e:
        print(f"Error getting video info: {e}")
    
    return {}


def get_video_duration(file_path: str) -> float:
    """Get video duration in seconds"""
    try:
        result = subprocess.run([
            "ffprobe", "-v", "quiet", "-print_format", "json", 
            "-show_format", file_path
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            duration = float(data["format"]["duration"])
            return duration
    except Exception as e:
        print(f"Error getting duration: {e}")
    
    return 0.0


def format_file_info(info: Dict[str, Any]) -> str:
    """Format file information for display"""
    if not info:
        return "Unable to read file information"
    
    try:
        format_info = info.get("format", {})
        streams = info.get("streams", [])
        
        # Basic file info
        text_parts = []
        
        # File format
        format_name = format_info.get("format_name", "Unknown")
        file_size = int(format_info.get("size", 0))
        duration = float(format_info.get("duration", 0))
        
        text_parts.append(f"Format: {format_name.upper()}")
        text_parts.append(f"Size: {file_size / (1024*1024):.1f} MB")
        text_parts.append(f"Duration: {int(duration//3600):02d}:{int((duration%3600)//60):02d}:{int(duration%60):02d}")
        
        # Video stream info
        video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
        if video_stream:
            width = video_stream.get("width", 0)
            height = video_stream.get("height", 0)
            codec = video_stream.get("codec_name", "Unknown")
            fps_str = video_stream.get("r_frame_rate", "0/1")
            try:
                fps = eval(fps_str) if fps_str != "0/1" else 0
                text_parts.append(f"Video: {codec.upper()} {width}x{height} @ {fps:.1f} FPS")
            except:
                text_parts.append(f"Video: {codec.upper()} {width}x{height}")
        
        # Audio stream info
        audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)
        if audio_stream:
            codec = audio_stream.get("codec_name", "Unknown")
            sample_rate = audio_stream.get("sample_rate", 0)
            channels = audio_stream.get("channels", 0)
            text_parts.append(f"Audio: {codec.upper()} {sample_rate}Hz {channels}ch")
        
        return "\n".join(text_parts)
        
    except Exception as e:
        return f"Error parsing file information: {str(e)}"