import pyaudio
import wave
import numpy as np
from pathlib import Path
from typing import Optional
import tempfile


class AudioRecorder:
    def __init__(self, sample_rate: int = 44100, channels: int = 1, chunk_size: int = 1024):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        
    def start_recording(self):
        self.frames = []
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        print("Recording started... Press Enter to stop.")
        
    def record_chunk(self) -> bool:
        if self.stream:
            try:
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                self.frames.append(data)
                return True
            except Exception:
                return False
        return False
        
    def stop_recording(self) -> Optional[Path]:
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            
            if not self.frames:
                return None
                
            temp_wav = Path(tempfile.mktemp(suffix=".wav"))
            
            with wave.open(str(temp_wav), 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(self.frames))
                
            return temp_wav
        return None
        
    def cleanup(self):
        if self.stream:
            self.stream.close()
        self.audio.terminate()