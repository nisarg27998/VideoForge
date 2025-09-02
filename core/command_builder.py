"""
FFmpeg Command Builder
Constructs FFmpeg commands based on user settings
"""

import os
import shlex
from pathlib import Path
from typing import List, Dict, Any, Optional


class CommandBuilder:
    """Builds FFmpeg commands for different operations"""
    
    def __init__(self):
        self.base_command = ["ffmpeg", "-y"]  # -y to overwrite output files
    
    def build_convert_command(self, input_file: str, output_file: str, 
                            video_codec: str = "libx264", audio_codec: str = "aac",
                            additional_options: Dict[str, Any] = None) -> List[str]:
        """Build command for format conversion"""
        cmd = self.base_command.copy()
        cmd.extend(["-i", input_file])
        
        # Video codec
        if video_codec != "copy":
            cmd.extend(["-c:v", video_codec])
        else:
            cmd.extend(["-c:v", "copy"])
        
        # Audio codec
        if audio_codec != "copy":
            cmd.extend(["-c:a", audio_codec])
        else:
            cmd.extend(["-c:a", "copy"])
        
        # Additional options
        if additional_options:
            if "crf" in additional_options:
                cmd.extend(["-crf", str(additional_options["crf"])])
            if "preset" in additional_options:
                cmd.extend(["-preset", additional_options["preset"]])
            if "scale" in additional_options:
                cmd.extend(["-vf", f"scale={additional_options['scale']}"])
        
        cmd.append(output_file)
        return cmd
    
    def build_audio_extract_command(self, input_file: str, output_file: str,
                                  audio_format: str = "mp3", bitrate: str = "192k") -> List[str]:
        """Build command for audio extraction"""
        cmd = self.base_command.copy()
        cmd.extend(["-i", input_file])
        
        # No video stream
        cmd.append("-vn")
        
        # Audio codec based on format
        codec_map = {
            "mp3": "libmp3lame",
            "aac": "aac",
            "wav": "pcm_s16le", 
            "flac": "flac",
            "ogg": "libvorbis"
        }
        
        if audio_format in codec_map:
            cmd.extend(["-c:a", codec_map[audio_format]])
        
        # Set bitrate (except for lossless formats)
        if audio_format not in ["wav", "flac"]:
            cmd.extend(["-b:a", bitrate])
        
        cmd.append(output_file)
        return cmd
    
    def build_compress_command(self, input_file: str, output_file: str,
                             crf: int = 23, preset: str = "medium", 
                             scale: Optional[str] = None) -> List[str]:
        """Build command for video compression"""
        cmd = self.base_command.copy()
        cmd.extend(["-i", input_file])
        
        # Video encoding settings
        cmd.extend(["-c:v", "libx264"])
        cmd.extend(["-crf", str(crf)])
        cmd.extend(["-preset", preset])
        
        # Audio encoding
        cmd.extend(["-c:a", "aac"])
        cmd.extend(["-b:a", "128k"])
        
        # Scaling if specified
        if scale and scale != "Original":
            scale_map = {
                "1080p": "1920:1080",
                "720p": "1280:720", 
                "480p": "854:480",
                "360p": "640:360"
            }
            if scale in scale_map:
                cmd.extend(["-vf", f"scale={scale_map[scale]}"])
        
        cmd.append(output_file)
        return cmd
    
    def build_trim_command(self, input_file: str, output_file: str,
                          start_time: str = None, end_time: str = None,
                          duration: str = None) -> List[str]:
        """Build command for video trimming"""
        cmd = self.base_command.copy()
        
        # Add start time before input for seeking
        if start_time and start_time != "00:00:00":
            cmd.extend(["-ss", start_time])
        
        cmd.extend(["-i", input_file])
        
        # Add duration or end time
        if duration and duration != "00:00:00":
            cmd.extend(["-t", duration])
        elif end_time and end_time != "00:00:00":
            cmd.extend(["-to", end_time])
        
        # Copy streams for speed (no re-encoding)
        cmd.extend(["-c", "copy"])
        
        cmd.append(output_file)
        return cmd
    
    def build_merge_command(self, input_files: List[str], output_file: str,
                           method: str = "concat", output_codec: str = "libx264") -> List[str]:
        """Build command for video merging"""
        
        if method == "fast" or "Fast Concat" in method:
            # Fast concatenation (same codecs)
            return self._build_fast_concat_command(input_files, output_file)
        else:
            # Re-encode concatenation (different codecs)
            return self._build_reencode_concat_command(input_files, output_file, output_codec)
    
    def _build_fast_concat_command(self, input_files: List[str], output_file: str) -> List[str]:
        """Build fast concatenation command using concat demuxer"""
        # Create temporary concat file
        concat_file = "temp_concat_list.txt"
        
        try:
            with open(concat_file, 'w', encoding='utf-8') as f:
                for file_path in input_files:
                    # Use forward slashes and escape path
                    safe_path = file_path.replace('\\', '/').replace("'", "\\'")
                    f.write(f"file '{safe_path}'\n")
        except Exception as e:
            print(f"Error creating concat file: {e}")
            # Fallback to re-encode method
            return self._build_reencode_concat_command(input_files, output_file, "libx264")
        
        cmd = self.base_command.copy()
        cmd.extend(["-f", "concat", "-safe", "0", "-i", concat_file])
        cmd.extend(["-c", "copy"])
        cmd.append(output_file)
        
        return cmd
    
    def _build_reencode_concat_command(self, input_files: List[str], 
                                     output_file: str, output_codec: str) -> List[str]:
        """Build re-encoding concatenation command using filter_complex"""
        cmd = self.base_command.copy()
        
        # Add all input files
        for file_path in input_files:
            cmd.extend(["-i", file_path])
        
        # Build filter complex for concatenation
        filter_parts = []
        for i in range(len(input_files)):
            filter_parts.append(f"[{i}:v][{i}:a]")
        
        filter_str = "".join(filter_parts) + f"concat=n={len(input_files)}:v=1:a=1[outv][outa]"
        
        cmd.extend(["-filter_complex", filter_str])
        cmd.extend(["-map", "[outv]", "-map", "[outa]"])
        
        # Output codec
        if output_codec != "copy":
            cmd.extend(["-c:v", output_codec])
            cmd.extend(["-c:a", "aac"])
        
        cmd.append(output_file)
        return cmd
    
    def build_custom_command(self, custom_args: str) -> List[str]:
        """Build command from custom arguments"""
        try:
            # Parse custom arguments safely
            args = shlex.split(custom_args)
            cmd = ["ffmpeg"] + args
            return cmd
        except Exception as e:
            raise ValueError(f"Invalid command syntax: {str(e)}")
    
    def add_optimization_flags(self, cmd: List[str], optimize_web: bool = True,
                              preserve_metadata: bool = True) -> List[str]:
        """Add optimization flags to command"""
        if optimize_web:
            # Add web optimization flags
            if "-c:v" in cmd and "libx264" in cmd:
                # Add after video codec
                video_idx = cmd.index("libx264") 
                cmd.insert(video_idx + 1, "-movflags")
                cmd.insert(video_idx + 2, "+faststart")
        
        if not preserve_metadata:
            # Strip metadata
            cmd.extend(["-map_metadata", "-1"])
        
        return cmd
    
    def validate_command(self, cmd: List[str]) -> tuple[bool, str]:
        """Validate FFmpeg command"""
        if not cmd or cmd[0] != "ffmpeg":
            return False, "Command must start with 'ffmpeg'"
        
        # Check for input files
        if "-i" not in cmd:
            return False, "No input files specified"
        
        # Check for output file
        if len(cmd) < 3:
            return False, "No output file specified"
        
        # Basic validation passed
        return True, "Command is valid"
    
    def get_estimated_duration(self, input_files: List[str]) -> float:
        """Estimate total duration for progress tracking"""
        total_duration = 0.0
        
        for file_path in input_files:
            if os.path.exists(file_path):
                try:
                    from .ffmpeg_manager import get_video_duration
                    duration = get_video_duration(file_path)
                    total_duration += duration
                except Exception:
                    pass
        
        return total_duration


