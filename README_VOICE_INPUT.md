# 🎤 Parle Voice Input - System-Wide Voice Transcription for Windows

A Windows system tray application that provides voice-to-text functionality in ANY text field across your entire system. Press a hotkey, speak, and your words are instantly transcribed and pasted wherever your cursor is.

## ✨ Features

### 🎯 **Universal Voice Input**
- Works in **ANY** text field - browsers, Word, VS Code, chat apps, notepad, etc.
- Global hotkey triggers recording (default: `Ctrl+Shift+R`)
- Auto-transcribes and pastes text directly where your cursor is
- No need to switch windows or copy/paste manually

### 🔊 **Audio Feedback**
- **High beep** (1000Hz) when recording starts
- **Low beep** (600Hz) when recording stops
- Visual indicator in system tray (blue = idle, red = recording)

### ⚙️ **Customization**
- **Change hotkey** through GUI dialog
- **Language selection** for transcription
- **Auto-start** with Windows option
- **Configurable** beeps and notifications

## 🚀 Quick Start

### Prerequisites
1. **Deepinfra API Key** for transcription
   - Get one at: https://deepinfra.com
   - Create `.env` file in project root:
   ```
   DEEPINFRA_API_KEY=your_api_key_here
   ```

2. **FFmpeg** (already installed if you have the base Parle app)

### Installation
```bash
# Install with UV (if not already done)
uv pip install -e .
```

### Running the Voice Input System

#### Method 1: System Tray App (Recommended)
```bash
uv run parle-tray
```
Or double-click `start-voice-input.bat`

#### Method 2: Configure Hotkey
```bash
uv run parle-config
```

## 📖 How to Use

1. **Start the tray app** - A microphone icon appears in your system tray
2. **Click in any text field** where you want to type
3. **Press your hotkey** (default: `Ctrl+Shift+R`)
4. **Hear high beep** - Start speaking
5. **Press hotkey again** to stop
6. **Hear low beep** - Text automatically appears in your field!

## 🎛️ System Tray Menu

Right-click the microphone icon for:
- **Start/Stop Recording** - Manual trigger without hotkey
- **Start with Windows** - Toggle auto-start on boot
- **Change Hotkey** - Opens GUI to set custom hotkey
- **Help** - Shows current hotkey reminder
- **Quit** - Exits the application

## ⚙️ Configuration

Settings are stored in `~/.parle/config.json`:

```json
{
  "hotkey": "ctrl+shift+r",      // Your recording hotkey
  "language": "en",               // Transcription language
  "start_on_boot": false,         // Auto-start with Windows
  "show_notifications": true,     // Show Windows notifications
  "beep_on_start": true,         // Beep when recording starts
  "beep_on_stop": true           // Beep when recording stops
}
```

### Supported Languages
- `en` - English
- `fr` - French  
- `es` - Spanish
- `de` - German
- (and many more via Deepinfra)

## 🔧 Changing the Hotkey

### Via GUI (Easy)
1. Right-click tray icon → "Change Hotkey"
2. Click "Record Hotkey"
3. Press your desired key combination
4. Click "Save"
5. Restart the app

### Via Config File
1. Edit `~/.parle/config.json`
2. Change `"hotkey": "ctrl+shift+r"` to your preference
3. Examples: `"ctrl+alt+v"`, `"win+shift+s"`, `"ctrl+space"`
4. Restart the app

## 🚦 Auto-Start with Windows

### Enable via Tray Menu
1. Right-click tray icon
2. Click "Start with Windows"
3. See ✓ checkmark when enabled

### Manual Registry Method
The app adds an entry to:
```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
```

## 🎤 Transcription Engine

Uses **Deepinfra's Whisper Large V3 Turbo** model:
- Fast, accurate transcription
- Supports 100+ languages
- Automatic punctuation
- Low latency (~1-2 seconds)

## 📁 Project Structure

```
parle/
├── parle/
│   ├── tray.py           # System tray application
│   ├── hotkey_dialog.py  # GUI for hotkey configuration
│   ├── config.py         # Configuration management
│   ├── transcriber.py    # Deepinfra transcription
│   ├── recorder.py       # Audio recording
│   └── converter.py      # Audio format conversion
├── start-voice-input.bat  # Windows launcher
├── parle-startup.vbs     # Silent startup script
└── .env                  # API keys (create this)
```

## 🐛 Troubleshooting

### Hotkey not working
- Run command prompt as Administrator
- Check if another app is using the same hotkey
- Try a different combination

### No transcription
- Check your Deepinfra API key in `.env`
- Ensure microphone permissions are granted
- Check internet connection

### No beep sounds
- Some systems may not support `winsound.Beep`
- Check Windows sound settings

### App won't start with Windows
- Manually add `parle-startup.vbs` to Windows Startup folder
- Or use Task Scheduler for more control

## 🔒 Privacy & Security

- Audio is processed via Deepinfra API (encrypted in transit)
- No audio is stored locally after transcription
- Temporary files are immediately deleted
- API key stored locally in `.env`

## 💡 Tips & Tricks

1. **Quick notes**: Use in Notepad for rapid note-taking
2. **Coding**: Great for code comments and documentation
3. **Chat**: Perfect for long messages in chat apps
4. **Accessibility**: Helpful for users with typing difficulties
5. **Multiple languages**: Change language in config for multilingual support

## 🛠️ Advanced Usage

### Running without system tray
For direct transcription to clipboard:
```bash
uv run parle --transcribe --no-playback
```

### Custom scripts
Create AutoHotkey scripts that call:
```bash
uv run parle --transcribe --language es > output.txt
```

## 📝 License

This project extends the Parle audio recording tool with system-wide voice input capabilities.

---

**Enjoy hands-free typing anywhere on Windows! 🎉**