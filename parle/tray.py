import sys
import threading
import queue
import time
import winsound
import winreg
import os
import subprocess
from pathlib import Path
from datetime import datetime
import pyaudio
import pyperclip
import keyboard
import pystray
from PIL import Image, ImageDraw
from plyer import notification

from .recorder import AudioRecorder
from .converter import AudioConverter
from .transcriber import AudioTranscriber
from .config import Config


class VoiceInputTray:
    def __init__(self):
        self.recording = False
        self.recorder = None
        self.config = Config()
        self.transcriber = AudioTranscriber(language=self.config.get('language', 'en'))
        self.audio_queue = queue.Queue()
        self.icon = None
        self.last_hotkey_time = 0
        self.current_hotkey = None
        
    def create_icon_image(self, recording=False):
        """Create a simple microphone icon"""
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Microphone shape
        color = (255, 0, 0, 255) if recording else (0, 128, 255, 255)
        
        # Mic body
        draw.ellipse([20, 10, 44, 40], fill=color)
        draw.rectangle([20, 25, 44, 40], fill=color)
        
        # Mic stand
        draw.rectangle([30, 40, 34, 50], fill=color)
        draw.rectangle([24, 50, 40, 54], fill=color)
        
        if recording:
            # Recording indicator
            draw.ellipse([48, 8, 56, 16], fill=(255, 0, 0, 255))
        
        return image
    
    def play_beep(self, frequency, duration):
        """Play a beep sound"""
        if not ((frequency == 1000 and self.config.get('beep_on_start', True)) or 
                (frequency == 600 and self.config.get('beep_on_stop', True))):
            return
        try:
            winsound.Beep(frequency, duration)
        except:
            # Fallback if beep doesn't work
            pass
    
    def start_recording(self):
        """Start recording audio"""
        if self.recording:
            return
            
        self.recording = True
        self.recorder = AudioRecorder()
        
        # Play start beep (higher pitch)
        threading.Thread(target=lambda: self.play_beep(1000, 200), daemon=True).start()
        
        # Update tray icon
        if self.icon:
            self.icon.icon = self.create_icon_image(recording=True)
        
        # Show notification
        notification.notify(
            title='Voice Input',
            message='Recording... Press Ctrl+Shift+R again to stop',
            timeout=2
        )
        
        # Start recording in background
        def record_audio():
            self.recorder.frames = []
            self.recorder.stream = self.recorder.audio.open(
                format=pyaudio.paInt16,
                channels=self.recorder.channels,
                rate=self.recorder.sample_rate,
                input=True,
                frames_per_buffer=self.recorder.chunk_size
            )
            
            while self.recording:
                try:
                    self.recorder.record_chunk()
                except Exception as e:
                    print(f"Recording error: {e}")
                    break
        
        self.record_thread = threading.Thread(target=record_audio, daemon=True)
        self.record_thread.start()
    
    def stop_recording_and_transcribe(self):
        """Stop recording and transcribe the audio"""
        if not self.recording:
            return
            
        self.recording = False
        
        # Play stop beep (lower pitch)
        threading.Thread(target=lambda: self.play_beep(600, 200), daemon=True).start()
        
        # Update tray icon
        if self.icon:
            self.icon.icon = self.create_icon_image(recording=False)
        
        # Stop recording
        wav_path = self.recorder.stop_recording()
        self.recorder.cleanup()
        
        if wav_path:
            notification.notify(
                title='Voice Input',
                message='Processing transcription...',
                timeout=2
            )
            
            # Convert to MP3
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            mp3_path = Path(f"temp_recording_{timestamp}.mp3")
            mp3_path = AudioConverter.wav_to_mp3(wav_path, mp3_path, '16k')
            AudioConverter.cleanup_temp_file(wav_path)
            
            # Transcribe
            try:
                transcription = self.transcriber.transcribe(mp3_path)
                
                if transcription:
                    # Copy to clipboard
                    pyperclip.copy(transcription)
                    
                    # Clean up temp file
                    mp3_path.unlink(missing_ok=True)
                    
                    # Paste to active window
                    time.sleep(0.1)  # Small delay to ensure focus
                    
                    # Simulate Ctrl+V
                    keyboard.press_and_release('ctrl+v')
                else:
                    notification.notify(
                        title='Voice Input Error',
                        message='Transcription failed',
                        timeout=3
                    )
            except Exception as e:
                notification.notify(
                    title='Voice Input Error',
                    message=f'Error: {str(e)}',
                    timeout=3
                )
                # Clean up temp file
                mp3_path.unlink(missing_ok=True)
    
    def on_hotkey(self):
        """Handle hotkey press"""
        # Prevent multiple triggers
        current_time = time.time()
        if current_time - self.last_hotkey_time < 0.5:
            return
        self.last_hotkey_time = current_time
        
        if self.recording:
            self.stop_recording_and_transcribe()
        else:
            self.start_recording()
    
    def quit_app(self, icon, item):
        """Quit the application"""
        if self.recording:
            self.recording = False
            if self.recorder:
                self.recorder.cleanup()
        icon.stop()
        sys.exit(0)
    
    def show_help(self, icon, item):
        """Show help notification"""
        hotkey = self.config.get('hotkey', 'ctrl+shift+r').upper().replace('+', ' + ')
        notification.notify(
            title='Voice Input Help',
            message=f'Press {hotkey} to start/stop recording\nTranscription will auto-paste to active field',
            timeout=5
        )
    
    def toggle_recording(self, icon, item):
        """Toggle recording from menu"""
        self.on_hotkey()
    
    def change_hotkey(self, icon, item):
        """Change the hotkey"""
        try:
            # Launch the config dialog as a separate process (without CREATE_NO_WINDOW for GUI)
            subprocess.Popen([sys.executable, "-m", "parle.hotkey_dialog"])
        except Exception as e:
            # Fallback to direct file edit instruction
            config_path = Path.home() / '.parle' / 'config.json'
            notification.notify(
                title='Change Hotkey',
                message=f'Edit the config file at:\n{config_path}\n\nThen restart the app',
                timeout=5
            )
    
    def toggle_startup(self, icon, item):
        """Toggle Windows startup"""
        startup_enabled = self.config.get('start_on_boot', False)
        
        # Registry key for current user startup
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "ParleVoiceInput"
        
        try:
            if not startup_enabled:
                # Enable startup
                exe_path = sys.executable
                if 'python' in exe_path.lower():
                    # Running from Python, create batch file path
                    startup_cmd = f'"{sys.executable}" -m parle.tray'
                else:
                    # Running from compiled exe
                    startup_cmd = f'"{exe_path}"'
                
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE)
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, startup_cmd)
                winreg.CloseKey(key)
                
                self.config.set('start_on_boot', True)
                notification.notify(
                    title='Startup Enabled',
                    message='Voice Input will start with Windows',
                    timeout=3
                )
            else:
                # Disable startup
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE)
                try:
                    winreg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    pass
                winreg.CloseKey(key)
                
                self.config.set('start_on_boot', False)
                notification.notify(
                    title='Startup Disabled',
                    message='Voice Input will not start with Windows',
                    timeout=3
                )
        except Exception as e:
            notification.notify(
                title='Error',
                message=f'Failed to modify startup: {str(e)}',
                timeout=3
            )
    
    def run(self):
        """Run the system tray application"""
        # Get hotkey from config
        hotkey = self.config.get('hotkey', 'ctrl+shift+r')
        hotkey_display = hotkey.upper().replace('+', ' + ')
        
        # Create dynamic menu
        def create_menu():
            startup_enabled = self.config.get('start_on_boot', False)
            startup_text = "✓ Start with Windows" if startup_enabled else "Start with Windows"
            
            return pystray.Menu(
                pystray.MenuItem(f"Voice Input - {hotkey_display}", lambda: None, enabled=False),
                pystray.MenuItem("Start/Stop Recording", self.toggle_recording),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem(startup_text, self.toggle_startup),
                pystray.MenuItem("Change Hotkey", self.change_hotkey),
                pystray.MenuItem("Help", self.show_help),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Quit", self.quit_app)
            )
        
        # Create system tray icon
        self.icon = pystray.Icon(
            "voice_input",
            self.create_icon_image(),
            f"Voice Input - Press {hotkey_display}",
            create_menu()
        )
        
        # Register hotkey using keyboard library
        self.current_hotkey = hotkey
        keyboard.add_hotkey(hotkey, self.on_hotkey, suppress=False)
        
        # Show initial notification only if configured
        if self.config.get('show_notifications', True):
            notification.notify(
                title='Voice Input Started',
                message=f'Press {hotkey_display} to record and transcribe',
                timeout=3
            )
        
        # Run the icon
        self.icon.run()


def main():
    """Main entry point for system tray app"""
    app = VoiceInputTray()
    app.run()


if __name__ == "__main__":
    main()