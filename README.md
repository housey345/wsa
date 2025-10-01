# WSA Terminal - Windows Subsystem for Amiga

🎯 **Relive the legendary Amiga computer experience on modern systems!**

WSA Terminal is a lovingly crafted Python implementation that recreates the authentic Amiga Workbench command-line interface, complete with classic commands, retro styling, and modern integration features. Whether you're a nostalgic Amiga enthusiast or curious about computing history, WSA Terminal brings the magic of AmigaOS to your Windows, Linux, or WSL environment.

> **⚠️ Development Status Notice**  
> This project is actively under development. While many features are functional, some commands may be partially implemented or not yet working as expected. This project is mainly vibe coded for fun but also to improve my knowledge of the Python programming language.

**_ ! THE CONSOLE VERSION IS BY FAR THE MOST UP TO DATE ! _**
**_ Try the web version if you like but it's nowhere near as complete. _**

## ✨ Core Features

### 🖥️ **Authentic Amiga Experience**

- **Genuine Amiga 3.1 shell interface** with period-accurate command behavior
- **Classic Amiga commands**: INFO, AVAIL, STATUS, MOUNT, ED, DIR, CD, PATTERN, DATE, ECHO, HELP
- **Amiga-style directory navigation** with device names (SYS:, RAM:, C:, DH0:)
- **Startup sequence execution** just like real AmigaOS boot scripts
- **Guru Meditation errors** for that authentic crash experience! 😄

### 🌐 **Dual Interface Options**

- **Web Version** (`wsa.py`) - Browser-based terminal with retro CRT effects and WebSocket real-time interaction
- **Console Version** (`wsa_console.py`) - Direct command-line interface for terminal purists

### 🔗 **Modern Integration**

- **Windows C: drive integration** - Your C: drive appears as DH0: with full file system access
- **WinUAE Integration** - Launch real Amiga emulator directly from the command line
- **SAY Command** - Text-to-speech synthesis just like original AmigaOS
- **PING utility** - Network connectivity testing with authentic output
- **Tab-based path autocomplete** - Modern convenience for navigation
- **Cross-platform compatibility** (Windows, Linux, WSL)

### 🎮 **Advanced Features**

- **Built-in ED text editor** with Amiga-style commands for file editing
- **Real file system support** for DH0: subdirectory navigation and listing
- **Pattern matching utility** with actual file system integration
- **Easter eggs** including classic Amiga references and ASCII art
- **Executable generation** with PyInstaller for standalone distribution

## 🛠️ System Requirements

- **Python 3.7 or higher**
- **aiohttp library** (for web version only)
- **psutil library** (optional, for enhanced system information in INFO command)

### Optional Integrations

- **WinUAE** (for WINUAE command integration)
- **espeak or festival** (for enhanced SAY command text-to-speech)
- **pyttsx3** (Python TTS library alternative)

## 🚀 Quick Start Installation

1. **Clone or download this repository**

   ```bash
   git clone https://github.com/housey345/wsa.git
   cd wsa
   ```

2. **Install required dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **For enhanced system information (optional)**

   ```bash
   pip install psutil
   ```

4. **Launch WSA Terminal**

   **Console Version (Recommended for first-time users):**

   ```bash
   # Windows
   wsa_console.bat

   # Linux/Mac/WSL
   python wsa_console.py
   ```

   **Web Version:**

   ```bash
   # Windows
   wsa.bat

   # Linux/Mac/WSL
   python wsa.py
   # Then open http://localhost:3000 in your browser
   ```

## Running the Terminal

### Web Version

#### On Windows

Double-click `wsa.bat` or run from command prompt:

```
wsa.bat
```

You can also specify a different port:

```
wsa.bat --port 8080
```

#### On Linux/Mac/WSL

```
python wsa.py
```

By default, the terminal will be available at http://localhost:3000

You can specify a different port:

```
python wsa.py --port 8080
```

### Console Version

#### On Windows

Double-click `wsa_console.bat` or run from command prompt:

```
wsa_console.bat
```

You can also skip the intro message:

```
wsa_console.bat --no-intro
```

#### On Linux/Mac/WSL

```
python wsa_console.py
```

To skip the intro message:

```
python wsa_console.py --no-intro
```

## 📋 Available Commands

WSA Terminal includes all the classic Amiga commands you remember, plus modern enhancements:

### 🔧 **System Commands**

