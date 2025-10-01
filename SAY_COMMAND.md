# SAY Command - Text-to-Speech for WSA Terminal

## Overview

The SAY command brings authentic Amiga text-to-speech functionality to WSA Terminal, just like the original AmigaOS SAY command. It supports multiple TTS engines and voice customization.

## Usage

### Basic Commands

1. **Speak text:**

   ```
   SYS:> say "Hello from Amiga"
   ```

2. **Speak with custom rate:**

   ```
   SYS:> say "Welcome to WSA Terminal" RATE=150
   ```

3. **Speak with specific voice:**

   ```
   SYS:> say "Greetings" VOICE=female
   ```

4. **List available voices:**

   ```
   SYS:> say voices
   ```

5. **Get help:**
   ```
   SYS:> help say
   ```

### Parameters

- **RATE=n** - Speech rate in words per minute (50-400)
- **VOICE=name** - Voice selection (male, female, robot, amiga, or specific voice name)

### Examples

```
C:> say "The Amiga lives on in WSA Terminal"
C:> say "Computing at light speed" RATE=200 VOICE=robot
C:> say "Boing!" VOICE=amiga
```

## Supported TTS Engines

WSA Terminal automatically detects and uses available TTS engines:

### Windows (SAPI)

- **Built-in voices** on Windows systems
- **High quality** speech synthesis
- **Multiple voice options** (if installed)

### eSpeak (Cross-platform)

- **Lightweight** and fast
- **Multiple languages** supported
- **Robotic/retro sound** perfect for Amiga nostalgia
- Install: `sudo apt install espeak espeak-data` (Linux/WSL)

### Festival (Linux)

- **Natural sounding** speech
- **Classic Unix** TTS engine
- Install: `sudo apt install festival` (Linux)

### macOS Say

- **Native macOS** speech synthesis
- **High quality voices** built-in

### pyttsx3 (Python)

- **Cross-platform** Python library
- **Fallback option** when system TTS unavailable
- Install: `pip install pyttsx3`

## Voice Options

### Predefined Voice Names

- **male** - Male voice (default)
- **female** - Female voice
- **robot** - Robotic/synthesized voice
- **amiga** - Retro computer-style voice

### System-Specific Voices

Use `SAY VOICES` to list all available voices on your system.

## Installation

### Linux/WSL

```bash
# Install eSpeak (recommended)
sudo apt update
sudo apt install espeak espeak-data

# Alternative: Install Festival
sudo apt install festival

# Python option
pip install pyttsx3
```

### Windows

- **Built-in SAPI** voices work automatically
- Optional: Install additional SAPI voices
- Optional: `pip install pyttsx3` for Python TTS

### macOS

- **Built-in voices** work automatically
- Optional: `pip install pyttsx3` for Python TTS

## Amiga Authenticity

The SAY command recreates the classic Amiga experience:

- **Same syntax** as original AmigaOS SAY command
- **Rate control** like the original Amiga speech synthesizer
- **Voice selection** similar to Amiga narrator.device
- **Retro speech quality** with eSpeak's robotic voices

## Examples Session

```
SYS:> C:
C:> say voices
Available Text-to-Speech Voices:
===================================
eSpeak Voices:
  english (en)
  spanish (es)
  french (fr)
  german (de)
  italian (it)

C:> say "Welcome to the Amiga experience"
Speaking: "Welcome to the Amiga experience"

C:> say "Boing! Boing!" VOICE=robot RATE=120
Speaking: "Boing! Boing!"

C:> say "The future was created here" VOICE=amiga
Speaking: "The future was created here"
```

## Integration

The SAY command is fully integrated into WSA Terminal:

- **Available in C:** directory alongside other commands
- **Tab completion** support
- **Help system** integration
- **Error handling** with helpful installation messages
- **Background execution** - continue using terminal while speaking

## Troubleshooting

### "Text-to-speech not available"

1. Install eSpeak: `sudo apt install espeak espeak-data`
2. Or install Festival: `sudo apt install festival`
3. Or install Python TTS: `pip install pyttsx3`

### No audio in WSL

- eSpeak may not have audio output in WSL environment
- Try Windows host TTS or run from Windows terminal
- Consider using Windows SAPI voices for actual audio

### Voice not found

- Use `SAY VOICES` to see available voices
- Check voice name spelling
- Try predefined names: male, female, robot, amiga

## Technical Notes

The SAY command:

- **Auto-detects** available TTS engines
- **Falls back** through multiple engines if needed
- **Handles quotes** in text properly
- **Validates parameters** (rate limits, voice names)
- **Cross-platform** - works on Windows, Linux, macOS
- **Authentic syntax** matching original Amiga SAY command
