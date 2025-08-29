import soundfile as sf
import numpy as np
from pathlib import Path
import pyaudio
import wave


class AudioPlayer:
    @staticmethod
    def play_mp3(mp3_path: Path):
        if not mp3_path.exists():
            raise FileNotFoundError(f"MP3 file not found: {mp3_path}")
            
        print(f"Playing: {mp3_path.name}")
        print("Note: Direct MP3 playback requires conversion to WAV first")
        
        temp_wav = mp3_path.with_suffix('.temp.wav')
        
        import subprocess
        result = subprocess.run([
            "ffmpeg", "-i", str(mp3_path), 
            "-y", str(temp_wav)
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Could not convert MP3 for playback: {result.stderr}")
        
        try:
            AudioPlayer._play_with_pyaudio(temp_wav)
        finally:
            if temp_wav.exists():
                temp_wav.unlink()
        
        print("Playback finished.")
        
    @staticmethod
    def play_wav(wav_path: Path):
        if not wav_path.exists():
            raise FileNotFoundError(f"WAV file not found: {wav_path}")
            
        print(f"Playing: {wav_path.name}")
        AudioPlayer._play_with_pyaudio(wav_path)
        print("Playback finished.")
    
    @staticmethod
    def _play_with_pyaudio(wav_path: Path):
        wf = wave.open(str(wav_path), 'rb')
        
        p = pyaudio.PyAudio()
        
        stream = p.open(
            format=p.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True
        )
        
        chunk_size = 1024
        data = wf.readframes(chunk_size)
        
        while data:
            stream.write(data)
            data = wf.readframes(chunk_size)
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        wf.close()