- `INFO` - Display comprehensive system information (both simulated Amiga and real system specs)
- `AVAIL` - List all available commands
- `STATUS` - Show detailed system status and uptime
- `MOUNT` - Display mounted volumes and device assignments
- `DATE` - Show current date and time
- `HELP` - Display help information for commands

### 📁 **File & Directory Commands**

- `DIR [path]` - List directory contents in authentic Amiga format with period-accurate output:
  - Header: `Directory "path" on DayName DD-MMM-YY`
  - Files: `filename    size  ----rwed     DD-MMM-YY HH:MM:SS`
  - Directories: `dirname    (dir)    ----rwed     DD-MMM-YY HH:MM:SS`
  - Executables: `command    size  ---xrwed     DD-MMM-YY HH:MM:SS`
  - Summary: `X files - Y directories - Z bytes used`
- `CD <directory>` - Change directory (supports `cd ..`, `cd C:`, `cd DH0:`, etc.)
- `ED <filename>` - Built-in text editor with Amiga-style interface
- `TYPE <file>` - Display file contents (supports both virtual Amiga files and real Windows files via DH0:)
- `COPY <source> <dest>` - Copy files
- `DELETE <file>` - Delete files (with confirmation)
- `MAKEDIR <directory>` - Create new directories

### 🌐 **Network & Communication**

- `PING <host> [COUNT=n]` - Network ping utility with authentic output
- `SAY <text> [RATE=n] [VOICE=name]` - Text-to-speech synthesis (like original AmigaOS!)

### 🎮 **Entertainment & Easter Eggs**

- `AMIGA` - Classic Amiga easter egg with ASCII art and nostalgic references
- `GURU` - Display the legendary Guru Meditation error (Press Ctrl+C to stop)
- `PATTERN <pattern>` - Pattern matching utility with file system support

### 🚀 **Advanced Features**

- `WINUAE [config]` - Launch WinUAE Amiga emulator with configuration management
- `EXECUTE <script>` - Run Amiga-style script files
- `CLS`/`CLEAR` - Clear the screen
- `EXIT`/`QUIT` - Exit the terminal (console version only)

### 💡 **Special Features**

- **Tab Autocomplete** - Press Tab to autocomplete file and directory paths
- **Device Navigation** - Type just `DH0:` or `SYS:` to change to that device
- **Real File System Access** - DH0: provides direct access to your Windows C: drive

## 🏛️ Authentic Amiga Experience

### Classic Amiga Features

- **Device-based navigation** - Type just a device name (e.g., `dh0:`) to automatically change directory
- **Authentic command behavior** - Commands work exactly like the original Amiga Workbench CLI
- **Period-accurate output formatting** - Directory listings, system info, and error messages match the original AmigaOS 3.1:
  - DIR command shows day name, full date/time, proper file permissions (`----rwed`, `---xrwed`)
  - Commands in C: directory display as executable files rather than directories
  - File summary format: "X files - Y directories - Z bytes used"
- **Amiga-style path conventions** - Uses forward slashes and device colons (SYS:, RAM:, C:, DH0:)
- **Startup sequence execution** - Runs AmigaOS-style boot scripts at terminal startup

### Modern Integration Features

- **Tab-based path autocomplete** for both file and directory names
- **Real file system integration** for DH0: on Windows systems
- **Cross-platform compatibility** (Windows, Linux, Mac, WSL)
- **Background process support** for launching external applications

### 🌍 Cross-Platform Compatibility

WSA Terminal automatically adapts to your operating system:

| Feature                | Windows              | Linux/WSL       | macOS                |
| ---------------------- | -------------------- | --------------- | -------------------- |
| **DH0: Drive**         | Real C: drive access | Virtual mapping | Virtual mapping      |
| **Text-to-Speech**     | Windows SAPI voices  | eSpeak/Festival | Native `say` command |
| **WinUAE Integration** | Full support         | Not applicable  | Not applicable       |
| **Network Tools**      | Windows ping         | Unix ping       | BSD ping             |
| **File System**        | Windows paths        | Unix paths      | Unix paths           |
| **Path Separators**    | Backslash/Forward    | Forward slash   | Forward slash        |

#### Platform Detection

WSA automatically detects your environment and configures itself accordingly:

- **Windows**: Full C: drive integration, Windows-specific commands
- **WSL**: Hybrid environment with Linux tools but Windows file access
- **Linux**: Pure Unix environment with virtual Windows simulation
- **macOS**: Unix environment with Mac-specific speech synthesis

## 💽 DH0: Drive Integration

WSA Terminal provides seamless integration with your Windows C: drive through the DH0: device:

### Capabilities

