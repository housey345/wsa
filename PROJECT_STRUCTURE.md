# WSA Terminal Project Structure

## 📁 Files Overview

### 🚀 Main Applications

- `wsa.py` - **Web version** with AmigaTerminal class, WebSocket server, and browser interface
- `wsa_console.py` - **Console version** that runs directly in terminal using Python's cmd module
- `requirements.txt` - Python dependencies for both versions
- `setup.py` - Setup script for packaging and distribution
- `wsa.spec` / `wsa_console.spec` - PyInstaller spec files for executable creation

### 🔧 Runtime Scripts

- `wsa.bat` / `wsa.ps1` - Windows batch/PowerShell scripts to run web version
- `wsa_console.bat` / `wsa_console.ps1` - Windows batch/PowerShell scripts to run console version
- `build_exe.bat` / `build_windows_exe.bat` / `build_console_exe.bat` - Executable creation scripts
- `get_icon.bat` - Icon extraction utility

### 📚 Documentation

- `README.md` - Comprehensive project documentation
- `PROJECT_STRUCTURE.md` - This file - project structure overview
- `WINUAE_INTEGRATION.md` - WinUAE emulator integration guide
- `SAY_COMMAND.md` - Text-to-speech functionality documentation
- `HOWTO_STARTUP.md` - Startup sequence configuration guide
- `wsa.ico` - Application icon
- `wsa.manifest` - Windows application manifest
- `.gitignore` - Git ignore file for build artifacts and cache files

## 🏗️ Directory Structure Simulation

WSA Terminal simulates an authentic Amiga directory structure:

### 💾 Virtual Devices

- **SYS:** - System directory (contains AmigaOS system files and subdirectories)
  - `SYS:S/` - System scripts (including Startup-Sequence)
  - `SYS:L/` - Libraries directory
  - `SYS:DEVS/` - Device drivers
  - `SYS:Fonts/` - System fonts
  - `SYS:Prefs/` - Preferences and environment variables
  - `SYS:Tools/` - System utilities
- **RAM:** - RAM disk for temporary files
  - `RAM:T/` - Temporary files directory
- **C:** - Commands directory (contains all executable Amiga commands)
- **DH0:** - Windows C: drive mapping (real file system access)

### 🔧 Command Implementation Architecture

Commands are implemented differently in each version:

#### **Web Version** (`wsa.py`)

- Commands implemented as **async methods** in the `AmigaTerminal` class
- WebSocket-based real-time communication
- JSON response format for structured output
- Browser-based interface with retro styling

#### **Console Version** (`wsa_console.py`)

- Commands implemented using Python's **cmd module** with `do_*` methods
- Direct terminal input/output
- Tab completion support via `complete_*` methods
- Enhanced with real-time system information integration

## 🎮 Implemented Commands

### 🔧 **Core System Commands**

- `INFO` - Enhanced system information (both simulated Amiga and real system specs)
- `AVAIL` - List all available commands
- `STATUS` - Detailed system status with real-time information
- `MOUNT` - Show mounted volumes and device assignments
- `DATE` - Current date and time display
- `HELP` - Context-sensitive help system

### 📁 **File & Directory Management**

- `DIR` - Amiga-style directory listings with Size, Protection, Date columns
- `CD` - Directory navigation with device support (`cd SYS:`, `cd DH0:`, `cd ..`)
- `ED` - Built-in line-based text editor with Amiga-style interface
- `TYPE` - Display file contents
- `COPY` - File copy operations
- `DELETE` - File deletion with confirmation prompts
- `MAKEDIR` - Directory creation
- `PATTERN` - Pattern matching utility with real file system support

### 🌐 **Network & Communication**

- `PING <host> [COUNT=n]` - Network connectivity testing with real ping functionality
- `SAY <text> [RATE=n] [VOICE=name]` - Text-to-speech synthesis (multiple TTS engines)

### 🎨 **Entertainment & Easter Eggs**

- `AMIGA` - Classic Amiga easter egg with ASCII art and nostalgic references
- `GURU` - Authentic Guru Meditation error display with flashing red banner
- `ECHO` - Text output command

### 🚀 **Advanced Integration Features**

- `WINUAE [config]` - Launch WinUAE Amiga emulator with configuration management
- `EXECUTE <script>` - Run AmigaOS-style script files
- `CLS`/`CLEAR` - Screen clearing
- `EXIT`/`QUIT` - Terminal exit (console version only)

### 💡 **Special Navigation Features**

- **Device shortcuts** - Type device names (`SYS:`, `DH0:`, `RAM:`) to change directory
- **Tab completion** - Path autocomplete for files and directories
- **Real file system access** - DH0: provides direct Windows C: drive integration

## 🌐 Technical Architecture

### **Web Interface** (`wsa.py`)

- **WebSocket communication** for real-time bidirectional interaction
- **Async/await architecture** for non-blocking command processing
- **HTML/CSS interface** with authentic Amiga Workbench 4.0 styling
- **JavaScript client** for terminal interaction and CRT effects
- **aiohttp web server** for HTTP and WebSocket handling

### **Console Interface** (`wsa_console.py`)

- **Python cmd module** for command-line interface framework
- **Cross-platform terminal handling** (Windows, Linux, Mac, WSL)
- **Tab completion system** with custom `complete_*` methods
- **Direct stdin/stdout** for immediate response and interaction
- **Real-time system integration** via psutil and subprocess

### **Cross-Platform Compatibility**

- **Windows** - Native Windows API integration, WinUAE support, Windows SAPI TTS
- **Linux/WSL** - eSpeak/Festival TTS, Unix ping command, /mnt/c drive access
- **macOS** - Native say command for TTS, BSD-style utilities

## 🛠️ Development Guidelines

### Adding New Commands

1. **Web Version** (`wsa.py`):

   ```python
   async def handle_command_mycommand(self, args):
       """Handle MYCOMMAND - Description"""
       # Implementation here
       return [{"text": "Output", "color": "white"}]
   ```

2. **Console Version** (`wsa_console.py`):

   ```python
   def do_mycommand(self, arg):
       """MYCOMMAND - Description"""
       # Implementation here
       print("Output")

   def complete_mycommand(self, text, line, begidx, endidx):
       """Tab completion for MYCOMMAND"""
       return self._get_matching_paths(text)
   ```

### Development Workflow

1. **Edit implementation files** (`wsa.py` and/or `wsa_console.py`)
2. **Test functionality** manually in both web and console versions for consistency
3. **Update documentation** as needed (README.md and relevant .md files)
4. **Create executables** for distribution: `build_exe.bat` / `build_windows_exe.bat`

### Project Standards

- **Maintain Amiga authenticity** - Commands should behave like original AmigaOS
- **Cross-platform compatibility** - Test on Windows, Linux, and WSL
- **Comprehensive documentation** - Update README.md and relevant .md files
- **Error handling** - Graceful degradation when optional features unavailable
