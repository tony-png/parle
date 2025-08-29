import os
import requests
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class AudioTranscriber:
    def __init__(self):
        self.api_key = os.getenv('DEEPINFRA_API_KEY')
        if not self.api_key:
            raise ValueError("DEEPINFRA_API_KEY not found in environment variables")
        
        self.api_url = "https://api.deepinfra.com/v1/audio/transcriptions"
        
    def transcribe(self, audio_path: Path) -> Optional[str]:
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        with open(audio_path, 'rb') as audio_file:
            files = {
                'file': (audio_path.name, audio_file, 'audio/mpeg')
            }
            
            data = {
                'model': 'mistralai/Voxtral-Mini-3B-2507'
            }
            
            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get('text', '')
                else:
                    print(f"Transcription failed: {response.status_code} - {response.text}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                print(f"Error during transcription: {e}")
                return None