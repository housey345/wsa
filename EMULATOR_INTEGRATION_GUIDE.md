# WSA Terminal - Emulator Integration Implementation Guide

## 🎯 **Feature Overview: Mount WinUAE/FS-UAE as Virtual Drives**

This guide outlines the implementation plan for integrating WinUAE and FS-UAE emulators as mounted drives within WSA Terminal.

## 🛠️ **Implementation Phases**

### **Phase 1: ADF Reader** (Foundation - Most Valuable)
**Goal**: Read Amiga disk files (ADF/HDF) directly and present as virtual drives

#### Features:
- Mount ADF/HDF files as virtual drives (DF0:, DH1:, etc.)
- Parse OFS/FFS Amiga file systems
- Support DIR, TYPE, COPY operations on mounted disks
- Read Amiga file metadata and permissions

#### Implementation:
```python
class ADFReader:
    def __init__(self, adf_path):
        self.adf_path = adf_path
        self.sectors = self._read_adf()
    
    def _read_adf(self):
        # Read ADF file structure (880KB standard)
        # Parse boot block, root block, directory blocks
        # Handle OFS (Original File System) and FFS (Fast File System)
        pass
    
    def list_directory(self, path="/"):
        # Parse directory blocks
        # Return files/dirs in authentic Amiga format
        pass
    
    def read_file(self, path):
        # Follow file allocation chains
        # Extract file contents from data blocks
        pass
```

#### Commands:
```bash
mount DF0: FROM "C:\Amiga\Workbench31.adf"    # Mount floppy
mount DH1: FROM "C:\Amiga\Games.hdf"          # Mount hard disk
dir DF0:                                      # Browse contents
type DF0:S/Startup-Sequence                   # Read files
copy DH0:myfile.txt DF0:RAM:                  # Transfer files
```

---

### **Phase 2: Shared Folders** (Practical - CURRENT PHASE)
**Goal**: Mount WinUAE/FS-UAE shared directories as virtual drives

#### Features:
- Detect and mount WinUAE shared folder configurations
- Mount FS-UAE shared directories
- Bidirectional file transfer between WSA and emulators
- Real-time synchronization and change detection

#### Implementation Strategy:
```python
class EmulatorSharedFolder:
    def __init__(self, emulator_type, config_name_or_path):
        self.emulator_type = emulator_type  # 'winuae' or 'fs-uae'
        self.config = self._parse_config(config_name_or_path)
        self.shared_path = self._get_shared_path()
    
    def _parse_winuae_config(self, config_name):
        # Parse WinUAE .uae configuration files
        # Look for filesystem2= entries (shared folders)
        # Extract volume name and host path
        pass
    
    def _parse_fsuae_config(self, config_path):
        # Parse FS-UAE .fs-uae configuration files
        # Look for hard_drive_* entries with host folders
        pass
```

#### WinUAE Configuration Detection:
- Standard config locations:
  - `C:\Users\Public\Documents\Amiga Files\WinUAE\Configurations\`
  - `%USERPROFILE%\Documents\Amiga Files\WinUAE\Configurations\`
- Parse `.uae` files for `filesystem2=` entries
- Extract shared folder mappings

#### FS-UAE Configuration Detection:
- Standard config locations:
  - `~/.config/fs-uae/`
  - `~/Documents/FS-UAE/Configurations/`
- Parse `.fs-uae` files for `hard_drive_*` entries
- Support both file and directory mounting

#### Commands:
```bash
mount SHARED: FROM WINUAE "My A1200 Config"   # Mount WinUAE shared
mount FSU0: FROM FS-UAE "Workbench31.fs-uae"  # Mount FS-UAE shared
winuae list configs                           # List available configs
winuae show "My A1200 Config"                # Show config details
cd SHARED:                                    # Access shared files
```

---

### **Phase 3: Live Integration** (Advanced - Future)
**Goal**: Connect to running emulator instances in real-time

#### Features:
- Detect running WinUAE/FS-UAE instances
- Connect via TCP/IP or named pipes
- Real-time file system access
- Send commands to emulator (reset, disk change, etc.)
- Monitor emulator state and events

#### Implementation:
```python
class LiveEmulatorConnection:
    def __init__(self, emulator_type, connection_method):
        self.emulator = emulator_type
        self.connection = self._establish_connection(connection_method)
    
    def _establish_connection(self, method):
        # TCP socket connection to emulator
        # Named pipe communication (Windows)
        # Shared memory access
        pass
    
    def send_command(self, command):
        # Send debugger commands to WinUAE
        # Send scripting commands to FS-UAE
        pass