class PresetManager:
    """Manages encoding presets"""
    
    def __init__(self):
        self.presets = {
            "YouTube Upload": {
                "format": "mp4",
                "video_codec": "libx264",
                "audio_codec": "aac",
                "crf": 23,
                "preset": "medium",
                "optimize_web": True
            },
            "WhatsApp Share": {
                "format": "mp4", 
                "video_codec": "libx264",
                "audio_codec": "aac",
                "crf": 28,
                "preset": "fast",
                "scale": "720p",
                "optimize_web": True
            },
            "High Quality": {
                "format": "mp4",
                "video_codec": "libx264", 
                "audio_codec": "aac",
                "crf": 18,
                "preset": "slow",
                "optimize_web": True
            },
            "Small File Size": {
                "format": "mp4",
                "video_codec": "libx264",
                "audio_codec": "aac", 
                "crf": 32,
                "preset": "fast",
                "scale": "480p",
                "optimize_web": True
            },
            "Archive Quality": {
                "format": "mkv",
                "video_codec": "libx265",
                "audio_codec": "flac",
                "crf": 16,
                "preset": "slow",
                "optimize_web": False
            }
        }
    
    def get_preset(self, name: str) -> Dict[str, Any]:
        """Get preset configuration"""
        return self.presets.get(name, {})
    
    def get_preset_names(self) -> List[str]:
        """Get list of available preset names"""
        return list(self.presets.keys())
    
    def apply_preset_to_command(self, preset_name: str, base_cmd: List[str]) -> List[str]:
        """Apply preset settings to a base command"""
        preset = self.get_preset(preset_name)
        if not preset:
            return base_cmd
        
        # This would modify the command based on preset settings
        # Implementation depends on the specific command structure
        return base_cmd