- **Automatic C: drive mounting** as DH0: at startup
- **Real-time file system access** for listing directories and files
- **Full subdirectory navigation** (e.g., `cd DH0:Windows\System32`)
- **Actual file sizes and dates** displayed in DIR output
- **File editing support** with the ED command for real files
- **Proper relative path handling** within DH0: directory structure

### Usage Examples

```bash
cd DH0:                    # Navigate to Windows C: drive root
cd DH0:Windows             # Navigate to Windows subdirectory
dir DH0:                   # List contents of C: drive root
dir DH0:Windows\System32   # List Windows system directory
ed DH0:myfile.txt          # Edit a file on the C: drive
type DH0:autoexec.bat      # View contents of C: drive file
```

## 🔧 Advanced Features

### 🎮 WinUAE Integration

Launch real Amiga emulation directly from WSA Terminal!

```bash
winuae                    # Launch with default configuration
winuae "My Config"        # Launch with specific configuration
winuae list              # List available configurations
winuae config            # Show configuration settings
```

**Setup**: Set environment variables to customize WinUAE paths:

```cmd
set WINUAE_PATH=C:\Program Files\WinUAE\winuae.exe
set WINUAE_CONFIG_DIR=C:\Users\Public\Documents\Amiga Files\WinUAE\Configurations
```

### 🗣️ Text-to-Speech (SAY Command)

Experience authentic Amiga speech synthesis:

```bash
say "Hello from Amiga"                    # Basic speech
say "Welcome" RATE=150 VOICE=female      # Custom rate and voice
say voices                               # List available voices
```

**Supported TTS engines**: Windows SAPI, eSpeak, Festival, pyttsx3, macOS say

### 📝 Built-in ED Text Editor

Full-featured line-based text editor just like classic AmigaOS:

```bash
ed myfile.txt             # Edit or create a file
ed SYS:S/Startup-Sequence # Edit system startup script
ed DH0:config.txt         # Edit files on Windows C: drive
```

**Editor commands**:

- Type text and press Enter to add lines
- `LIST` - Show all lines
- `SAVE` - Save the file
- `QUIT` - Exit without saving
- `Ctrl+C` - Exit with save prompt

## 🚀 Startup Sequences

WSA Terminal supports authentic AmigaOS-style startup sequences that run automatically when the terminal starts.

### How It Works

1. **Automatic execution** - Startup script runs when WSA Terminal launches
2. **AmigaOS-compatible** - Uses same syntax and conventions as real Amiga
3. **Customizable** - Edit scripts to personalize your startup experience

### Default Startup Script Content

```bash
; AmigaOS-style startup sequence
; This script runs when the WSA Terminal starts

; Mount additional volumes
; mount RAM: FROM RAM SIZE=1024

; Set environment variables
; setenv PATH C: SYS:S

; Run system tools
; execute SYS:Tools/Shell-Startup
```

### Script Locations (checked in order)

1. `SYS:S/Startup-Sequence` (virtual file system)
2. `DH0:S/Startup-Sequence` (Windows C: drive)
3. `S:Startup-Sequence` (alternate locations)

### Creating Custom Startup Sequences

**Step 1**: Edit the startup script

```bash
ed SYS:S/Startup-Sequence
```

**Step 2**: Add your custom commands

```bash
; My Custom WSA Terminal Startup
echo "Welcome to my personalized WSA Terminal!"
date
info
echo "System ready - The Amiga lives on!"
```

**Step 3**: Save and restart

- Save with `Ctrl+X` in the editor
- Restart WSA Terminal to see your changes

### Manual Script Execution

Run any script manually with the EXECUTE command:

```bash
execute SYS:S/Startup-Sequence
execute DH0:MyScripts/Custom-Setup
execute MyScript.txt
```

## ⌨️ Path Autocomplete Usage

WSA Terminal supports modern Tab-based path autocomplete for enhanced productivity:

### Console Version

1. Type a command like `cd ` (with space)
2. Press **Tab** to see directory completions
3. Continue typing partial paths and press **Tab** for specific completions

### Web Version

1. Type a command like `cd ` (with space)
2. Press **Tab** to autocomplete - first matching path fills automatically

### Examples

```bash
cd SYS:[Tab]              # Shows: SYS:Prefs/, SYS:Tools/, SYS:C/, etc.
cd SYS:P[Tab]             # Completes to: SYS:Prefs/
cd SYS:Prefs/[Tab]        # Shows: SYS:Prefs/Env/, SYS:Prefs/Env-Archive/
dir SYS:P[Tab]            # Works with DIR command too
cd DH0:Win[Tab]           # Real filesystem: completes to DH0:Windows/
```

