# Parle

A CLI tool to record microphone input, save as MP3, and play it back.

## Prerequisites

1. **FFmpeg**: Required for MP3 conversion and playback
   - Download from: https://ffmpeg.org/download.html
   - Make sure it's in your PATH

2. **UV**: Python package manager
   - Install: `pip install uv`

3. **Deepinfra API Key** (optional, for transcription):
   - Create a `.env` file in the project root
   - Add: `DEEPINFRA_API_KEY=your_api_key_here`

## Installation

Install using UV:

```bash
uv pip install -e .
```

Note: You may need to install system dependencies for PyAudio:
- **Windows**: PyAudio should install directly
- **macOS**: `brew install portaudio`
- **Linux**: `sudo apt-get install portaudio19-dev` (Ubuntu/Debian)

## Usage

All commands should be run with UV:

Basic recording:
```bash
uv run parle
```

Specify output file:
```bash
uv run parle -o my_recording.mp3
```

Skip playback:
```bash
uv run parle --no-playback
```

Custom bitrate:
```bash
uv run parle -b 320k
```

Keep WAV file:
```bash
uv run parle --keep-wav
```

### Transcription

Record and transcribe audio using Deepinfra's Voxtral model:
```bash
uv run parle --transcribe
```

Transcribe with custom output:
```bash
uv run parle -o meeting.mp3 --transcribe
```

### Test Different Bitrates

Test mode records once and converts to multiple bitrates (8k, 16k, 32k, 64k, 96k, 128k, 192k, 256k, 320k) so you can compare quality:

```bash
uv run parle --test-bitrates
```

This will:
1. Record your audio once
2. Convert to 9 different bitrates
3. Play each version sequentially (press Enter between each)
4. Save all versions as `test_TIMESTAMP_BITRATE.mp3`

Great for finding the lowest acceptable bitrate for your use case!

## Commands

- Start recording: Run `uv run parle`
- Stop recording: Press Enter
- The tool will automatically convert to MP3 and play back the recording