```

## 📋 **Technical Requirements**

### **Python Libraries Needed:**
- `struct` - Binary data parsing (ADF/HDF files)
- `mmap` - Memory-mapped file access for large disk images  
- `configparser` - Parse emulator configuration files
- `watchdog` - Monitor shared folder changes
- `sqlite3` - Cache directory structures for performance
- `socket` - Network communication with emulators (Phase 3)
- `threading` - Background monitoring and synchronization

### **File Format Support:**
- **ADF** (Amiga Disk File) - 880KB floppy disk images
- **HDF** (Hard Disk File) - Amiga hard disk images
- **UAE** (WinUAE configuration files)
- **FS-UAE** (FS-UAE configuration files)
- **DMS** (Disk Masher System) - Compressed Amiga disks (future)

## 🎯 **Benefits & Use Cases**

### **Developer Workflow:**
```bash
# Develop on modern system
ed DH0:Projects\AmigaGame\main.c
# Compile and test
copy DH0:Projects\AmigaGame\* SHARED:Development/
cd SHARED:Development
winuae launch "Development A1200"
# Game runs in emulator immediately
```

### **Archive Management:**
```bash
# Browse disk collection without launching emulator
mount DF0: FROM "C:\Amiga\Games\Lemmings.adf"
dir DF0:
type DF0:readme.txt
# Extract specific files
copy DF0:Lemmings DH0:ExtractedGames\
```

### **Hybrid Computing:**
```bash
# Use modern tools with retro environment
dir SHARED:                    # Browse emulator files
copy SHARED:document.txt DH0:  # Bring to modern system
ed DH0:document.txt           # Edit with modern tools
copy DH0:document.txt SHARED: # Send back to emulator
```

## 🚀 **Implementation Priority Order**

1. **Phase 2 (Current)**: Shared Folders - Immediate practical value
2. **Phase 1**: ADF Reader - Unique archive access capability  
3. **Phase 3**: Live Integration - Advanced real-time features

## 📝 **Configuration File Examples**

### **WinUAE .uae file extract:**
```ini
filesystem2=rw,DH0:Shared:C:\WinUAE\Shared,0
filesystem2=rw,DH1:Games:C:\Amiga\Games,0
filesystem2=ro,DF0:Floppies:C:\Amiga\ADFs,-128
```

### **FS-UAE .fs-uae file extract:**
```ini
hard_drive_0 = ~/Amiga/Workbench
hard_drive_0_label = Workbench
hard_drive_1 = ~/Amiga/Games  
hard_drive_1_label = Games
```

## 💡 **Error Handling & Edge Cases**

### **Common Issues to Handle:**
- Missing emulator installations
- Invalid configuration files
- Permission issues accessing shared folders
- Network connectivity problems (Phase 3)
- Corrupted ADF/HDF files (Phase 1)
- Multiple emulator instances (Phase 3)

### **User Experience Considerations:**
- Auto-detect emulator installations
- Provide helpful error messages
- Graceful fallback when emulators unavailable  
- Progress indicators for large operations
- Confirmation prompts for destructive operations

---

**Last Updated**: October 2, 2025
**Status**: Phase 2 (Shared Folders) - In Development
**Next Steps**: Implement WinUAE configuration parsing and shared folder mounting