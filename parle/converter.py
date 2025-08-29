import soundfile as sf
import numpy as np
from scipy.io import wavfile
from pathlib import Path
from typing import Optional
import subprocess
import sys


class AudioConverter:
    @staticmethod
    def wav_to_mp3(wav_path: Path, output_path: Optional[Path] = None, bitrate: str = "192k") -> Path:
        if not wav_path.exists():
            raise FileNotFoundError(f"WAV file not found: {wav_path}")
            
        if output_path is None:
            output_path = wav_path.with_suffix(".mp3")
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "show", "ffmpeg-python"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                import ffmpeg
                ffmpeg.input(str(wav_path)).output(
                    str(output_path), 
                    audio_bitrate=bitrate
                ).overwrite_output().run(quiet=True)
            else:
                result = subprocess.run([
                    "ffmpeg", "-i", str(wav_path), 
                    "-b:a", bitrate, 
                    "-y", str(output_path)
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    raise RuntimeError(f"FFmpeg conversion failed. Please install FFmpeg: {result.stderr}")
        except FileNotFoundError:
            raise RuntimeError("FFmpeg not found. Please install FFmpeg and ensure it's in your PATH")
        except Exception as e:
            raise RuntimeError(f"Audio conversion failed: {e}")
            
        return output_path
        
    @staticmethod
    def cleanup_temp_file(file_path: Path):
        if file_path.exists() and ("temp" in str(file_path).lower() or "tmp" in str(file_path).lower()):
            try:
                file_path.unlink()
            except Exception:
                pass