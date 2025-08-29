import click
import threading
import sys
from pathlib import Path
from datetime import datetime
import pyaudio

from .recorder import AudioRecorder
from .converter import AudioConverter
from .player import AudioPlayer
from .transcriber import AudioTranscriber


@click.command()
@click.option('--output', '-o', type=click.Path(), help='Output MP3 file path')
@click.option('--bitrate', '-b', default='16k', help='MP3 bitrate (default: 16k)')
@click.option('--no-playback', is_flag=True, help='Skip automatic playback after recording')
@click.option('--keep-wav', is_flag=True, help='Keep the temporary WAV file')
@click.option('--test-bitrates', is_flag=True, help='Test multiple bitrates (8k to 320k) to compare quality')
@click.option('--transcribe', is_flag=True, help='Transcribe the audio using Deepinfra Voxtral API')
def main(output, bitrate, no_playback, keep_wav, test_bitrates, transcribe):
    """Record microphone input, save as MP3, and play it back."""
    
    if test_bitrates:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"test_{timestamp}"
    elif output:
        output_path = Path(output)
        if not output_path.suffix:
            output_path = output_path.with_suffix('.mp3')
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(f"recording_{timestamp}.mp3")
    
    recorder = AudioRecorder()
    
    try:
        if transcribe:
            print("Recording... Press Enter to stop.")
        else:
            recorder.start_recording()
        
        recording = True
        def record_audio():
            while recording:
                recorder.record_chunk()
        
        if transcribe:
            recorder.frames = []
            recorder.stream = recorder.audio.open(
                format=pyaudio.paInt16,
                channels=recorder.channels,
                rate=recorder.sample_rate,
                input=True,
                frames_per_buffer=recorder.chunk_size
            )
        
        record_thread = threading.Thread(target=record_audio)
        record_thread.start()
        
        input()
        
        recording = False
        record_thread.join()
        
        if not transcribe:
            print("Stopping recording...")
        wav_path = recorder.stop_recording()
        
        if wav_path:
            if test_bitrates:
                test_bitrate_list = ['8k', '16k', '32k', '64k', '96k', '128k', '192k', '256k', '320k']
                print(f"\nTesting {len(test_bitrate_list)} different bitrates...")
                
                mp3_files = []
                for test_bitrate in test_bitrate_list:
                    output_path = Path(f"{base_name}_{test_bitrate}.mp3")
                    print(f"Converting to {test_bitrate}: {output_path}")
                    mp3_path = AudioConverter.wav_to_mp3(wav_path, output_path, test_bitrate)
                    mp3_files.append((test_bitrate, mp3_path))
                
                if not no_playback:
                    print("\n=== Playing all bitrates for comparison ===")
                    for test_bitrate, mp3_path in mp3_files:
                        print(f"\n>>> Bitrate: {test_bitrate}")
                        AudioPlayer.play_mp3(mp3_path)
                        if test_bitrate != test_bitrate_list[-1]:
                            input("Press Enter to continue to next bitrate...")
                
                print(f"\nAll test files saved with prefix: {base_name}_*.mp3")
                
                if not keep_wav:
                    AudioConverter.cleanup_temp_file(wav_path)
            else:
                if not transcribe:
                    print(f"Converting to MP3: {output_path}")
                mp3_path = AudioConverter.wav_to_mp3(wav_path, output_path, bitrate)
                
                if not keep_wav:
                    AudioConverter.cleanup_temp_file(wav_path)
                    
                if not transcribe:
                    print(f"Recording saved to: {mp3_path}")
                
                if transcribe:
                    try:
                        transcriber = AudioTranscriber()
                        transcription = transcriber.transcribe(mp3_path)
                        if transcription:
                            print(transcription)
                        else:
                            print("Transcription failed or returned empty.")
                    except Exception as e:
                        print(f"Transcription error: {e}")
                elif not no_playback:
                    print("\nPlaying back the recording...")
                    AudioPlayer.play_mp3(mp3_path)
        else:
            print("No audio recorded.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nRecording cancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        recorder.cleanup()


if __name__ == "__main__":
    main()