#!/usr/bin/env python3
"""
WSA Terminal Console Version - Windows Subsystem for Amiga
Command-line version that runs directly in the terminal
"""

import os
import sys
import cmd
import argparse
import platform
import subprocess
import time
import random
import io
import contextlib
import re
import configparser
import glob
from datetime import datetime

# WinUAE Configuration - Global Variables with Fallbacks
WINUAE_CONFIG = {
    'executable_path': os.environ.get('WINUAE_PATH', r'C:\Program Files\WinUAE\winuae.exe'),
    'config_dir': os.environ.get('WINUAE_CONFIG_DIR', r'C:\Users\Public\Documents\Amiga Files\WinUAE\Configurations'),
    'default_config': os.environ.get('WINUAE_DEFAULT_CONFIG', 'MY AGS CONFIG.uae'),
    'kickstart_dir': os.environ.get('WINUAE_KICKSTART_DIR', r'C:\Users\Public\Documents\Amiga Files\WinUAE\Kickstarts'),
    'hdf_dir': os.environ.get('WINUAE_HDF_DIR', r'C:\Users\Public\Documents\Amiga Files\WinUAE\Hardfiles')
}

def get_winuae_executable():
    """Get the WinUAE executable path with fallback search"""
    # Try environment variable first
    winuae_path = WINUAE_CONFIG['executable_path']
    if os.path.exists(winuae_path):
        return winuae_path
    
    # Common installation paths to try
    common_paths = [
        r'C:\Program Files\WinUAE\winuae.exe',
        r'C:\Program Files (x86)\WinUAE\winuae.exe',
        r'C:\WinUAE\winuae.exe',
        r'C:\Games\WinUAE\winuae.exe'
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    return None

def get_winuae_config_path(config_name=None):
    """Get the full path to a WinUAE configuration file"""
    if config_name is None:
        config_name = WINUAE_CONFIG['default_config']
    
    config_dir = WINUAE_CONFIG['config_dir']
    
    # Try to expand user paths
    config_dir = os.path.expanduser(config_dir)
    config_dir = os.path.expandvars(config_dir)
    
    return os.path.join(config_dir, config_name)

def list_winuae_configs():
    """List available WinUAE configuration files"""
    config_dir = WINUAE_CONFIG['config_dir']
    config_dir = os.path.expanduser(config_dir)
    config_dir = os.path.expandvars(config_dir)
    
    if not os.path.exists(config_dir):
        return []
    
    try:
        files = os.listdir(config_dir)
        return [f for f in files if f.lower().endswith('.uae')]
    except Exception:
        return []


class EmulatorSharedFolder:
    """Class to handle WinUAE and FS-UAE shared folder mounting"""
    
    def __init__(self):
        self.mounted_shared_folders = {}
        self.winuae_configs = {}
        self.fsuae_configs = {}
        self._scan_emulator_configs()
    
    def _scan_emulator_configs(self):
        """Scan for available WinUAE and FS-UAE configurations"""
        self._scan_winuae_configs()
        self._scan_fsuae_configs()
    
    def _scan_winuae_configs(self):
        """Scan for WinUAE configuration files and extract shared folders"""
        config_dir = WINUAE_CONFIG['config_dir']
        config_dir = os.path.expanduser(config_dir)
        config_dir = os.path.expandvars(config_dir)
        
        if not os.path.exists(config_dir):
            return
        
        try:
            for config_file in glob.glob(os.path.join(config_dir, "*.uae")):
                config_name = os.path.basename(config_file)
                shared_folders = self._parse_winuae_config(config_file)
                if shared_folders:
                    self.winuae_configs[config_name] = {
                        'path': config_file,
                        'shared_folders': shared_folders
                    }
        except Exception as e:
            print(f"Warning: Error scanning WinUAE configs: {e}")
    
    def _scan_fsuae_configs(self):
        """Scan for FS-UAE configuration files and extract shared folders"""
        # Common FS-UAE config locations
        fsuae_dirs = [
            os.path.expanduser("~/.config/fs-uae"),
            os.path.expanduser("~/Documents/FS-UAE/Configurations"),
            os.path.expanduser("~/.fs-uae")
        ]
        
        for config_dir in fsuae_dirs:
            if os.path.exists(config_dir):
                try:
                    for config_file in glob.glob(os.path.join(config_dir, "*.fs-uae")):
                        config_name = os.path.basename(config_file)
                        shared_folders = self._parse_fsuae_config(config_file)
                        if shared_folders:
                            self.fsuae_configs[config_name] = {
                                'path': config_file,
                                'shared_folders': shared_folders
                            }
                except Exception as e:
                    print(f"Warning: Error scanning FS-UAE configs in {config_dir}: {e}")
    
    def _parse_winuae_config(self, config_file):
        """Parse WinUAE .uae configuration file for shared folders"""
        shared_folders = {}
        
        try:
            with open(config_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    # Look for filesystem2= entries (WinUAE shared folders)
                    if line.startswith('filesystem2='):
                        # Format: filesystem2=rw,DH0:Label:C:\Path,0
                        try:
                            parts = line.split('=', 1)[1].split(',')
                            if len(parts) >= 3:
                                access_mode = parts[0]  # rw, ro, etc.
                                device_info = parts[1]  # DH0:Label:Path
                                
                                if ':' in device_info:
                                    device_parts = device_info.split(':', 2)
                                    if len(device_parts) >= 3:
                                        device = device_parts[0] + ":"
                                        label = device_parts[1]
                                        path = device_parts[2]
                                        
                                        if os.path.exists(path):
                                            shared_folders[device] = {
                                                'label': label,
                                                'path': path,
                                                'access': access_mode
                                            }
                        except Exception:
                            continue
        except Exception as e:
            print(f"Warning: Could not parse WinUAE config {config_file}: {e}")
        
        return shared_folders
    
    def _parse_fsuae_config(self, config_file):
        """Parse FS-UAE .fs-uae configuration file for shared folders"""
        shared_folders = {}
        
        try:
            with open(config_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    # Look for hard_drive_* entries
                    if line.startswith('hard_drive_') and '=' in line:
                        try:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            
                            # Extract drive number
                            if '_' in key:
                                drive_num = key.split('_')[-1]
                                
                                # Skip if it's a label definition
                                if key.endswith('_label'):
                                    continue
                                
                                # Check if it's a directory path (not a file)
                                if os.path.isdir(value):
                                    device = f"DH{drive_num}:"
                                    
                                    # Look for corresponding label
                                    label = f"Drive{drive_num}"
                                    # This is simplified - in a full implementation,
                                    # we'd parse the entire file to match labels
                                    
                                    shared_folders[device] = {
                                        'label': label,
                                        'path': value,
                                        'access': 'rw'
                                    }
                        except Exception:
                            continue
        except Exception as e:
            print(f"Warning: Could not parse FS-UAE config {config_file}: {e}")
        
        return shared_folders
    
    def mount_shared_folder(self, device, emulator_type, config_name):
        """Mount a shared folder from emulator configuration"""
        device = device.upper()
        if not device.endswith(':'):
            device += ':'
        
        if emulator_type.lower() == 'winuae':
            if config_name in self.winuae_configs:
                config = self.winuae_configs[config_name]
                if device in config['shared_folders']:
                    folder_info = config['shared_folders'][device]
                    self.mounted_shared_folders[device] = {
                        'emulator': 'winuae',
                        'config': config_name,
                        'label': folder_info['label'],
                        'path': folder_info['path'],
                        'access': folder_info['access']
                    }
                    return True, f"{device} mounted from WinUAE config '{config_name}' ({folder_info['label']})"
                else:
                    return False, f"Device {device} not found in WinUAE config '{config_name}'"
            else:
                return False, f"WinUAE config '{config_name}' not found"
        
        elif emulator_type.lower() == 'fs-uae':
            if config_name in self.fsuae_configs:
                config = self.fsuae_configs[config_name]
                if device in config['shared_folders']:
                    folder_info = config['shared_folders'][device]
                    self.mounted_shared_folders[device] = {
                        'emulator': 'fs-uae',
                        'config': config_name,
                        'label': folder_info['label'],
                        'path': folder_info['path'],
                        'access': folder_info['access']
                    }
                    return True, f"{device} mounted from FS-UAE config '{config_name}' ({folder_info['label']})"
                else:
                    return False, f"Device {device} not found in FS-UAE config '{config_name}'"
            else:
                return False, f"FS-UAE config '{config_name}' not found"
        
        else:
            return False, f"Unknown emulator type: {emulator_type}"
    
    def unmount_shared_folder(self, device):
        """Unmount a shared folder"""
        device = device.upper()
        if not device.endswith(':'):
            device += ':'
        
        if device in self.mounted_shared_folders:
            del self.mounted_shared_folders[device]
            return True, f"{device} unmounted"
        else:
            return False, f"Device {device} is not mounted"
    
    def list_available_configs(self):
        """List all available emulator configurations"""
        configs = []
        
        for config_name, config_info in self.winuae_configs.items():
            configs.append({
                'emulator': 'WinUAE',
                'name': config_name,
                'shared_folders': list(config_info['shared_folders'].keys())
            })
        
        for config_name, config_info in self.fsuae_configs.items():
            configs.append({
                'emulator': 'FS-UAE',
                'name': config_name,
                'shared_folders': list(config_info['shared_folders'].keys())
            })
        
        return configs
    
    def get_shared_folder_path(self, device):
        """Get the real path for a mounted shared folder device"""
        device = device.upper()
        if not device.endswith(':'):
            device += ':'
        
        if device in self.mounted_shared_folders:
            return self.mounted_shared_folders[device]['path']
        return None


class WSAConsoleTerminal(cmd.Cmd):
    intro = """WSA Terminal - Windows Subsystem for Amiga
Copyright (C) 2025 WSA Project Contributors
Inspired by the legendary Amiga computer systems
Type 'help' or '?' for available commands.
"""
    
    # Override default cmd module behavior to make commands case-insensitive (authentic Amiga behavior)
    def onecmd(self, line):
        """Process command line with case-insensitivity"""
        cmd, arg, line = self.parseline(line)
        if not line:
            return self.emptyline()
        if cmd is None:
            return self.default(line)
        
        # This is the key change - convert command to lowercase before looking for do_* method
        cmd = cmd.lower()
        self.lastcmd = line
        
        if cmd == '':
            return self.default(line)
        else:
            try:
                func = getattr(self, 'do_' + cmd)
            except AttributeError:
                return self.default(line)
            return func(arg)
    
    def __init__(self):
        super().__init__()
        self.current_dir = "SYS:"
        self.prompt = "SYS:> "
        
        # Initialize emulator shared folder integration
        self.emulator_integration = EmulatorSharedFolder()
        
        # Add Windows C: drive by default
        self.directories = {
            "SYS:": ["Prefs", "Tools", "L", "S", "C", "DEVS", "Fonts", "WBStartup"],
            "SYS:S": [],  # System scripts directory
            "SYS:L": [],  # Libraries directory  
            "SYS:DEVS": [],  # Device drivers directory
            "SYS:Fonts": [],  # Fonts directory
            "SYS:Prefs": ["Env-Archive", "Env"],  # Preferences directory with Env subdirectories
            "SYS:Prefs/Env-Archive": [],  # Environment archive directory
            "SYS:Prefs/Env": [],  # Current environment directory
            "RAM:": ["T"],
            "RAM:T": [],  # Temporary files directory
            "C:": ["Info", "Avail", "Status", "Mount", "Ed", "Dir", "Cd", "Pattern", "Date", "Echo", "Help", "Amiga", "Ping", "WinUAE", "Say", "Guru"],
            "DH0:": []  # Windows C: drive mapped as DH0:
        }
        self.files = {
            "SYS:Prefs/Env-Archive/PATH": "C: SYS:S SYS:C",
            "SYS:Prefs/Env-Archive/SHELL": "WSA Terminal",
            "SYS:Prefs/Env/PATH": "C: SYS:S SYS:C", 
            "SYS:Prefs/Env/SHELL": "WSA Terminal",
            "SYS:Tools/Shell-Startup": "Shell startup script",
            "SYS:S/Startup-Sequence": "; AmigaOS-style startup sequence\n; This script runs when the WSA Terminal starts\n\n; Mount additional volumes\n; mount RAM: FROM RAM SIZE=1024\n\n; Set environment variables\n; setenv PATH C: SYS:S\n\n; Run system tools\n; execute SYS:Tools/Shell-Startup\n",
            "RAM:T/Temp-File": "Temporary file",
            "C:Info": "System information utility",
            "C:Avail": "List available commands",
            "C:Status": "Show system status",
            "C:Mount": "Mount volumes",
            "C:Ed": "Text editor",
            "C:Dir": "Directory listing",
            "C:Cd": "Change directory",
            "C:Pattern": "Pattern matching utility",
            "C:Date": "Show date and time",
            "C:Echo": "Echo text to terminal",
            "C:Help": "Display help information",
            "C:Amiga": "Amiga easter egg command",
            "C:Ping": "Network ping utility",
            "C:WinUAE": "Launch WinUAE Amiga emulator",
            "C:Say": "Text-to-speech synthesis",
            "C:Guru": "Guru Meditation error demo"
        }
        
        # Add Windows C: drive files if we're on Windows
        if platform.system() == "Windows":
            # Try to get actual C: drive contents
            try:
                c_drive_path = "C:\\"
                if os.path.exists(c_drive_path):
                    self.directories["DH0:"] = []
                    # Add some common Windows directories
                    common_dirs = ["Windows", "Program Files", "Users", "Documents and Settings", "Program Files (x86)"]
                    for dir_name in common_dirs:
                        if os.path.exists(os.path.join(c_drive_path, dir_name)):
                            self.directories["DH0:"].append(dir_name)
                    
                    # Add some common files
                    common_files = ["pagefile.sys", "hiberfil.sys", "swapfile.sys"]
                    for file_name in common_files:
                        if os.path.exists(os.path.join(c_drive_path, file_name)):
                            self.files[f"DH0:/{file_name}"] = f"System file: {file_name}"
            except Exception:
                # Fallback to placeholder content
                self.directories["DH0:"] = ["Windows", "Program Files", "Users", "Documents and Settings"]
                self.files.update({
                    "DH0:/Windows/System32/kernel32.dll": "Windows kernel library",
                    "DH0:/Windows/explorer.exe": "Windows Explorer",
                    "DH0:/Program Files/": "Program Files directory",
                    "DH0:/Users/": "Users directory"
                })
        else:
            # For non-Windows systems, add placeholder content
            self.directories["DH0:"] = ["Windows", "Program Files", "Users", "Documents and Settings"]
            self.files.update({
                "DH0:/Windows/System32/kernel32.dll": "Windows kernel library",
                "DH0:/Windows/explorer.exe": "Windows Explorer",
                "DH0:/Program Files/": "Program Files directory",
                "DH0:/Users/": "Users directory"
            })
        
        # Execute startup sequence
        self._execute_startup_sequence()
        
    def _execute_startup_sequence(self):
        """Execute the Amiga-style startup sequence"""
        # Print startup message
        print("Executing startup sequence...")
        
        # Check for SYS:S/Startup-Sequence in virtual file system
        startup_file = "SYS:S/Startup-Sequence"
        if startup_file in self.files:
            self._run_startup_script(startup_file, self.files[startup_file])
            return
            
        # Check for actual file in DH0: (Windows C: drive)
        if platform.system() == "Windows":
            try:
                fs_path = os.path.join("C:\\", "S", "Startup-Sequence")
                if os.path.exists(fs_path):
                    with open(fs_path, 'r') as f:
                        content = f.read()
                    self._run_startup_script(startup_file, content)
                    return
            except Exception:
                pass  # Continue to next check
                
        # Check for other common startup locations
        startup_locations = [
            "SYS:S/startup-sequence",
            "S:Startup-Sequence",
            "S:startup-sequence"
        ]
        
        for location in startup_locations:
            if location in self.files:
                self._run_startup_script(location, self.files[location])
                return
                
    def _run_startup_script(self, script_name, content):
        """Run a startup script"""
        print(f"Executing {script_name}...")
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith(';'):
                continue
                
            # Execute the command
            try:
                # Handle echo commands
                if line.lower().startswith('echo '):
                    print(line[5:])
                # Handle other commands by calling the appropriate method
                else:
                    # Parse command and arguments
                    parts = line.split()
                    if not parts:
                        continue
                        
                    cmd = parts[0].lower()
                    args = ' '.join(parts[1:]) if len(parts) > 1 else ''
                    
                    # Execute built-in commands
                    if hasattr(self, f"do_{cmd}"):
                        method = getattr(self, f"do_{cmd}")
                        # Capture output and print it
                        import io
                        import contextlib
                        f = io.StringIO()
                        with contextlib.redirect_stdout(f):
                            method(args)
                        output = f.getvalue()
                        if output.strip():
                            print(output.strip())
                    # Handle some special cases
                    elif cmd == 'cd':
                        result = self._change_directory(args)
                        if result:
                            print(result)
                    elif cmd == 'dir':
                        import io
                        import contextlib
                        f = io.StringIO()
                        with contextlib.redirect_stdout(f):
                            self._list_files()
                        output = f.getvalue()
                        print(output.strip())
                    elif cmd == 'mount':
                        import io
                        import contextlib
                        f = io.StringIO()
                        with contextlib.redirect_stdout(f):
                            self._mount_command()
                        output = f.getvalue()
                        print(output.strip())
                    elif cmd == 'date':
                        print(str(datetime.now()))
                    else:
                        print(f"Startup command not recognized: {line}")
            except Exception as e:
                print(f"Error executing startup command '{line}': {e}")
    
    def precmd(self, line):
        """Process command line before execution - handle device names as CD commands"""
        # If the line is just a device name (ends with :), treat it as a CD command
        if line and line.upper().endswith(':') and ':' in line:
            # Check if it's a valid device (case insensitive)
            device = line.upper()
            
            # Handle logical assignments (common Amiga directory shortcuts)
            logical_assignments = {
                "S:": "SYS:S",
                "L:": "SYS:L", 
                "DEVS:": "SYS:DEVS",
                "FONTS:": "SYS:Fonts",
                "T:": "RAM:T"
            }
            
            if device in logical_assignments:
                return f"cd {logical_assignments[device]}"
            
            # Check main devices
            if device in [d.upper() for d in self.directories.keys()]:
                # Find the actual device name with correct case
                for actual_device in self.directories.keys():
                    if actual_device.upper() == device:
                        return f"cd {actual_device}"
        return line
        
    def complete_cd(self, text, line, begidx, endidx):
        """Autocomplete for CD command - complete directory names"""
        return self._get_matching_paths(text, directories_only=True)
        
    def complete_dir(self, text, line, begidx, endidx):
        """Autocomplete for DIR command - complete directory and file names"""
        return self._get_matching_paths(text, directories_only=False)
        
    def _get_matching_paths(self, text, directories_only=False):
        """Get matching paths for autocomplete"""
        # Handle absolute paths (starting with device:)
        if ":" in text:
            device_part, path_part = text.split(":", 1)
            device = device_part + ":"
            
            # Handle DH0: with actual file system
            if device.upper() == "DH0:":
                # Check if we're running in WSL environment
                is_wsl = os.path.exists("/mnt/c")
                is_windows = platform.system() == "Windows"
                
                if is_wsl or is_windows:
                    try:
                        # Determine the actual file system path
                        if is_wsl:
                            fs_base_path = "/mnt/c"
                        else:
                            fs_base_path = "C:\\"
                            
                        if path_part:
                            if is_wsl:
                                fs_search_path = os.path.join(fs_base_path, path_part.replace("\\", "/"))
                            else:
                                fs_search_path = os.path.join(fs_base_path, path_part.replace("/", "\\"))
                        else:
                            fs_search_path = fs_base_path
                        
                        # Normalize the path
                        fs_search_path = os.path.normpath(fs_search_path)
                        
                        # Get parent directory to list contents
                        if path_part and not path_part.endswith("/") and not path_part.endswith("\\"):
                            fs_parent_path = os.path.dirname(fs_search_path)
                        else:
                            fs_parent_path = fs_search_path
                        
                        if os.path.exists(fs_parent_path) and os.path.isdir(fs_parent_path):
                            items = os.listdir(fs_parent_path)
                            matches = []
                            for item in items:
                                item_path = os.path.join(fs_parent_path, item)
                                if path_part:
                                    full_path = device + path_part.rsplit("/", 1)[0] + "/" + item
                                else:
                                    full_path = device + item
                                
                                # Add trailing slash for directories
                                if os.path.isdir(item_path):
                                    full_path += "/"
                                    if directories_only:
                                        matches.append(full_path)
                                    else:
                                        matches.append(full_path)
                                elif not directories_only:
                                    matches.append(full_path)
                            
                            # Filter by text match
                            return [match for match in matches if match.startswith(text)]
                    except Exception:
                        pass  # Fall back to placeholder matching
            
            # Handle other devices with placeholder content
            if device in self.directories:
                matches = []
                # Add directories
                for dir_name in self.directories[device]:
                    full_path = device + dir_name + "/"
                    if full_path.startswith(text):
                        matches.append(full_path)
                
                # Add files if not directory only
                if not directories_only:
                    for file_path in self.files:
                        if file_path.startswith(device):
                            file_name = file_path[len(device):]
                            if "/" not in file_name:  # Only direct children
                                full_path = device + file_name
                                if full_path.startswith(text):
                                    matches.append(full_path)
                
                return matches
        
        # Handle relative paths (no device specified)
        else:
            # For relative paths, we autocomplete with items in current directory
            matches = []
            
            # Handle DH0: with actual file system
            if self.current_dir.upper().startswith("DH0:"):
                # Check if we're running in WSL environment
                is_wsl = os.path.exists("/mnt/c")
                is_windows = platform.system() == "Windows"
                
                if is_wsl or is_windows:
                    try:
                        # Determine current directory path
                        if self.current_dir.upper() == "DH0:":
                            if is_wsl:
                                fs_path = "/mnt/c"
                            else:
                                fs_path = "C:\\"
                        else:
                            sub_path = self.current_dir[4:]  # Remove "DH0:" prefix
                            if sub_path.startswith("/"):
                                sub_path = sub_path[1:]
                            
                            if is_wsl:
                                fs_path = os.path.join("/mnt/c", sub_path.replace("\\", "/"))
                            else:
                                fs_path = os.path.join("C:\\", sub_path.replace("/", "\\"))
                        
                        # Normalize the path
                        fs_path = os.path.normpath(fs_path)
                        
                        if os.path.exists(fs_path) and os.path.isdir(fs_path):
                            items = os.listdir(fs_path)
                            for item in items:
                                item_path = os.path.join(fs_path, item)
                                if item.startswith(text):
                                    if os.path.isdir(item_path):
                                        matches.append(item + "/")
                                    elif not directories_only:
                                        matches.append(item)
                            return matches
                    except Exception:
                        pass  # Fall back to placeholder matching
            
            # Handle other devices with placeholder content
            # Add directories in current directory
            if self.current_dir in self.directories:
                for dir_name in self.directories[self.current_dir]:
                    if dir_name.startswith(text):
                        matches.append(dir_name + "/")
            
            # Add files in current directory if not directory only
            if not directories_only:
                for file_path in self.files:
                    if file_path.startswith(self.current_dir + "/"):
                        file_name = file_path[len(self.current_dir) + 1:]
                        if "/" not in file_name and file_name.startswith(text):  # Only direct children
                            matches.append(file_name)
            
            return matches
        
        return []
        
    def do_dir(self, arg):
        """DIR [path] - List directory contents"""
        if arg.strip():
            # List specific directory
            resolved_path = self._resolve_path(arg.strip())
            self._list_files(resolved_path)
        else:
            # List current directory
            self._list_files()
        
    def do_cd(self, arg):
        """CD <directory> - Change directory"""
        if not arg:
            print(f"Current directory: {self.current_dir}")
            return
            
        result = self._change_directory(arg)
        if result:
            print(result)
            
    def do_info(self, arg):
        """INFO - Display system information"""
        print(self._info_command())
        
    def do_avail(self, arg):
        """AVAIL - List available commands"""
        print(self._avail_command())
        
    def do_status(self, arg):
        """STATUS - Show system status"""
        print(self._status_command())
        
    def do_mount(self, arg):
        """MOUNT - Show mounted volumes or mount emulator shared folders
        
        Usage:
          MOUNT                                    - Show mounted volumes
          MOUNT <device> FROM WINUAE <config>     - Mount WinUAE shared folder
          MOUNT <device> FROM FS-UAE <config>     - Mount FS-UAE shared folder
          MOUNT LIST WINUAE                       - List WinUAE configurations
          MOUNT LIST FS-UAE                       - List FS-UAE configurations
          MOUNT UNMOUNT <device>                  - Unmount shared folder
        
        Examples:
          MOUNT SHARED: FROM WINUAE "My A1200 Config"
          MOUNT UAE0: FROM FS-UAE "Workbench31.fs-uae"
          MOUNT LIST WINUAE
          MOUNT UNMOUNT SHARED:
        """
        if not arg:
            # Show mounted volumes
            print(self._mount_command())
            return
        
        args = arg.split()
        if len(args) == 0:
            print(self._mount_command())
            return
        
        # Handle LIST commands
        if args[0].upper() == "LIST":
            if len(args) > 1 and args[1].upper() == "WINUAE":
                self._list_winuae_configs()
                return
            elif len(args) > 1 and args[1].upper() == "FS-UAE":
                self._list_fsuae_configs()
                return
            else:
                self._list_all_emulator_configs()
                return
        
        # Handle UNMOUNT commands
        if args[0].upper() == "UNMOUNT":
            if len(args) > 1:
                device = args[1]
                success, message = self.emulator_integration.unmount_shared_folder(device)
                print(message)
                if success:
                    # Remove from our directories
                    device = device.upper()
                    if not device.endswith(':'):
                        device += ':'
                    if device in self.directories:
                        del self.directories[device]
            else:
                print("Usage: MOUNT UNMOUNT <device>")
            return
        
        # Handle mount commands: DEVICE FROM EMULATOR CONFIG
        if len(args) >= 4 and args[1].upper() == "FROM":
            device = args[0]
            emulator_type = args[2]
            config_name = " ".join(args[3:]).strip('"')  # Handle quoted config names
            
            success, message = self.emulator_integration.mount_shared_folder(device, emulator_type, config_name)
            print(message)
            
            if success:
                # Add to our directories for navigation
                device = device.upper()
                if not device.endswith(':'):
                    device += ':'
                
                # Get the actual path and populate directory listing
                shared_path = self.emulator_integration.get_shared_folder_path(device)
                if shared_path and os.path.exists(shared_path):
                    try:
                        contents = os.listdir(shared_path)
                        self.directories[device] = [item for item in contents if os.path.isdir(os.path.join(shared_path, item))]
                    except Exception as e:
                        print(f"Warning: Could not read shared folder contents: {e}")
                        self.directories[device] = []
            return
        
        # If we get here, show usage
        print("Usage:")
        print("  MOUNT                                    - Show mounted volumes")
        print("  MOUNT <device> FROM WINUAE <config>     - Mount WinUAE shared folder")
        print("  MOUNT <device> FROM FS-UAE <config>     - Mount FS-UAE shared folder")
        print("  MOUNT LIST WINUAE                       - List WinUAE configurations")
        print("  MOUNT LIST FS-UAE                       - List FS-UAE configurations")
        print("  MOUNT UNMOUNT <device>                  - Unmount shared folder")
        print("")
        print("Examples:")
        print("  MOUNT SHARED: FROM WINUAE \"My A1200 Config\"")
        print("  MOUNT UAE0: FROM FS-UAE \"Workbench31.fs-uae\"")
        print("  MOUNT LIST WINUAE")
        print("  MOUNT UNMOUNT SHARED:")
        
    def do_echo(self, arg):
        """ECHO <text> - Echo text to terminal"""
        print(arg)
        
    def do_date(self, arg):
        """DATE - Show current date and time"""
        print(str(datetime.now()))
        
    def do_help(self, arg):
        """HELP - Display help information"""
        if arg:
            # Try to get help for specific command
            cmd_method = getattr(self, f"do_{arg.lower()}", None)
            if cmd_method and hasattr(cmd_method, '__doc__') and cmd_method.__doc__:
                print(cmd_method.__doc__)
            else:
                print(f"No help available for '{arg}'")
        else:
            print(self._help_command())
            
    def do_amiga(self, arg):
        """AMIGA - Amiga easter egg"""
        print(self._amiga_command())
        
    def do_ping(self, arg):
        """PING <host> - Network ping utility"""
        if not arg:
            print("Usage: PING <host> [COUNT=n]")
            print("Examples:")
            print("  PING google.com")
            print("  PING 8.8.8.8 COUNT=5")
            print("  PING 127.0.0.1 COUNT=1")
            return
            
        # Parse arguments (simple implementation)
        parts = arg.split()
        host = parts[0]
        count = 4  # Default ping count
        
        # Check for count parameter (PING host COUNT=n)
        for part in parts[1:]:
            if part.upper().startswith("COUNT="):
                try:
                    count = int(part.split("=")[1])
                    count = max(1, min(count, 10))  # Limit between 1-10
                except ValueError:
                    pass
        
        print(f"PING {host} ({count} packets):")
        print()
        
        # Perform actual ping
        success_count = 0
        total_time = 0
        
        for i in range(count):
            try:
                # Use system ping command
                if platform.system() == "Windows":
                    # Windows ping syntax
                    result = subprocess.run(
                        ["ping", "-n", "1", "-w", "3000", host],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                else:
                    # Unix/Linux ping syntax (WSL)
                    result = subprocess.run(
                        ["ping", "-c", "1", "-W", "3", host],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                
                if result.returncode == 0:
                    # Parse ping output for time
                    output = result.stdout
                    time_ms = self._parse_ping_time(output)
                    if time_ms:
                        print(f"Reply from {host}: bytes=32 time={time_ms}ms TTL=64")
                        success_count += 1
                        total_time += time_ms
                    else:
                        print(f"Reply from {host}: bytes=32 time<1ms TTL=64")
                        success_count += 1
                        total_time += 1
                else:
                    print(f"Request timeout for {host}")
                    
            except subprocess.TimeoutExpired:
                print(f"Request timeout for {host}")
            except FileNotFoundError:
                print(f"Ping command not available on this system")
                return
            except Exception as e:
                print(f"Ping failed: {e}")
            
            # Small delay between pings (except for last one)
            if i < count - 1:
                time.sleep(1)
        
        # Print summary
        print()
        lost_count = count - success_count
        loss_percent = (lost_count / count) * 100
        print(f"Ping statistics for {host}:")
        print(f"    Packets: Sent = {count}, Received = {success_count}, Lost = {lost_count} ({loss_percent:.0f}% loss)")
        
        if success_count > 0:
            avg_time = total_time / success_count
            print(f"Approximate round trip times in milli-seconds:")
            print(f"    Average = {avg_time:.0f}ms")
            
    def _parse_ping_time(self, ping_output):
        """Parse ping time from ping command output"""
        import re
        
        # Look for time patterns in ping output
        # Windows: "time<1ms" or "time=123ms"
        # Linux: "time=123 ms" or "time=123ms"
        patterns = [
            r'time[<=](\d+(?:\.\d+)?)ms',
            r'time[<=](\d+(?:\.\d+)?)\s*ms',
            r'time[<=](\d+(?:\.\d+)?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, ping_output, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        
        return None
        
    def do_winuae(self, arg):
        """WINUAE [config] - Launch WinUAE Amiga emulator"""
        # Display configuration information first
        print("WinUAE Integration for WSA Terminal")
        print("=" * 40)
        
        # Check if WinUAE executable exists
        winuae_exe = get_winuae_executable()
        if not winuae_exe:
            print("ERROR: WinUAE executable not found!")
            print()
            print("Please install WinUAE or set the WINUAE_PATH environment variable:")
            print("  set WINUAE_PATH=C:\\Path\\To\\Your\\winuae.exe")
            print()
            print("Common installation paths:")
            print("  C:\\Program Files\\WinUAE\\winuae.exe")
            print("  C:\\Program Files (x86)\\WinUAE\\winuae.exe")
            return
        
        print(f"WinUAE Executable: {winuae_exe}")
        
        # Handle different argument cases
        if not arg:
            # No arguments - show available configurations and launch default
            config_name = WINUAE_CONFIG['default_config']
            print(f"Using default configuration: {config_name}")
        elif arg.upper() == "LIST":
            # List available configurations
            configs = list_winuae_configs()
            if configs:
                print("\nAvailable WinUAE configurations:")
                for i, config in enumerate(configs, 1):
                    print(f"  {i:2}. {config}")
            else:
                print("\nNo configuration files found in:")
                print(f"  {WINUAE_CONFIG['config_dir']}")
            print()
            print("Usage: WINUAE [config_name]")
            print("       WINUAE LIST")
            print("       WINUAE CONFIG")
            return
        elif arg.upper() == "CONFIG":
            # Show configuration information
            print("\nWinUAE Configuration:")
            print(f"  Executable: {WINUAE_CONFIG['executable_path']}")
            print(f"  Config Dir: {WINUAE_CONFIG['config_dir']}")
            print(f"  Default Config: {WINUAE_CONFIG['default_config']}")
            print(f"  Kickstart Dir: {WINUAE_CONFIG['kickstart_dir']}")
            print(f"  HDF Dir: {WINUAE_CONFIG['hdf_dir']}")
            print()
            print("Set environment variables to customize paths:")
            print("  WINUAE_PATH - Path to winuae.exe")
            print("  WINUAE_CONFIG_DIR - Configuration directory")
            print("  WINUAE_DEFAULT_CONFIG - Default config file")
            print("  WINUAE_KICKSTART_DIR - Kickstart ROM directory")
            print("  WINUAE_HDF_DIR - Hard disk file directory")
            return
        else:
            # Specific configuration requested
            config_name = arg
            # Add .uae extension if not present
            if not config_name.lower().endswith('.uae'):
                config_name += '.uae'
        
        # Get full path to configuration file
        config_path = get_winuae_config_path(config_name)
        
        print(f"Configuration: {config_path}")
        
        # Check if configuration file exists
        if not os.path.exists(config_path):
            print(f"ERROR: Configuration file not found!")
            print()
            available_configs = list_winuae_configs()
            if available_configs:
                print("Available configurations:")
                for config in available_configs[:5]:  # Show first 5
                    print(f"  {config}")
                if len(available_configs) > 5:
                    print(f"  ... and {len(available_configs) - 5} more")
                print()
                print("Use 'WINUAE LIST' to see all configurations")
            else:
                print("No configuration files found. Please check your WinUAE installation.")
            return
        
        print()
        print("Launching WinUAE...")
        
        try:
            # Launch WinUAE with the configuration file
            # Use -f flag to specify configuration file
            cmd_args = [winuae_exe, "-f", config_path]
            
            # Launch as background process
            process = subprocess.Popen(
                cmd_args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if platform.system() == "Windows" else 0
            )
            
            print(f"WinUAE launched with PID {process.pid}")
            print(f"Configuration: {config_name}")
            print()
            print("WinUAE is running in the background.")
            print("You can continue using WSA Terminal while WinUAE is running.")
            
        except FileNotFoundError:
            print(f"ERROR: Could not launch WinUAE executable: {winuae_exe}")
        except Exception as e:
            print(f"ERROR: Failed to launch WinUAE: {e}")
        
    def do_say(self, arg):
        """SAY <text> [RATE=n] [VOICE=name] - Text-to-speech synthesis"""
        if not arg:
            print("Usage: SAY <text> [RATE=n] [VOICE=name]")
            print("Examples:")
            print("  SAY \"Hello from Amiga\"")
            print("  SAY \"Welcome to WSA Terminal\" RATE=150")
            print("  SAY \"Greetings\" VOICE=female")
            print("  SAY VOICES  (list available voices)")
            return
        
        # Check if user wants to list voices
        if arg.upper() == "VOICES":
            self._list_tts_voices()
            return
        
        # Parse arguments
        text_parts = []
        rate = None
        voice = None
        
        # Split arguments and extract RATE and VOICE parameters
        parts = arg.split()
        for part in parts:
            if part.upper().startswith("RATE="):
                try:
                    rate = int(part.split("=")[1])
                    rate = max(50, min(rate, 400))  # Limit between 50-400 WPM
                except ValueError:
                    print("SAY: Invalid rate value, using default")
            elif part.upper().startswith("VOICE="):
                voice = part.split("=")[1].lower()
            else:
                text_parts.append(part)
        
        # Join remaining parts as text to speak
        text_to_speak = " ".join(text_parts)
        
        # Remove quotes if present
        if text_to_speak.startswith('"') and text_to_speak.endswith('"'):
            text_to_speak = text_to_speak[1:-1]
        elif text_to_speak.startswith("'") and text_to_speak.endswith("'"):
            text_to_speak = text_to_speak[1:-1]
        
        if not text_to_speak:
            print("SAY: No text specified")
            return
        
        print(f"Speaking: \"{text_to_speak}\"")
        
        # Try different TTS engines based on platform
        success = False
        
        # Try Windows SAPI (Speech API)
        if platform.system() == "Windows":
            success = self._say_windows_sapi(text_to_speak, rate, voice)
        
        # Try espeak (cross-platform, common on Linux/WSL)
        if not success:
            success = self._say_espeak(text_to_speak, rate, voice)
        
        # Try festival (another Linux TTS engine)
        if not success:
            success = self._say_festival(text_to_speak, rate, voice)
        
        # Try say command (macOS)
        if not success and platform.system() == "Darwin":
            success = self._say_macos(text_to_speak, rate, voice)
        
        # Try pyttsx3 (Python TTS library)
        if not success:
            success = self._say_pyttsx3(text_to_speak, rate, voice)
        
        if not success:
            print("SAY: Text-to-speech not available on this system")
            print("Try installing: espeak, festival, or pyttsx3")
    
    def _list_tts_voices(self):
        """List available TTS voices"""
        print("Available Text-to-Speech Voices:")
        print("=" * 35)
        
        voices_found = False
        
        # Try to list Windows SAPI voices
        if platform.system() == "Windows":
            try:
                result = subprocess.run(
                    ["powershell", "-Command", 
                     "Add-Type -AssemblyName System.Speech; " +
                     "(New-Object System.Speech.Synthesis.SpeechSynthesizer).GetInstalledVoices() | " +
                     "ForEach-Object { $_.VoiceInfo.Name + ' (' + $_.VoiceInfo.Culture + ')' }"],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0 and result.stdout.strip():
                    print("Windows SAPI Voices:")
                    for line in result.stdout.strip().split('\n'):
                        if line.strip():
                            print(f"  {line.strip()}")
                    voices_found = True
                    print()
            except Exception:
                pass
        
        # Try to list espeak voices
        try:
            result = subprocess.run(["espeak", "--voices"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("eSpeak Voices:")
                lines = result.stdout.strip().split('\n')
                for line in lines[1:6]:  # Show first 5 voices
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 4:
                            print(f"  {parts[3]} ({parts[1]})")
                voices_found = True
                print()
        except Exception:
            pass
        
        # Try to list festival voices
        try:
            result = subprocess.run(["festival", "--help"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("Festival: Available (use default voice)")
                voices_found = True
                print()
        except Exception:
            pass
        
        if not voices_found:
            print("No TTS engines detected.")
            print("Try installing:")
            print("  Windows: Built-in SAPI voices")
            print("  Linux/WSL: sudo apt install espeak espeak-data")
            print("  Python: pip install pyttsx3")
    
    def _say_windows_sapi(self, text, rate=None, voice=None):
        """Use Windows SAPI for text-to-speech"""
        try:
            # Build PowerShell command for Windows Speech API
            ps_cmd = [
                "powershell", "-Command",
                "Add-Type -AssemblyName System.Speech; " +
                "$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            ]
            
            # Set rate if specified
            if rate:
                ps_cmd[2] += f"$synth.Rate = {max(-10, min(10, (rate - 200) // 20))}; "
            
            # Set voice if specified
            if voice:
                ps_cmd[2] += f"try {{ $synth.SelectVoice((Get-WmiObject Win32_CDROMDrive | Where-Object {{$_.Caption -like '*{voice}*'}})); }} catch {{ }}; "
            
            # Speak the text
            ps_cmd[2] += f"$synth.Speak('{text.replace(chr(39), chr(39)+chr(39))}'); $synth.Dispose()"
            
            result = subprocess.run(ps_cmd, capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except Exception:
            return False
    
    def _say_espeak(self, text, rate=None, voice=None):
        """Use espeak for text-to-speech"""
        try:
            cmd = ["espeak"]
            
            # Set rate (words per minute)
            if rate:
                cmd.extend(["-s", str(rate)])
            else:
                cmd.extend(["-s", "175"])  # Default Amiga-like rate
            
            # Set voice
            if voice:
                # Map common voice names to espeak voices
                voice_map = {
                    "male": "en+m3",
                    "female": "en+f3",
                    "robot": "en+whisper",
                    "amiga": "en+m2"  # Retro computer-like voice
                }
                espeak_voice = voice_map.get(voice, voice)
                cmd.extend(["-v", espeak_voice])
            else:
                cmd.extend(["-v", "en+m2"])  # Default to male voice 2
            
            # Add the text
            cmd.append(text)
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except Exception:
            return False
    
    def _say_festival(self, text, rate=None, voice=None):
        """Use festival for text-to-speech"""
        try:
            # Festival uses a different approach - pipe text to it
            cmd = ["festival", "--tts"]
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, text=True, timeout=30)
            process.communicate(input=text)
            return process.returncode == 0
        except Exception:
            return False
    
    def _say_macos(self, text, rate=None, voice=None):
        """Use macOS say command"""
        try:
            cmd = ["say"]
            
            if rate:
                cmd.extend(["-r", str(rate)])
            
            if voice:
                cmd.extend(["-v", voice])
            
            cmd.append(text)
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except Exception:
            return False
    
    def _say_pyttsx3(self, text, rate=None, voice=None):
        """Use pyttsx3 Python library for text-to-speech"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            
            if rate:
                engine.setProperty('rate', rate)
            
            if voice:
                voices = engine.getProperty('voices')
                for v in voices:
                    if voice.lower() in v.name.lower():
                        engine.setProperty('voice', v.id)
                        break
            
            engine.say(text)
            engine.runAndWait()
            engine.stop()
            return True
        except ImportError:
            return False
        except Exception:
            return False
        
    def do_pattern(self, arg):
        """PATTERN <pattern> - Pattern matching utility"""
        if not arg:
            print("""Usage: PATTERN <pattern>
Examples:
  PATTERN #?        (matches single character files)
  PATTERN ~pattern  (matches files starting with pattern)
  PATTERN *         (matches all files)""")
            return
            
        print(self._pattern_command(arg.split()))
        
    def do_guru(self, arg):
        """GURU - Display Guru Meditation error (Press Ctrl+C to stop)"""
        self._guru_meditation_demo()
        
    def do_ed(self, arg):
        """ED <filename> - Text editor"""
        if not arg:
            print("ED: No filename specified")
            print("Usage: ED <filename>")
            print("Type 'ED HELP' for editor commands")
            return
            
        if arg.upper() == "HELP":
            self._ed_help()
            return
            
        # Handle file path
        file_path = self._resolve_file_path(arg)
        if not file_path:
            print(f"ED: Cannot create file '{arg}'")
            return
            
        # Try to read existing file content
        content = []
        if file_path in self.files:
            content = self.files[file_path].split('\n')
        elif file_path.startswith("DH0:") and platform.system() == "Windows":
            # Try to read from actual file system
            try:
                fs_path = self._get_fs_path(file_path)
                if fs_path and os.path.exists(fs_path):
                    with open(fs_path, 'r') as f:
                        content = f.read().splitlines()
            except Exception:
                pass  # File doesn't exist or can't be read, start with empty content
        
        # Run the editor
        self._ed_editor(file_path, content)
        
    def do_type(self, arg):
        """TYPE <file> - Display file contents"""
        if not arg:
            print("TYPE: No file specified")
            print("Usage: TYPE <file>")
            return
            
        # Resolve the file path
        file_path = self._resolve_file_path(arg)
        
        # Try to find the file in virtual file system first
        if file_path in self.files:
            content = self.files[file_path]
            print(content)
            return
            
        # Try to find the file in actual file system (for DH0:)
        if file_path.startswith("DH0:"):
            # Check if we're running in WSL environment
            is_wsl = os.path.exists("/mnt/c")
            is_windows = platform.system() == "Windows"
            
            if is_wsl or is_windows:
                try:
                    sub_path = file_path[4:]  # Remove "DH0:" prefix
                    if sub_path.startswith("/"):
                        sub_path = sub_path[1:]
                    
                    if is_wsl:
                        fs_path = os.path.join("/mnt/c", sub_path.replace("\\", "/"))
                    else:
                        fs_path = os.path.join("C:\\", sub_path.replace("/", "\\"))
                    
                    # Normalize the path
                    fs_path = os.path.normpath(fs_path)
                    
                    if os.path.exists(fs_path) and os.path.isfile(fs_path):
                        try:
                            with open(fs_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            print(content)
                            return
                        except UnicodeDecodeError:
                            # Try with different encoding for binary files
                            try:
                                with open(fs_path, 'r', encoding='latin-1') as f:
                                    content = f.read()
                                print(content)
                                return
                            except Exception:
                                print(f"TYPE: Cannot read file '{arg}' - binary file or encoding error")
                                return
                        except Exception as e:
                            print(f"TYPE: Error reading file '{arg}': {e}")
                            return
                    else:
                        print(f"TYPE: File '{arg}' not found")
                        return
                except Exception as e:
                    print(f"TYPE: Error accessing file '{arg}': {e}")
                    return
                    
        print(f"TYPE: File '{arg}' not found")
        
    def do_copy(self, arg):
        """COPY <source> <dest> - Copy files"""
        if not arg:
            print("COPY: No arguments specified")
            print("Usage: COPY <source> <destination>")
            return
            
        args = arg.split()
        if len(args) < 2:
            print("COPY: Missing destination")
            print("Usage: COPY <source> <destination>")
            return
            
        source_file = args[0]
        dest_file = args[1]
        
        # Resolve paths
        source_path = self._resolve_file_path(source_file)
        dest_path = self._resolve_file_path(dest_file)
        
        # Read source file
        source_content = None
        
        # Try virtual file system first
        if source_path in self.files:
            source_content = self.files[source_path]
        # Try real file system for DH0:
        elif source_path.startswith("DH0:"):
            source_content = self._read_real_file(source_path)
            if source_content is None:
                print(f"COPY: Cannot read source file '{source_file}'")
                return
        else:
            print(f"COPY: Source file '{source_file}' not found")
            return
            
        # Write to destination
        if dest_path.startswith("DH0:"):
            # Write to real file system
            if self._write_real_file(dest_path, source_content):
                print(f"COPY: '{source_file}' copied to '{dest_file}'")
            else:
                print(f"COPY: Failed to copy to '{dest_file}'")
        else:
            # Write to virtual file system
            self.files[dest_path] = source_content
            print(f"COPY: '{source_file}' copied to '{dest_file}'")
            
    def do_delete(self, arg):
        """DELETE <file> - Delete files"""
        if not arg:
            print("DELETE: No file specified")
            print("Usage: DELETE <file>")
            return
            
        # Resolve the file path
        file_path = self._resolve_file_path(arg)
        
        # Check if file exists
        file_exists = False
        is_real_file = False
        
        # Check virtual file system
        if file_path in self.files:
            file_exists = True
        # Check real file system for DH0:
        elif file_path.startswith("DH0:"):
            if self._real_file_exists(file_path):
                file_exists = True
                is_real_file = True
                
        if not file_exists:
            print(f"DELETE: File '{arg}' not found")
            return
            
        # Confirm deletion
        try:
            response = input(f"Delete '{arg}' (y/N)? ").strip().lower()
            if response not in ['y', 'yes']:
                print("DELETE: Operation cancelled")
                return
        except KeyboardInterrupt:
            print("\nDELETE: Operation cancelled")
            return
            
        # Perform deletion
        if is_real_file:
            if self._delete_real_file(file_path):
                print(f"DELETE: File '{arg}' deleted")
            else:
                print(f"DELETE: Failed to delete '{arg}'")
        else:
            del self.files[file_path]
            print(f"DELETE: File '{arg}' deleted")

    def do_makedir(self, arg):
        """Create a new directory - MAKEDIR <directory_name>"""
        if not arg.strip():
            print("MAKEDIR: No directory name specified")
            print("Usage: MAKEDIR <directory_name>")
            return
            
        dir_name = arg.strip()
        
        # Check if this is a real filesystem path (DH0:)
        if dir_name.startswith("DH0:"):
            if self._create_real_directory(dir_name):
                print(f"MAKEDIR: Directory '{dir_name}' created")
            else:
                print(f"MAKEDIR: Failed to create directory '{dir_name}'")
        else:
            # Handle virtual filesystem directories
            # Resolve relative paths
            current_dir = self.current_dir
            if not dir_name.startswith(('SYS:', 'RAM:', 'C:', 'DH0:')):
                # It's a relative path
                if current_dir.endswith(':'):
                    dir_path = current_dir + dir_name
                else:
                    dir_path = current_dir + '/' + dir_name
            else:
                dir_path = dir_name
                
            # Add to virtual directories
            if dir_path not in self.directories:
                # Add the new directory as a new key with empty subdirectories list
                self.directories[dir_path] = []
                print(f"MAKEDIR: Directory '{dir_name}' created")
                
                # Also add it to the parent directory's subdirectory list
                parent_dir = current_dir
                if parent_dir in self.directories:
                    if dir_name not in self.directories[parent_dir]:
                        self.directories[parent_dir].append(dir_name)
            else:
                print(f"MAKEDIR: Directory '{dir_name}' already exists")

    def _create_real_directory(self, amiga_path):
        """Create a real directory on DH0: path"""
        if not amiga_path.startswith("DH0:"):
            return False
            
        # Check if we're running in WSL environment
        is_wsl = os.path.exists("/mnt/c")
        is_windows = platform.system() == "Windows"
        
        if not (is_wsl or is_windows):
            return False
            
        try:
            sub_path = amiga_path[4:]  # Remove "DH0:" prefix
            if sub_path.startswith("/"):
                sub_path = sub_path[1:]
            
            if is_wsl:
                # WSL environment - use /mnt/c
                fs_path = f"/mnt/c/{sub_path}"
            else:
                # Windows environment - use C:\
                fs_path = f"C:\\{sub_path}"
                
            # Convert forward slashes to appropriate path separators
            if is_wsl:
                fs_path = fs_path.replace("\\", "/")
            else:
                fs_path = fs_path.replace("/", "\\")
                
            # Create the directory
            os.makedirs(fs_path, exist_ok=True)
            return True
            
        except Exception as e:
            print(f"MAKEDIR: Error creating directory - {str(e)}")
            return False

    def _read_real_file(self, amiga_path):
        """Read a real file from DH0: path"""
        if not amiga_path.startswith("DH0:"):
            return None
            
        # Check if we're running in WSL environment
        is_wsl = os.path.exists("/mnt/c")
        is_windows = platform.system() == "Windows"
        
        if not (is_wsl or is_windows):
            return None
            
        try:
            sub_path = amiga_path[4:]  # Remove "DH0:" prefix
            if sub_path.startswith("/"):
                sub_path = sub_path[1:]
            
            if is_wsl:
                fs_path = os.path.join("/mnt/c", sub_path.replace("\\", "/"))
            else:
                fs_path = os.path.join("C:\\", sub_path.replace("/", "\\"))
            
            # Normalize the path
            fs_path = os.path.normpath(fs_path)
            
            if os.path.exists(fs_path) and os.path.isfile(fs_path):
                with open(fs_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception:
            try:
                # Try with different encoding
                with open(fs_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception:
                pass
        return None
        
    def _write_real_file(self, amiga_path, content):
        """Write content to a real file at DH0: path"""
        if not amiga_path.startswith("DH0:"):
            return False
            
        # Check if we're running in WSL environment
        is_wsl = os.path.exists("/mnt/c")
        is_windows = platform.system() == "Windows"
        
        if not (is_wsl or is_windows):
            return False
            
        try:
            sub_path = amiga_path[4:]  # Remove "DH0:" prefix
            if sub_path.startswith("/"):
                sub_path = sub_path[1:]
            
            if is_wsl:
                fs_path = os.path.join("/mnt/c", sub_path.replace("\\", "/"))
            else:
                fs_path = os.path.join("C:\\", sub_path.replace("/", "\\"))
            
            # Normalize the path
            fs_path = os.path.normpath(fs_path)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(fs_path), exist_ok=True)
            
            with open(fs_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception:
            return False
            
    def _real_file_exists(self, amiga_path):
        """Check if a real file exists at DH0: path"""
        if not amiga_path.startswith("DH0:"):
            return False
            
        # Check if we're running in WSL environment
        is_wsl = os.path.exists("/mnt/c")
        is_windows = platform.system() == "Windows"
        
        if not (is_wsl or is_windows):
            return False
            
        try:
            sub_path = amiga_path[4:]  # Remove "DH0:" prefix
            if sub_path.startswith("/"):
                sub_path = sub_path[1:]
            
            if is_wsl:
                fs_path = os.path.join("/mnt/c", sub_path.replace("\\", "/"))
            else:
                fs_path = os.path.join("C:\\", sub_path.replace("/", "\\"))
            
            # Normalize the path
            fs_path = os.path.normpath(fs_path)
            
            return os.path.exists(fs_path) and os.path.isfile(fs_path)
        except Exception:
            return False
            
    def _delete_real_file(self, amiga_path):
        """Delete a real file at DH0: path"""
        if not amiga_path.startswith("DH0:"):
            return False
            
        # Check if we're running in WSL environment
        is_wsl = os.path.exists("/mnt/c")
        is_windows = platform.system() == "Windows"
        
        if not (is_wsl or is_windows):
            return False
            
        try:
            sub_path = amiga_path[4:]  # Remove "DH0:" prefix
            if sub_path.startswith("/"):
                sub_path = sub_path[1:]
            
            if is_wsl:
                fs_path = os.path.join("/mnt/c", sub_path.replace("\\", "/"))
            else:
                fs_path = os.path.join("C:\\", sub_path.replace("/", "\\"))
            
            # Normalize the path
            fs_path = os.path.normpath(fs_path)
            
            if os.path.exists(fs_path) and os.path.isfile(fs_path):
                os.remove(fs_path)
                return True
        except Exception:
            return False
        return False
        
    def _format_amiga_date(self, timestamp=None, file_path=None, full_format=False):
        """Format date in Amiga style"""
        try:
            if file_path and os.path.exists(file_path):
                # Get actual file modification time
                timestamp = os.path.getmtime(file_path)
            elif timestamp is None:
                # Use current time for virtual files
                timestamp = datetime.now().timestamp()
            
            dt = datetime.fromtimestamp(timestamp)
            if full_format:
                # Full Amiga format: DD-MMM-YY HH:MM:SS
                return dt.strftime("%d-%b-%y %H:%M:%S")
            else:
                # Short format: DD-MMM-YY (e.g., "15-Sep-25")
                return dt.strftime("%d-%b-%y")
        except Exception:
            # Fallback to Amiga release date
            if full_format:
                return "01-Jan-85 12:00:00"
            else:
                return "01-Jan-85"
    
    def _list_shared_folder_files(self, path, device):
        """List files in emulator shared folder with Amiga DIR command format"""
        shared_info = self.emulator_integration.mounted_shared_folders[device]
        base_path = shared_info['path']
        
        # Determine the actual file system path
        if path == device:
            fs_path = base_path
        else:
            # Handle subdirectories within the shared folder
            sub_path = path[len(device):]
            if sub_path.startswith('/'):
                sub_path = sub_path[1:]
            fs_path = os.path.join(base_path, sub_path.replace('/', os.sep))
        
        fs_path = os.path.normpath(fs_path)
        
        if not os.path.exists(fs_path) or not os.path.isdir(fs_path):
            print(f"Directory {path} not found.")
            return
        
        try:
            # Authentic Amiga DIR header
            day_name = self._format_amiga_day(file_path=fs_path)
            header_date = self._format_amiga_date(file_path=fs_path)
            emulator = shared_info['emulator'].upper()
            config = shared_info['config']
            print(f'Directory "{path}" on {day_name} {header_date}')
            print(f'({emulator} Shared Folder: "{shared_info["label"]}" from {config})')
            
            # List directory contents
            try:
                items = os.listdir(fs_path)
            except PermissionError:
                print("Access denied to this directory.")
                return
            except Exception as e:
                print(f"Error reading directory: {e}")
                return
            
            dirs = []
            files = []
            
            # Separate directories and files
            for item in items:
                item_path = os.path.join(fs_path, item)
                try:
                    if os.path.isdir(item_path):
                        dirs.append(item)
                    else:
                        files.append(item)
                except:
                    # If we can't access the item, treat it as a file
                    files.append(item)
            
            # Sort directories and files
            dirs.sort(key=str.lower)
            files.sort(key=str.lower)
            
            # Print directories first (authentic Amiga format)
            for dir_name in dirs:
                dir_path = os.path.join(fs_path, dir_name)
                date_str = self._format_amiga_date(file_path=dir_path, full_format=True)
                print(f" {dir_name:<22} (dir)    ----rwed     {date_str}")
            
            # Print files (authentic Amiga format)  
            total_bytes = 0
            for file_name in files:
                file_path = os.path.join(fs_path, file_name)
                try:
                    file_size = os.path.getsize(file_path)
                    total_bytes += file_size
                except:
                    file_size = 0
                date_str = self._format_amiga_date(file_path=file_path, full_format=True)
                print(f" {file_name:<22} {file_size:>7}  ----rwed     {date_str}")
            
            dir_count = len(dirs)
            file_count = len(files)
            access_note = " (Read-Only)" if shared_info['access'] == 'ro' else ""
            print(f"{dir_count + file_count} files - {dir_count} directories - {total_bytes} bytes used{access_note}")
            
        except Exception as e:
            print(f"Error accessing shared folder {path}: {e}")

    def _format_amiga_day(self, timestamp=None, file_path=None):
        """Format day of week in Amiga style"""
        try:
            if file_path and os.path.exists(file_path):
                timestamp = os.path.getmtime(file_path)
            elif timestamp is None:
                timestamp = datetime.now().timestamp()
            
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%A")  # Full day name
        except Exception:
            return "Monday"
        
    def _ed_help(self):
        """Display ED editor help"""
        print("""WSA Terminal ED Text Editor Commands:
  
  Just type text and press ENTER to add lines to the file.
  
  Special Commands:
    LIST    - Show all lines in the file
    SAVE    - Save the file
    QUIT    - Exit without saving
    
  To exit the editor:
    Press Ctrl+C and choose whether to save
    
  Examples:
    1> echo "This is line 1"    (adds text to the file)
    2> LIST                     (shows all lines)
    3> SAVE                     (saves the file)
    4> QUIT                     (exits without saving)
""")
        
    def _resolve_file_path(self, filename):
        """Resolve filename to full path"""
        # Handle absolute paths
        if ":" in filename:
            return filename
            
        # Handle relative paths
        if self.current_dir.endswith(":"):
            return f"{self.current_dir}{filename}"
        else:
            return f"{self.current_dir}/{filename}"
            
    def _get_fs_path(self, amiga_path):
        """Convert Amiga path to filesystem path for DH0:"""
        if amiga_path.startswith("DH0:"):
            sub_path = amiga_path[4:]  # Remove "DH0:" prefix
            if sub_path.startswith("/"):
                sub_path = sub_path[1:]
            return os.path.join("C:\\", sub_path.replace("/", "\\"))
        return None
        
    def _ed_editor(self, file_path, content):
        """Simple line-based text editor implementation"""
        print(f"Editing '{file_path}'")
        print("Enter lines of text. Press Ctrl+C to exit editor.")
        print("Commands: LIST (show lines), SAVE (save file), QUIT (exit without saving)")
        print()
        
        # Make a copy of the content for editing
        if content and len(content) > 0:
            lines = content.copy()
        else:
            lines = []
        
        # Display initial content
        if lines:
            print("Current file contents:")
            for i, line in enumerate(lines, 1):
                print(f"{i:3}: {line}")
            print()
        else:
            print("Empty file - start typing to add content.")
            print()
        
        while True:
            try:
                line_input = input(f"{len(lines)+1:3}> ")
                
                # Handle editor commands
                cmd = line_input.upper().strip()
                if cmd == "LIST":
                    if lines:
                        print("\nCurrent contents:")
                        for i, line in enumerate(lines, 1):
                            print(f"{i:3}: {line}")
                        print()
                    else:
                        print("File is empty.")
                elif cmd == "SAVE":
                    # Save content
                    content_str = '\n'.join(lines)
                    
                    # Check if this is a real file (DH0:) or virtual file
                    if file_path.startswith("DH0:"):
                        # Save to actual file system
                        try:
                            # Check if we're running in WSL environment
                            is_wsl = os.path.exists("/mnt/c")
                            is_windows = platform.system() == "Windows"
                            
                            if is_wsl or is_windows:
                                sub_path = file_path[4:]  # Remove "DH0:" prefix
                                if sub_path.startswith("/"):
                                    sub_path = sub_path[1:]
                                
                                if is_wsl:
                                    fs_path = os.path.join("/mnt/c", sub_path.replace("\\", "/"))
                                else:
                                    fs_path = os.path.join("C:\\", sub_path.replace("/", "\\"))
                                
                                # Normalize the path
                                fs_path = os.path.normpath(fs_path)
                                
                                # Create directory if needed
                                fs_dir = os.path.dirname(fs_path)
                                if fs_dir and not os.path.exists(fs_dir):
                                    os.makedirs(fs_dir)
                                
                                with open(fs_path, 'w', encoding='utf-8') as f:
                                    f.write(content_str)
                                print(f"File saved to {fs_path}")
                            else:
                                print("DH0: access not available on this system")
                        except Exception as e:
                            print(f"Error saving file: {e}")
                    else:
                        # Save to virtual file system
                        self.files[file_path] = content_str
                        print("File saved to virtual filesystem.")
                elif cmd == "QUIT":
                    print("Editor exited without saving.")
                    return
                elif cmd == "":
                    # Empty line - add blank line to file
                    lines.append("")
                else:
                    # Regular line input - add to file
                    lines.append(line_input)
                        
            except KeyboardInterrupt:
                print("\n")
                # Ask if user wants to save before exiting
                try:
                    save_choice = input("Save changes before exiting? (y/N): ").strip().lower()
                    if save_choice in ['y', 'yes']:
                        # Save content
                        content_str = '\n'.join(lines)
                        
                        if file_path.startswith("DH0:"):
                            # Save to actual file system
                            try:
                                # Check if we're running in WSL environment
                                is_wsl = os.path.exists("/mnt/c")
                                is_windows = platform.system() == "Windows"
                                
                                if is_wsl or is_windows:
                                    sub_path = file_path[4:]  # Remove "DH0:" prefix
                                    if sub_path.startswith("/"):
                                        sub_path = sub_path[1:]
                                    
                                    if is_wsl:
                                        fs_path = os.path.join("/mnt/c", sub_path.replace("\\", "/"))
                                    else:
                                        fs_path = os.path.join("C:\\", sub_path.replace("/", "\\"))
                                    
                                    # Normalize the path
                                    fs_path = os.path.normpath(fs_path)
                                    
                                    # Create directory if needed
                                    fs_dir = os.path.dirname(fs_path)
                                    if fs_dir and not os.path.exists(fs_dir):
                                        os.makedirs(fs_dir)
                                    
                                    with open(fs_path, 'w', encoding='utf-8') as f:
                                        f.write(content_str)
                                    print(f"File saved to {fs_path}")
                            except Exception as e:
                                print(f"Error saving file: {e}")
                        else:
                            # Save to virtual file system
                            self.files[file_path] = content_str
                            print("File saved.")
                    print("Editor exited.")
                except KeyboardInterrupt:
                    print("\nEditor exited without saving.")
                return
            except EOFError:
                print("\nEditor exited.")
                return
                
    def do_cls(self, arg):
        """CLS - Clear screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def do_clear(self, arg):
        """CLEAR - Clear screen"""
        self.do_cls(arg)
        
    def do_test(self, arg):
        """TEST - Run a simple test to verify functionality"""
        print("WSA Terminal Console is working correctly!")
        print(f"Current directory: {self.current_dir}")
        print(f"Available directories: {', '.join(self.directories.keys())}")
        
    def do_exit(self, arg):
        """EXIT - Exit the terminal"""
        print("Goodbye!")
        return True
        
    def do_quit(self, arg):
        """QUIT - Exit the terminal"""
        return self.do_exit(arg)
        
    def default(self, line):
        """Handle unknown commands"""
        # Check if it's a device name (ends with :)
        if line and line.upper().endswith(':'):
            device = line.upper()
            if device in self.directories:
                result = self._change_directory(line)
                if result:
                    print(result)
                return
        print(f"Command '{line.split()[0]}' not found. Type 'help' for available commands.")
        
    def do_execute(self, arg):
        """EXECUTE <script> - Execute a script file"""
        if not arg:
            print("EXECUTE: No script specified")
            print("Usage: EXECUTE <script>")
            return
            
        # Resolve the script path
        script_path = self._resolve_file_path(arg)
        
        # Try to find the script in virtual file system
        if script_path in self.files:
            content = self.files[script_path]
            self._run_startup_script(script_path, content)
            return
            
        # Try to find the script in actual file system (for DH0:)
        if script_path.startswith("DH0:") and platform.system() == "Windows":
            try:
                fs_path = self._get_fs_path(script_path)
                if fs_path and os.path.exists(fs_path):
                    with open(fs_path, 'r') as f:
                        content = f.read()
                    self._run_startup_script(script_path, content)
                    return
            except Exception as e:
                print(f"Error reading script: {e}")
                
        print(f"Script '{arg}' not found")

    def _resolve_path(self, path):
        """Resolve a relative or absolute path against current directory"""
        if not path:
            return self.current_dir
            
        # Handle absolute paths (with device:)
        if ":" in path:
            # Handle logical assignments (common Amiga directory shortcuts)
            logical_assignments = {
                "S:": "SYS:S",
                "L:": "SYS:L", 
                "DEVS:": "SYS:DEVS",
                "FONTS:": "SYS:Fonts",
                "T:": "RAM:T"
            }
            
            # Check if this is a logical assignment
            path_upper = path.upper()
            for logical, actual in logical_assignments.items():
                if path_upper.startswith(logical):
                    # Replace the logical assignment with the actual path
                    remaining_path = path[len(logical):]
                    if remaining_path:
                        return f"{actual}/{remaining_path}"
                    else:
                        return actual
            
            return path
            
        # Handle relative paths
        if self.current_dir.upper() == "DH0:":
            return f"DH0:/{path}"
        elif self.current_dir.upper().startswith("DH0:"):
            return f"{self.current_dir}/{path}"
        elif self.current_dir.endswith(":"):
            return f"{self.current_dir}{path}"
        else:
            return f"{self.current_dir}/{path}"

    def _list_files(self, path=None):
        """List files in directory with Amiga DIR command format"""
        if path is None:
            path = self.current_dir
        else:
            # Resolve relative paths
            path = self._resolve_path(path)
        
        # Check if this is a mounted emulator shared folder
        device = path.split('/')[0] if '/' in path else path
        device = device.upper()
        if not device.endswith(':'):
            device += ':'
        
        if device in self.emulator_integration.mounted_shared_folders:
            return self._list_shared_folder_files(path, device)
            
        # Handle DH0: (Windows C: drive) with actual file system access
        if path.upper().startswith("DH0:"):
            # Check if we're running in WSL environment
            is_wsl = os.path.exists("/mnt/c")
            is_windows = platform.system() == "Windows"
            
            if is_wsl or is_windows:
                try:
                    # Determine the actual file system path
                    if path.upper() == "DH0:":
                        if is_wsl:
                            fs_path = "/mnt/c"
                        else:
                            fs_path = "C:\\"
                    else:
                        # Extract subdirectory path from DH0:subdir format
                        sub_path = path[4:]  # Remove "DH0:" prefix
                        if sub_path.startswith("/"):
                            sub_path = sub_path[1:]
                        
                        if is_wsl:
                            fs_path = os.path.join("/mnt/c", sub_path.replace("\\", "/"))
                        else:
                            fs_path = os.path.join("C:\\", sub_path.replace("/", "\\"))
                    
                    # Normalize the path
                    fs_path = os.path.normpath(fs_path)
                    
                    if os.path.exists(fs_path) and os.path.isdir(fs_path):
                        # Authentic Amiga DIR header with day and date
                        day_name = self._format_amiga_day(file_path=fs_path)
                        header_date = self._format_amiga_date(file_path=fs_path)
                        print(f'Directory "{path}" on {day_name} {header_date}')
                        
                        # List actual directories and files in the path
                        try:
                            items = os.listdir(fs_path)
                        except PermissionError:
                            print("Access denied to this directory.")
                            return
                        except Exception as e:
                            print(f"Error reading directory: {e}")
                            return
                        
                        dirs = []
                        files = []
                        
                        # Separate directories and files
                        for item in items:
                            item_path = os.path.join(fs_path, item)
                            try:
                                if os.path.isdir(item_path):
                                    dirs.append(item)
                                else:
                                    files.append(item)
                            except:
                                # If we can't access the item, treat it as a file
                                files.append(item)
                                
                        # Sort directories and files
                        dirs.sort(key=str.lower)
                        files.sort(key=str.lower)
                        
                        # Print directories first (authentic Amiga format)
                        for dir_name in dirs:
                            dir_path = os.path.join(fs_path, dir_name)
                            date_str = self._format_amiga_date(file_path=dir_path, full_format=True)
                            print(f" {dir_name:<22} (dir)    ----rwed     {date_str}")
                            
                        # Print files (authentic Amiga format)
                        for file_name in files:
                            file_path = os.path.join(fs_path, file_name)
                            try:
                                file_size = os.path.getsize(file_path)
                            except:
                                file_size = 0
                            date_str = self._format_amiga_date(file_path=file_path, full_format=True)
                            print(f" {file_name:<22} {file_size:>7}  ----rwed     {date_str}")
                            
                        dir_count = len(dirs)
                        file_count = len(files)
                        total_bytes = sum(os.path.getsize(os.path.join(fs_path, f)) 
                                        for f in files 
                                        if os.path.isfile(os.path.join(fs_path, f)))
                        print(f"{dir_count + file_count} files - {dir_count} directories - {total_bytes} bytes used")
                        return
                    else:
                        print(f"Directory {path} not found.")
                        return
                except Exception as e:
                    print(f"Error accessing directory {path}: {e}")
                    # Fall back to placeholder content if there's an error
                    pass
            
            # Fallback to placeholder content
            day_name = self._format_amiga_day()
            header_date = self._format_amiga_date()
            print(f'Directory "{path}" on {day_name} {header_date}')
            
            # List directories (authentic Amiga format)
            dirs = self.directories.get(path, [])
            for dir_name in dirs:
                date_str = self._format_amiga_date(full_format=True)  # Use current time for virtual dirs
                print(f" {dir_name:<22} (dir)    ----rwed     {date_str}")
                
            # List files in current directory
            file_count = 0
            for file_path in self.files:
                if file_path.startswith(path + "/"):
                    file_name = file_path[len(path) + 1:]
                    if "/" not in file_name:  # Only direct children
                        file_content = self.files[file_path]
                        file_size = len(file_content)
                        date_str = self._format_amiga_date(full_format=True)  # Use current time for virtual files
                        print(f" {file_name:<22} {file_size:>7}  ----rwed     {date_str}")
                        file_count += 1
                        
            total_files = len(dirs) + file_count
            total_bytes = sum(len(self.files[fp]) for fp in self.files if fp.startswith(path + "/") and "/" not in fp[len(path) + 1:])
            print(f"{total_files} files - {len(dirs)} directories - {total_bytes} bytes used")
            return
            
        # Special case for C: directory - show commands as executable files, not directories  
        if path == "C:":
            day_name = self._format_amiga_day()
            header_date = self._format_amiga_date()
            print(f'Directory "{path}" on {day_name} {header_date}')
            
            # For C: directory, commands should be shown as executable files, not directories
            command_names = self.directories.get(path, [])
            file_count = 0
            total_bytes = 0
            
            # Show commands as executable files
            for cmd_name in command_names:
                # Get file size from the files dictionary if it exists
                cmd_file_path = f"C:{cmd_name}"
                if cmd_file_path in self.files:
                    file_size = len(self.files[cmd_file_path])
                else:
                    file_size = 1024  # Default size for executable commands
                total_bytes += file_size
                date_str = self._format_amiga_date(full_format=True)
                print(f" {cmd_name:<22} {file_size:>7}  ---xrwed     {date_str}")
                file_count += 1
                
            # Also list any actual files in C: directory
            for file_path in self.files:
                if file_path.startswith("C:") and file_path != "C:":
                    file_name = file_path[2:]  # Remove "C:" prefix
                    if "/" not in file_name and file_name not in command_names:  # Only direct children not already listed
                        file_content = self.files[file_path]
                        file_size = len(file_content)
                        total_bytes += file_size
                        date_str = self._format_amiga_date(full_format=True)  # Use current time for virtual files
                        print(f" {file_name:<22} {file_size:>7}  ----rwed     {date_str}")
                        file_count += 1
                        
            print(f"{file_count} files - 0 directories - {total_bytes} bytes used")
            return
        
        # Handle virtual directories (non-DH0 paths)
        if path not in self.directories:
            # Check if it's a subdirectory of a virtual device
            # e.g., "SYS:C" should map to "C:"
            if ":" in path:
                device_part, sub_part = path.split(":", 1)
                device = device_part + ":"
                
                # Special case: SYS:C maps to C:
                if device == "SYS:" and sub_part in self.directories.get("SYS:", []):
                    if sub_part == "C":
                        # List contents of C: device
                        virtual_path = "C:"
                        day_name = self._format_amiga_day()
                        header_date = self._format_amiga_date()
                        print(f'Directory "{path}" on {day_name} {header_date}')
                        
                        # For C: directory, commands should be shown as executable files, not directories
                        command_names = self.directories.get(virtual_path, [])
                        file_count = 0
                        total_bytes = 0
                        
                        # Show commands as executable files
                        for cmd_name in command_names:
                            # Get file size from the files dictionary if it exists
                            cmd_file_path = f"C:{cmd_name}"
                            if cmd_file_path in self.files:
                                file_size = len(self.files[cmd_file_path])
                            else:
                                file_size = 1024  # Default size for executable commands
                            total_bytes += file_size
                            date_str = self._format_amiga_date(full_format=True)
                            print(f" {cmd_name:<22} {file_size:>7}  ----rwed     {date_str}")
                            file_count += 1
                            
                        # Also list any actual files in C: directory
                        for file_path in self.files:
                            if file_path.startswith(virtual_path):
                                file_name = file_path[len(virtual_path):]
                                if "/" not in file_name and file_name and file_name not in command_names:  # Only direct children not already listed
                                    file_content = self.files[file_path]
                                    file_size = len(file_content)
                                    total_bytes += file_size
                                    date_str = self._format_amiga_date(full_format=True)  # Use current time for virtual files
                                    print(f" {file_name:<22} {file_size:>7}  ----rwed     {date_str}")
                                    file_count += 1
                                    
                        print(f"{file_count} files - 0 directories - {total_bytes} bytes used")
                        return
                    else:
                        # Handle other SYS: subdirectories
                        day_name = self._format_amiga_day()
                        header_date = self._format_amiga_date()
                        print(f'Directory "{path}" on {day_name} {header_date}')
                        
                        # List files in this virtual subdirectory
                        file_count = 0
                        path_prefix = path + "/"
                        total_bytes = 0
                        for file_path in self.files:
                            if file_path.startswith(path_prefix):
                                file_name = file_path[len(path_prefix):]
                                if "/" not in file_name:  # Only direct children
                                    file_content = self.files[file_path]
                                    file_size = len(file_content)
                                    total_bytes += file_size
                                    date_str = self._format_amiga_date(full_format=True)  # Use current time for virtual files
                                    print(f" {file_name:<22} {file_size:>7}  ----rwed     {date_str}")
                                    file_count += 1
                                    
                        print(f"{file_count} files - 0 directories - {total_bytes} bytes used")
                        return
            
            print(f"Directory {path} not found.")
            return
            
        day_name = self._format_amiga_day()
        header_date = self._format_amiga_date()
        print(f'Directory "{path}" on {day_name} {header_date}')
        
        # List subdirectories (authentic Amiga format)
        dirs = self.directories.get(path, [])
        for dir_name in dirs:
            date_str = self._format_amiga_date(full_format=True)  # Use current time for virtual dirs
            print(f" {dir_name:<22} (dir)    ----rwed     {date_str}")
            
        # List files in current directory
        file_count = 0
        total_bytes = 0
        for file_path in self.files:
            if file_path.startswith(path + "/"):
                file_name = file_path[len(path) + 1:]
                if "/" not in file_name:  # Only direct children
                    file_content = self.files[file_path]
                    file_size = len(file_content)
                    total_bytes += file_size
                    date_str = self._format_amiga_date(full_format=True)  # Use current time for virtual files
                    print(f" {file_name:<22} {file_size:>7}  ----rwed     {date_str}")
                    file_count += 1
                    
        total_files = len(dirs) + file_count
        print(f"{total_files} files - {len(dirs)} directories - {total_bytes} bytes used")
                    
    def _change_directory(self, path):
        """Change directory"""
        # Check if this is a mounted emulator shared folder
        device = path.split('/')[0] if '/' in path else path
        device = device.upper()
        if not device.endswith(':'):
            device += ':'
        
        if device in self.emulator_integration.mounted_shared_folders:
            return self._change_shared_folder_directory(path, device)
        
        # Handle DH0: (Windows C: drive)
        if path.upper() == "DH0:":
            self.current_dir = "DH0:"
            self.prompt = f"{self.current_dir}> "
            return ""
            
        if path == ".." or path.startswith("../"):
            if self.current_dir == "SYS:":
                return "Already at root directory."
            
            # Handle relative paths with ../
            if path.startswith("../"):
                # Get the target path after going up one level
                target_path = path[3:]  # Remove "../"
                
                # Go up one level first
                parts = self.current_dir.split(":")
                if len(parts) > 1 and parts[1]:
                    parent_parts = parts[1].split("/")
                    if len(parent_parts) > 1:
                        parent_dir = parts[0] + ":" + "/".join(parent_parts[:-1])
                    else:
                        parent_dir = parts[0] + ":"
                else:
                    parent_dir = "SYS:"
                
                # Now navigate to the target from the parent directory
                if target_path:
                    if parent_dir.endswith(":"):
                        new_path = parent_dir + target_path
                    else:
                        new_path = parent_dir + "/" + target_path
                    
                    # Check if the target directory exists
                    if new_path in self.directories:
                        self.current_dir = new_path
                        self.prompt = f"{self.current_dir}> "
                        return ""
                    else:
                        return f"Directory {target_path} not found."
                else:
                    self.current_dir = parent_dir
                    self.prompt = f"{self.current_dir}> "
                    return ""
            else:
                # Just go up one level
                parts = self.current_dir.split(":")
                if len(parts) > 1 and parts[1]:
                    parent_parts = parts[1].split("/")
                    if len(parent_parts) > 1:
                        new_path = parts[0] + ":" + "/".join(parent_parts[:-1])
                        if new_path == parts[0] + ":":
                            new_path = parts[0] + ":"
                        self.current_dir = new_path
                    else:
                        self.current_dir = parts[0] + ":"
                else:
                    self.current_dir = "SYS:"
                self.prompt = f"{self.current_dir}> "
                return ""
            
        # Handle absolute paths
        if ":" in path:
            # Special handling for DH0: subdirectories
            if path.upper().startswith("DH0:"):
                # Check if we're running in WSL environment
                is_wsl = os.path.exists("/mnt/c")
                is_windows = platform.system() == "Windows"
                
                if is_wsl or is_windows:
                    try:
                        sub_path = path[4:]  # Remove "DH0:" prefix
                        if sub_path.startswith("/"):
                            sub_path = sub_path[1:]
                        
                        if is_wsl:
                            fs_path = os.path.join("/mnt/c", sub_path.replace("\\", "/"))
                        else:
                            fs_path = os.path.join("C:\\", sub_path.replace("/", "\\"))
                        
                        # Normalize the path
                        fs_path = os.path.normpath(fs_path)
                        
                        if os.path.exists(fs_path) and os.path.isdir(fs_path):
                            self.current_dir = path
                            self.prompt = f"{self.current_dir}> "
                            return ""
                    except Exception as e:
                        pass
                return f"Directory {path} not found."
                
            if path in self.directories:
                self.current_dir = path
                self.prompt = f"{self.current_dir}> "
                return ""
            else:
                return f"Directory {path} not found."
                
        # Handle relative paths
        # Special handling for DH0: subdirectories
        if self.current_dir.upper().startswith("DH0:"):
            # Check if we're running in WSL environment
            is_wsl = os.path.exists("/mnt/c")
            is_windows = platform.system() == "Windows"
            
            if is_wsl or is_windows:
                try:
                    # Construct the new path
                    if self.current_dir.upper() == "DH0:":
                        new_path = f"DH0:/{path}"
                    else:
                        new_path = f"{self.current_dir}/{path}"
                    
                    # Check if the path exists in the actual file system
                    sub_path = new_path[4:]  # Remove "DH0:" prefix
                    if sub_path.startswith("/"):
                        sub_path = sub_path[1:]
                    
                    if is_wsl:
                        fs_path = os.path.join("/mnt/c", sub_path.replace("\\", "/"))
                    else:
                        fs_path = os.path.join("C:\\", sub_path.replace("/", "\\"))
                    
                    # Normalize the path
                    fs_path = os.path.normpath(fs_path)
                    
                    if os.path.exists(fs_path) and os.path.isdir(fs_path):
                        self.current_dir = new_path
                        self.prompt = f"{self.current_dir}> "
                        return ""
                except Exception as e:
                    pass
            return f"Directory {path} not found."
            
        if self.current_dir == "SYS:":
            new_path = f"SYS:{path}"
        else:
            new_path = f"{self.current_dir}/{path}"
            
        # Check if the new path exists in directories
        if new_path in self.directories:
            self.current_dir = new_path
            self.prompt = f"{self.current_dir}> "
            return ""
        else:
            # Check if it's a subdirectory of current directory
            if self.current_dir in self.directories and path in self.directories[self.current_dir]:
                if self.current_dir == "SYS:":
                    new_path = f"SYS:{path}"
                else:
                    new_path = f"{self.current_dir}/{path}"
                self.current_dir = new_path
                self.prompt = f"{self.current_dir}> "
                return ""
            else:
                return f"Directory {path} not found."
                
    def _info_command(self):
        """Enhanced system information command with comprehensive details"""
        import datetime
        import time
        
        # Get current time
        now = datetime.datetime.now()
        uptime_start = time.time() - time.perf_counter()
        uptime = datetime.datetime.fromtimestamp(uptime_start)
        
        # Get system information
        system_info = f"""System: {platform.system()} {platform.release()}
Processor: {platform.processor() or 'Unknown'}
Machine: {platform.machine()}
Node Name: {platform.node()}
Python Version: {platform.python_version()}"""
        
        # Try to get detailed system information
        memory_info = ""
        cpu_info = ""
        disk_info = ""
        
        try:
            import psutil
            
            # Memory information
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            memory_info = f"""Memory Information:
  Physical RAM: {memory.total // (1024**3):.1f}GB total, {memory.available // (1024**3):.1f}GB available
  Memory Usage: {memory.percent:.1f}% used
  Swap Space: {swap.total // (1024**3):.1f}GB total, {swap.used // (1024**3):.1f}GB used"""
            
            # CPU information
            cpu_count = psutil.cpu_count()
            cpu_count_logical = psutil.cpu_count(logical=True)
            cpu_freq = psutil.cpu_freq()
            cpu_usage = psutil.cpu_percent(interval=0.1)
            
            cpu_info = f"""CPU Information:
  Cores: {cpu_count} physical, {cpu_count_logical} logical
  Frequency: {cpu_freq.current:.0f}MHz (max: {cpu_freq.max:.0f}MHz)
  Usage: {cpu_usage:.1f}%"""
            
            # Disk information
            disk_usage = psutil.disk_usage('/')
            if platform.system() == "Windows":
                try:
                    disk_usage = psutil.disk_usage('C:')
                except:
                    pass
            
            disk_info = f"""Disk Information:
  Total: {disk_usage.total // (1024**3):.1f}GB
  Used: {disk_usage.used // (1024**3):.1f}GB ({disk_usage.used/disk_usage.total*100:.1f}%)
  Free: {disk_usage.free // (1024**3):.1f}GB"""
            
        except ImportError:
            memory_info = "Memory: Unknown (install 'pip install psutil' for detailed info)"
            cpu_info = "CPU: Unknown (install 'pip install psutil' for detailed info)"
            disk_info = "Disk: Unknown (install 'pip install psutil' for detailed info)"
        except Exception as e:
            memory_info = f"Memory: Error getting info ({e})"
            cpu_info = f"CPU: Error getting info ({e})"
            disk_info = f"Disk: Error getting info ({e})"
        
        # WSA Terminal information
        wsa_info = f"""WSA Terminal Information:
  Version: 1.0.0
  Started: {now.strftime('%d-%b-%y %H:%M:%S')}
  Current Directory: {self.current_dir}
  Virtual Devices: {len(self.directories)} mounted
  Virtual Files: {len(self.files)} files"""
        
        # Environment information
        env_info = ""
        if platform.system() == "Windows":
            is_wsl = os.path.exists("/mnt/c")
            if is_wsl:
                env_info = "Environment: WSL (Windows Subsystem for Linux)"
            else:
                env_info = "Environment: Native Windows"
        else:
            env_info = f"Environment: {platform.system()}"
        
        return f"""WSA Terminal - Windows Subsystem for Amiga
Copyright (C) 2025 WSA Project Contributors
Inspired by the legendary Amiga computer systems

=== AMIGA SIMULATION ===
System: AmigaOS 3.1
CPU: Motorola 68020 @ 25MHz  
ChipRAM: 2MB
FastRAM: 8MB
Kickstart: 3.1 (40.68)
Workbench: 3.1

=== ACTUAL SYSTEM ===
{system_info}
{env_info}

{memory_info}

{cpu_info}

{disk_info}

{wsa_info}

Commands: TYPE 'help' for available commands
Network: PING command available for connectivity testing
Speech: SAY command available for text-to-speech
Emulation: WINUAE command available for real Amiga emulation"""
        
    def _avail_command(self):
        """Available commands"""
        output = "Available commands:\n"
        commands = sorted(["info", "avail", "status", "mount", "ed", "dir", "cd", "pattern", 
                          "date", "echo", "help", "amiga", "ping", "cls", "clear", "test", "exit", "quit", "execute", "guru"])
        for cmd in commands:
            output += f"  {cmd}\n"
        return output
        
    def _status_command(self):
        """Enhanced system status with real-time information"""
        import datetime
        import time
        
        # Get current time and uptime
        now = datetime.datetime.now()
        
        # Calculate WSA Terminal session uptime (approximate)
        session_start = now - datetime.timedelta(seconds=time.perf_counter())
        
        # Basic Amiga-style status
        amiga_status = f"""=== AMIGA SYSTEM STATUS ===
Date: {now.strftime('%d-%b-%y')}
Time: {now.strftime('%H:%M:%S')}
CLI: Shell Process #{random.randint(1, 99)}
Current Directory: {self.current_dir}
Task Priority: 0
Stack: 8000 bytes used of 32000
Free Memory: 6.2MB Chip, 7.8MB Fast"""
        
        # Try to get real system status
        real_status = ""
        process_info = ""
        
        try:
            import psutil
            
            # System uptime and load
            boot_time = psutil.boot_time()
            uptime = now - datetime.datetime.fromtimestamp(boot_time)
            uptime_str = f"{uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m"
            
            # CPU and memory status
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            # Running processes
            processes = list(psutil.process_iter(['pid', 'name', 'cpu_percent']))
            process_count = len(processes)
            
            # Network interfaces
            net_interfaces = len(psutil.net_if_addrs())
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            
            real_status = f"""
=== ACTUAL SYSTEM STATUS ===
System Uptime: {uptime_str}
CPU Usage: {cpu_percent:.1f}%
Memory Usage: {memory.percent:.1f}% ({memory.used // (1024**3):.1f}GB of {memory.total // (1024**3):.1f}GB)
Running Processes: {process_count}
Network Interfaces: {net_interfaces}
Disk Reads: {disk_io.read_count if disk_io else 'N/A'}
Disk Writes: {disk_io.write_count if disk_io else 'N/A'}"""
            
            # Top processes (Amiga-style task list)
            top_processes = sorted(processes, key=lambda x: x.info['cpu_percent'] or 0, reverse=True)[:5]
            
            process_info = "\n=== ACTIVE TASKS (TOP 5) ==="
            for i, proc in enumerate(top_processes, 1):
                try:
                    name = proc.info['name'][:15]  # Limit name length
                    pid = proc.info['pid']
                    cpu = proc.info['cpu_percent'] or 0
                    process_info += f"\n{i:2}. {name:<15} PID:{pid:<6} CPU:{cpu:>5.1f}%"
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except ImportError:
            real_status = "\n=== ACTUAL SYSTEM STATUS ===\nDetailed status unavailable (install 'pip install psutil')"
            process_info = ""
        except Exception as e:
            real_status = f"\n=== ACTUAL SYSTEM STATUS ===\nError getting status: {e}"
            process_info = ""
        
        # WSA Terminal specific status
        wsa_status = f"""
=== WSA TERMINAL STATUS ===
Session Started: {session_start.strftime('%d-%b-%y %H:%M:%S')}
Virtual Devices Mounted: {len(self.directories)}
Virtual Files Available: {len(self.files)}
Commands Available: {len([attr for attr in dir(self) if attr.startswith('do_')])}
Last Command: {getattr(self, 'lastcmd', 'None')}"""
        
        # Device status
        device_status = "\n=== MOUNTED DEVICES ==="
        for device in sorted(self.directories.keys()):
            if device.upper() == "DH0:":
                # Check if Windows C: drive is accessible
                try:
                    if platform.system() == "Windows":
                        disk_usage = psutil.disk_usage('C:') if 'psutil' in globals() else None
                        if disk_usage:
                            free_gb = disk_usage.free // (1024**3)
                            device_status += f"\n{device:<8} Windows C: Drive ({free_gb}GB free)"
                        else:
                            device_status += f"\n{device:<8} Windows C: Drive (Status unknown)"
                    else:
                        device_status += f"\n{device:<8} Windows C: Drive (Not accessible)"
                except:
                    device_status += f"\n{device:<8} Windows C: Drive (Error accessing)"
            else:
                file_count = len([f for f in self.files.keys() if f.startswith(device)])
                subdir_count = len(self.directories.get(device, []))
                device_status += f"\n{device:<8} Virtual Device ({file_count} files, {subdir_count} subdirs)"
        
        return f"""{amiga_status}{real_status}{process_info}{wsa_status}{device_status}

Type 'info' for detailed system information
Type 'mount' to see mounted volumes
Type 'dir' to list current directory contents"""
        
    def _change_shared_folder_directory(self, path, device):
        """Change directory within emulator shared folder"""
        shared_info = self.emulator_integration.mounted_shared_folders[device]
        base_path = shared_info['path']
        
        # Determine the actual file system path
        if path == device:
            fs_path = base_path
            self.current_dir = device
        else:
            # Handle subdirectories within the shared folder
            sub_path = path[len(device):]
            if sub_path.startswith('/'):
                sub_path = sub_path[1:]
            fs_path = os.path.join(base_path, sub_path.replace('/', os.sep))
            
            # Verify the directory exists
            fs_path = os.path.normpath(fs_path)
            if not os.path.exists(fs_path) or not os.path.isdir(fs_path):
                return f"Directory {path} not found."
            
            self.current_dir = path
        
        self.prompt = f"{self.current_dir}> "
        return ""

    def _list_winuae_configs(self):
        """List available WinUAE configurations with their shared folders"""
        if not self.emulator_integration.winuae_configs:
            print("No WinUAE configurations found.")
            print("Make sure WinUAE is installed and configurations exist in:")
            print(f"  {WINUAE_CONFIG['config_dir']}")
            return
        
        print("Available WinUAE Configurations:")
        print("=" * 40)
        for config_name, config_info in self.emulator_integration.winuae_configs.items():
            print(f"\n  Config: {config_name}")
            print(f"  Path:   {config_info['path']}")
            if config_info['shared_folders']:
                print("  Shared Folders:")
                for device, folder_info in config_info['shared_folders'].items():
                    access_str = "(Read-Write)" if folder_info['access'] == 'rw' else "(Read-Only)"
                    print(f"    {device} \"{folder_info['label']}\" -> {folder_info['path']} {access_str}")
            else:
                print("  No shared folders configured")
    
    def _list_fsuae_configs(self):
        """List available FS-UAE configurations with their shared folders"""
        if not self.emulator_integration.fsuae_configs:
            print("No FS-UAE configurations found.")
            print("Make sure FS-UAE is installed and configurations exist in:")
            print("  ~/.config/fs-uae/")
            print("  ~/Documents/FS-UAE/Configurations/")
            return
        
        print("Available FS-UAE Configurations:")
        print("=" * 40)
        for config_name, config_info in self.emulator_integration.fsuae_configs.items():
            print(f"\n  Config: {config_name}")
            print(f"  Path:   {config_info['path']}")
            if config_info['shared_folders']:
                print("  Shared Folders:")
                for device, folder_info in config_info['shared_folders'].items():
                    print(f"    {device} \"{folder_info['label']}\" -> {folder_info['path']}")
            else:
                print("  No shared folders configured")
    
    def _list_all_emulator_configs(self):
        """List all available emulator configurations"""
        configs = self.emulator_integration.list_available_configs()
        
        if not configs:
            print("No emulator configurations found.")
            print("Make sure WinUAE and/or FS-UAE are installed with valid configurations.")
            return
        
        print("Available Emulator Configurations:")
        print("=" * 50)
        
        winuae_configs = [c for c in configs if c['emulator'] == 'WinUAE']
        fsuae_configs = [c for c in configs if c['emulator'] == 'FS-UAE']
        
        if winuae_configs:
            print("\nWinUAE Configurations:")
            for config in winuae_configs:
                shared_devices = ", ".join(config['shared_folders']) if config['shared_folders'] else "None"
                print(f"  {config['name']} (Devices: {shared_devices})")
        
        if fsuae_configs:
            print("\nFS-UAE Configurations:")
            for config in fsuae_configs:
                shared_devices = ", ".join(config['shared_folders']) if config['shared_folders'] else "None"
                print(f"  {config['name']} (Devices: {shared_devices})")
        
        print("\nUsage:")
        print("  MOUNT <device> FROM WINUAE \"<config_name>\"")
        print("  MOUNT <device> FROM FS-UAE \"<config_name>\"")

    def _mount_command(self):
        """Mounted volumes"""
        output = "Mounted volumes:\n"
        
        # Show standard volumes
        for vol in self.directories:
            if vol.upper() == "DH0:":
                output += f"  {vol} (Windows C: Drive)\n"
            elif vol in self.emulator_integration.mounted_shared_folders:
                # Show emulator shared folder info
                shared_info = self.emulator_integration.mounted_shared_folders[vol]
                emulator = shared_info['emulator'].upper()
                label = shared_info['label']
                config = shared_info['config']
                access = " (Read-Only)" if shared_info['access'] == 'ro' else ""
                output += f"  {vol} ({emulator} Shared: \"{label}\" from {config}){access}\n"
            else:
                output += f"  {vol}\n"
        
        return output
        
    def _help_command(self):
        """Help command"""
        return """Available commands:
  INFO     - Display system information
  AVAIL    - List available commands
  STATUS   - Show system status
  MOUNT    - Show mounted volumes
  ED       - Text editor
  DIR      - List directory contents (Amiga format with Name, Size, Protection, Date)
  CD       - Change directory
  TYPE     - Display file contents
  COPY     - Copy files
  DELETE   - Delete files
  MAKEDIR  - Create directories
  PATTERN  - Pattern matching utility
  DATE     - Show current date and time
  ECHO     - Echo text to terminal
  HELP     - Display this help
  AMIGA    - Amiga easter egg
  PING     - Network ping utility
  CLS      - Clear screen
  TEST     - Run a simple test
  EXECUTE  - Execute a script file
  EXIT     - Exit the terminal

Amiga Features:
  Type a device name (e.g., 'dh0:') to automatically CD to that directory
  Press Tab for path autocomplete (e.g., 'cd SYS:<Tab>' to complete directories)
  Startup sequence execution at terminal startup (SYS:S/Startup-Sequence)
"""
        
    def _amiga_command(self):
        """Enhanced Amiga easter egg with authentic ASCII art and references"""
        import random
        import time
        import sys
        
        # Classic Amiga ASCII art
        amiga_art = """
    ██████╗  ███╗   ███╗ ██╗  ██╗ ████████╗ ██████╗   ███████╗
   ██╔════╝  ████╗ ████║ ██║  ██║ ╚══██╔══╝ ██╔══██╗  ██╔════╝
   ██║  ███╗ ██╔████╔██║ ██║  ██║    ██║    ██║  ██║  ███████╗
   ██║   ██║ ██║╚██╔╝██║ ██║  ██║    ██║    ██║  ██║  ╚════██║
   ╚██████╔╝ ██║ ╚═╝ ██║ ██║  ██║    ██║    ██████╔╝  ███████║
    ╚═════╝  ╚═╝     ╚═╝ ╚═╝  ╚═╝    ╚═╝    ╚═════╝   ╚══════╝
                                                                
        ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
       ██                                                    ██
      ██  "Only Amiga Makes It Possible"™                     ██
     ██                                                       ██
    ██     Commodore-Amiga, Inc. 1985-1995                    ██
   ██                                                         ██
  ██       The Computer For The Creative Mind                 ██
 ██                                                           ██
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
"""
        
        # Random Amiga facts and quotes
        amiga_facts = [
            "The Amiga was the first multimedia computer with custom chips: Agnus, Denise, and Paula!",
            "AmigaOS featured preemptive multitasking when other systems were still cooperative.",
            "The Amiga could display 4096 colors simultaneously using Half-Bright mode and HAM.",
            "Workbench 1.0 was released in 1985, making it one of the first GUI operating systems.",
            "The Amiga's sound chip Paula could play 4 PCM channels simultaneously at different frequencies.",
            "Deluxe Paint on Amiga revolutionized digital art and animation in the late 80s and 90s.",
            "Many classic games like Lemmings, Defender of the Crown, and Shadow of the Beast debuted on Amiga.",
            "The Video Toaster made Amiga the king of video production in TV studios worldwide.",
            "Amiga's Copper chip could change colors mid-screen, creating stunning visual effects.",
            "The CLI (Command Line Interface) was more powerful than DOS and inspired modern terminals."
        ]
        
        # Amiga demo scene references
        demo_groups = [
            "Fairlight", "Kefrens", "The Silents", "Razor 1911", "Alcatraz", 
            "Sanity", "Spaceballs", "Red Sector Inc.", "Crusaders", "Tristar"
        ]
        
        # Build the output
        output = amiga_art
        output += f"\n💾 WSA Terminal - Windows Subsystem for Amiga v1.0.0"
        output += f"\n🎮 Bringing back the magic of AmigaOS to modern systems!"
        output += f"\n\n📚 Did you know? {random.choice(amiga_facts)}"
        output += f"\n\n🎨 Greetings to the demo scene: {', '.join(random.sample(demo_groups, 3))} and all the others!"
        
        # Add some system info in Amiga style
        output += f"\n\n💻 System Configuration:"
        output += f"\n   • Fast RAM: {platform.machine()} processor"
        output += f"\n   • Chip RAM: {platform.system()} {platform.release()}"
        output += f"\n   • Workbench: WSA Terminal 1.0"
        output += f"\n   • Kickstart: Python {platform.python_version()}"
        
        # Add some classic Amiga directories reference
        output += f"\n\n📁 Classic Amiga Volumes Available:"
        output += f"\n   • SYS: (System Volume)"
        output += f"\n   • RAM: (RAM Disk)"  
        output += f"\n   • DH0: (Hard Drive - mapped to C:)"
        output += f"\n   • C: (Commands Directory)"
        
        # Random Workbench color scheme reference
        wb_colors = ["Blue/Orange (WB 1.x)", "Grey/Blue (WB 2.x)", "Grey/White (WB 3.x)"]
        output += f"\n\n🎨 Workbench Color Scheme: {random.choice(wb_colors)}"
        
        # Add a motivational Amiga quote
        amiga_quotes = [
            "The Amiga: Because creativity shouldn't have limits.",
            "Multitasking was not a luxury, it was an Amiga standard.",
            "Before there was multimedia, there was Amiga.",
            "The computer that made the impossible, possible.",
            "AmigaOS: The operating system that was ahead of its time."
        ]
        output += f"\n\n💭 \"{random.choice(amiga_quotes)}\""
        
        output += f"\n\n🚀 Use DIR, TYPE, COPY, DELETE, MAKEDIR and other commands to explore!"
        output += f"\n⭐ Type HELP for available commands or start with: CD DH0:"
        output += f"\n\nWelcome to the Amiga experience! Enjoy your journey! 🎉"
        
        # Add classic demo scene scroller
        scroll_messages = [
            "WELCOME TO THE AMIGA DEMO SCENE... THE GREATEST COMPUTER EVER MADE... ",
            "GREETINGS TO ALL AMIGA SCENERS WORLDWIDE... KEEP THE SPIRIT ALIVE... ",
            "CODED WITH LOVE FOR THE AMIGA COMMUNITY... 68000 FOREVER... ",
            "REMEMBER THE GOLDEN AGE OF COMPUTING... WORKBENCH RULES... ",
            "PAULA PLAYS THE SWEETEST MUSIC... AGNUS DRAWS THE BEST GRAPHICS... ",
            "FROM WORKBENCH TO DEMOS... FROM GAMES TO MUSIC... AMIGA DOES IT ALL... ",
            "THIS IS A TRIBUTE TO JAY MINER AND THE AMIGA TEAM... LEGENDS NEVER DIE... ",
            "COPPER BARS... SINE SCROLLERS... PLASMA EFFECTS... CLASSIC DEMO MAGIC... ",
            "500... 600... 1000... 1200... 2000... 3000... 4000... ALL AMIGA MODELS ROCK... ",
            "KICKSTART ROM... AUTOCONFIG... GURU MEDITATION... CLASSIC AMIGA MEMORIES... "
        ]
        
        # Display static output first
        print(output)
        
        # Now display the animated scroller
        print("\n" + "="*70)
        print("🌟 CLASSIC AMIGA DEMO SCROLLER 🌟")
        print("="*70)
        
        # Select random scroll message
        scroll_text = random.choice(scroll_messages)
        scroll_width = 60
        
        try:
            print("\nPress Ctrl+C to stop the scroller...\n")
            
            # Infinite loop for continuous scrolling
            while True:
                # Animate the scroller - full cycle for each message
                for i in range(len(scroll_text) + scroll_width):
                    # Calculate the visible portion
                    if i < scroll_width:
                        # Text entering from right
                        visible_text = " " * (scroll_width - i) + scroll_text[:i]
                    elif i >= len(scroll_text):
                        # Text exiting to left
                        remaining = len(scroll_text) + scroll_width - i
                        if remaining <= 0:
                            visible_text = " " * scroll_width
                        else:
                            visible_text = scroll_text[i - scroll_width:] + " " * (scroll_width - remaining)
                    else:
                        # Text fully visible, scrolling
                        start_pos = i - scroll_width
                        end_pos = i
                        visible_text = scroll_text[start_pos:end_pos]
                        if len(visible_text) < scroll_width:
                            visible_text = visible_text + " " * (scroll_width - len(visible_text))
                    
                    # Ensure exactly scroll_width characters
                    visible_text = visible_text[:scroll_width]
                    if len(visible_text) < scroll_width:
                        visible_text = visible_text + " " * (scroll_width - len(visible_text))
                    
                    # Print the scroller line
                    print(f"\r🎬 [{visible_text}] 🎬", end="", flush=True)
                    time.sleep(0.08)  # Classic demo scroll speed
                
                # Small pause before next loop to make the repeat more visible
                time.sleep(0.3)
                
        except KeyboardInterrupt:
            print("\n\nScroller stopped by user.")
        
        print("\n\n" + "="*70)
        print("🎉 Thanks for watching! The Amiga spirit lives on! 🎉")
        print("="*70)
        
        return ""  # Return empty string since we already printed everything
        
    def _pattern_command(self, args):
        """Pattern matching utility"""
        pattern = args[0]
        output = f"Files matching pattern \"{pattern}\" in {self.current_dir}:\n"
        found = False
        
        # Handle DH0: with actual file system access
        if self.current_dir.upper() == "DH0:" and platform.system() == "Windows":
            try:
                c_drive_path = "C:\\"
                if os.path.exists(c_drive_path):
                    items = os.listdir(c_drive_path)
                    for item in items:
                        if pattern == "*" or item.startswith(pattern) or (pattern.startswith("~") and item.startswith(pattern[1:])):
                            item_path = os.path.join(c_drive_path, item)
                            if os.path.isdir(item_path):
                                output += f"  {item}/ (drwx)\n"
                            else:
                                output += f"  {item} (rwed)\n"
                            found = True
                    if found:
                        return output
            except Exception:
                pass  # Fall back to placeholder matching
                
        # Check pattern type for other directories
        if pattern == "#?":
            # Single character files
            for file_path in self.files:
                if file_path.startswith(self.current_dir):
                    file_name = file_path[len(self.current_dir) + 1:]
                    if file_name and "/" not in file_name and len(file_name) == 1:
                        output += f"  {file_name} (rwed)\n"
                        found = True
        elif pattern.startswith("~"):
            # Files starting with pattern
            prefix = pattern[1:]
            for file_path in self.files:
                if file_path.startswith(self.current_dir):
                    file_name = file_path[len(self.current_dir) + 1:]
                    if file_name and "/" not in file_name and file_name.startswith(prefix):
                        output += f"  {file_name} (rwed)\n"
                        found = True
        elif pattern == "*":
            # All files
            for file_path in self.files:
                if file_path.startswith(self.current_dir):
                    file_name = file_path[len(self.current_dir) + 1:]
                    if file_name and "/" not in file_name:
                        output += f"  {file_name} (rwed)\n"
                        found = True
        else:
            # Literal match
            for file_path in self.files:
                if file_path.startswith(self.current_dir):
                    file_name = file_path[len(self.current_dir) + 1:]
                    if file_name and "/" not in file_name and file_name == pattern:
                        output += f"  {file_name} (rwed)\n"
                        found = True
                        
        if not found:
            output += "  No files match the pattern.\n"
            
        return output
        
    def _guru_meditation_demo(self):
        """Display classic Amiga Guru Meditation error with flashing red banner"""
        import random
        import time
        import os
        
        # Generate random error codes like classic Amiga
        task_number = random.randint(1000000, 9999999)
        error_code = random.randint(0x80000001, 0x8FFFFFFF)
        
        # ANSI escape codes for terminal control
        CLEAR_SCREEN = "\033[2J"
        HIDE_CURSOR = "\033[?25l"
        SHOW_CURSOR = "\033[?25h"
        HOME = "\033[H"
        RED_BG = "\033[41m"
        WHITE_BG = "\033[47m"
        BLACK_TEXT = "\033[30m"
        WHITE_TEXT = "\033[37m"
        RESET = "\033[0m"
        BOLD = "\033[1m"
        
        # Clear screen and hide cursor
        print(CLEAR_SCREEN + HOME + HIDE_CURSOR, end="")
        
        # Create the classic error messages
        line1 = "Software Failure.  Press left mouse button to continue."
        line2 = f"Guru Meditation #{task_number:08X}.{error_code:08X}"
        
        # Calculate banner width (full terminal width or at least 80 chars)
        try:
            banner_width = os.get_terminal_size().columns
        except:
            banner_width = 80
        
        # Center the text in the banner
        line1_padding = (banner_width - len(line1)) // 2
        line2_padding = (banner_width - len(line2)) // 2
        
        try:
            flash_state = True
            flash_count = 0
            
            while True:
                # Clear screen and go to top
                print(HOME, end="")
                
                # Create flashing banner (alternates between red and white background)
                if flash_state:
                    bg_color = RED_BG
                    text_color = WHITE_TEXT
                else:
                    bg_color = WHITE_BG
                    text_color = BLACK_TEXT
                
                # Top banner line
                banner_line1 = bg_color + text_color + BOLD
                banner_line1 += " " * line1_padding + line1 + " " * (banner_width - len(line1) - line1_padding)
                banner_line1 += RESET
                
                # Bottom banner line
                banner_line2 = bg_color + text_color + BOLD
                banner_line2 += " " * line2_padding + line2 + " " * (banner_width - len(line2) - line2_padding)
                banner_line2 += RESET
                
                # Print the flashing banner at the top
                print(banner_line1)
                print(banner_line2)
                
                # Print black screen for rest of terminal
                # Fill the rest with empty lines to simulate black screen
                for _ in range(22):  # Approximate terminal height minus banner
                    print()
                
                # Flash every 0.5 seconds
                time.sleep(0.5)
                flash_state = not flash_state
                flash_count += 1
                
                # Optional: Add some variation to the flashing pattern
                if flash_count % 10 == 0:
                    time.sleep(0.2)  # Brief pause every 5 seconds
                
        except KeyboardInterrupt:
            # Restore terminal
            print(CLEAR_SCREEN + HOME + SHOW_CURSOR + RESET, end="")
            print("Guru Meditation interrupted. System recovered!")
            print("Welcome back to WSA Terminal.")
            print()
        
def main():
    parser = argparse.ArgumentParser(description='WSA Terminal Console - Windows Subsystem for Amiga')
    parser.add_argument('--no-intro', action='store_true', help='Skip the intro message')
    
    args = parser.parse_args()
    
    terminal = WSAConsoleTerminal()
    
    if args.no_intro:
        terminal.intro = ""
        
    try:
        terminal.cmdloop()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()