### Supported Devices

- **SYS:** - System directories
- **RAM:** - RAM disk
- **C:** - Command directory
- **DH0:** - Windows C: drive (with real file system access)

### Features

- **Directory identification** - Trailing slashes added to directories
- **Real file system integration** - DH0: uses actual Windows file system
- **Relative path support** - Works with both absolute (SYS:Prefs/) and relative (Prefs/) paths

## 📦 Creating Executables

Build standalone executables for easy distribution across different platforms:

### 🖥️ Platform-Specific Builds

**Important**: PyInstaller creates platform-specific executables. You must build on each target platform:

| Platform    | Build Environment      | Output Format   | Compatible With    |
| ----------- | ---------------------- | --------------- | ------------------ |
| **Windows** | Windows Command Prompt | `.exe` files    | Windows 7+         |
| **Linux**   | Linux/WSL terminal     | ELF binaries    | Most Linux distros |
| **macOS**   | macOS terminal         | Mach-O binaries | macOS 10.9+        |

### Windows Executables (.exe)

Run in **Windows Command Prompt** (not WSL):

```cmd
build_windows_exe.bat
```

Or manually:

```cmd
pip install pyinstaller
pyinstaller --onefile --name wsa wsa.py
pyinstaller --onefile --name wsa_console wsa_console.py
```

**Output**: Creates `wsa.exe` and `wsa_console.exe` in the `dist/` folder

- **File size**: ~6-11 MB each
- **Dependencies**: None (fully standalone)

### Linux Executables

Run in Linux or WSL terminal:

```bash
pip3 install pyinstaller
pyinstaller --onefile --name wsa wsa.py
pyinstaller --onefile --name wsa_console wsa_console.py
```

**Output**: Creates `wsa` and `wsa_console` binaries in the `dist/` folder

- **File format**: ELF 64-bit executables
- **File size**: ~6-11 MB each

### macOS Executables

Run in macOS terminal:

```bash
pip3 install pyinstaller
pyinstaller --onefile --name wsa wsa.py
pyinstaller --onefile --name wsa_console wsa_console.py
```

**Output**: Creates `wsa` and `wsa_console` binaries in the `dist/` folder

### 🌍 Cross-Platform Distribution Strategy

#### Option 1: Platform-Specific Releases ⭐ **Recommended**

Build separate executables for each platform:

- `wsa-windows.zip` (contains `.exe` files)
- `wsa-linux.tar.gz` (contains Linux binaries)
- `wsa-macos.tar.gz` (contains macOS binaries)

#### Option 2: Universal Python Source ⭐ **Simplest**

Distribute the Python source code - works on any platform with Python 3.7+:

```bash
python wsa.py              # Web version
python wsa_console.py      # Console version
```

### ⚠️ Important Notes

- **WSL Users**: Building in WSL creates Linux executables, not Windows ones
- **Windows Executables**: Must be built on Windows to get `.exe` format
- **Antivirus**: Some antivirus may flag PyInstaller executables as suspicious (false positive)
- **Size**: Executables are larger than source due to embedded Python interpreter

## 🤝 Contributing

We welcome contributions! Whether it's:

- 🐛 Bug fixes and improvements
- ✨ New Amiga commands or features
- 📚 Documentation enhancements
- 🎨 UI/UX improvements
- 🔧 Cross-platform compatibility fixes

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

**Copyright (c) 2025 Tim Davies** - Original creator and maintainer

The MIT License allows anyone to use, modify, and distribute this software freely, including for commercial purposes, as long as the original copyright notice is preserved.

## 🙏 Acknowledgments

- Inspired by the legendary **Commodore Amiga** computer systems
- Tribute to **AmigaOS** and its innovative command-line interface
- Built with love for retro computing enthusiasts and nostalgia seekers

### Recent Updates (v1.0.0)

- ✨ **Enhanced DIR Command** - Now displays authentic AmigaOS 3.1 format with proper headers, permissions, and summaries
- 🔧 **Improved File System Integration** - Better handling of both virtual Amiga files and real Windows files
- 📁 **Cross-Platform Executables** - Platform-specific build instructions and distribution strategies
- 🎯 **Period-Accurate Output** - Commands now match original Amiga formatting exactly

---

**"The Amiga lives on in WSA Terminal!"** 🚀

_Experience the magic of 1980s computing with modern convenience._
