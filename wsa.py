#!/usr/bin/env python3
"""
WSA Terminal - Windows Subsystem for Amiga
Python implementation of the Amiga terminal emulator
"""

import asyncio
import os
import sys
import json
import argparse
import platform
from datetime import datetime
from pathlib import Path

try:
    from aiohttp import web, WSMsgType
except ImportError:
    print("Please install aiohttp: pip install aiohttp")
    sys.exit(1)

# Version information
WSA_VERSION = "1.0.0"

class AmigaTerminal:
    def __init__(self):
        self.current_dir = "SYS:"
        # Add Windows C: drive by default
        self.directories = {
            "SYS:": ["Prefs", "Tools", "L", "S", "C", "DEVS", "Fonts", "WBStartup"],
            "RAM:": ["T"],
            "C:": ["Info", "Avail", "Status", "Mount", "Ed", "Dir", "Cd", "Pattern", "Date", "Echo", "Help", "Amiga", "Ping"],
            "DH0:": []  # Windows C: drive mapped as DH0:
        }
        self.files = {
            "SYS:Prefs/Env-Archive": "Environment variables archive",
            "SYS:Prefs/Env": "Current environment variables",
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
            "C:Ping": "Network ping utility"
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
        
        self.prompt = "SYS:> "
        self.command_history = []
        
        # Execute startup sequence
        self._execute_startup_sequence()
        
    def _execute_startup_sequence(self):
        """Execute the Amiga-style startup sequence and return output"""
        output = "Executing startup sequence...\n"
        
        # Check for SYS:S/Startup-Sequence in virtual file system
        startup_file = "SYS:S/Startup-Sequence"
        if startup_file in self.files:
            startup_output = self._run_startup_script(startup_file, self.files[startup_file])
            return output + startup_output
            
        # Check for actual file in DH0: (Windows C: drive)
        if platform.system() == "Windows":
            try:
                fs_path = os.path.join("C:\\", "S", "Startup-Sequence")
                if os.path.exists(fs_path):
                    with open(fs_path, 'r') as f:
                        content = f.read()
                    startup_output = self._run_startup_script(startup_file, content)
                    return output + startup_output
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
                startup_output = self._run_startup_script(location, self.files[location])
                return output + startup_output
                
        return output
        
    def _run_startup_script(self, script_name, content):
        """Run a startup script and return output"""
        output = f"Executing {script_name}...\n"
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
                    output += line[5:] + "\n"
                # Handle other commands
                else:
                    # Parse command and arguments
                    parts = line.split()
                    if not parts:
                        continue
                        
                    cmd = parts[0].lower()
                    args = ' '.join(parts[1:]) if len(parts) > 1 else ''
                    
                    # Execute built-in commands
                    if cmd == "info":
                        output += self.info_command() + "\n"
                    elif cmd == "avail":
                        output += self.avail_command() + "\n"
                    elif cmd == "status":
                        output += self.status_command() + "\n"
                    elif cmd == "mount":
                        output += self.mount_command() + "\n"
                    elif cmd == "dir":
                        output += self.list_files() + "\n"
                    elif cmd == "date":
                        output += str(datetime.now()) + "\n"
                    elif cmd == "echo":
                        output += args + "\n"
                    elif cmd == "help":
                        output += self.help_command() + "\n"
                    elif cmd == "amiga":
                        output += self.amiga_command() + "\n"
                    elif cmd == "ping" and args:
                        output += self.ping_command([args]) + "\n"
                    elif cmd == "pattern" and args:
                        output += self.pattern_command([args]) + "\n"
                    # Handle some special cases
                    elif cmd == 'cd':
                        result = self.change_directory(args)
                        if result:
                            output += result + "\n"
                    else:
                        output += f"Startup command not recognized: {line}\n"
            except Exception as e:
                output += f"Error executing startup command '{line}': {e}\n"
                
        return output
        
    def get_prompt(self):
        return f"{self.current_dir}> "
        
    def list_files(self, path=None):
        if path is None:
            path = self.current_dir
            
        # Handle DH0: (Windows C: drive) with actual file system access
        if path.startswith("DH0:"):
            if platform.system() == "Windows":
                try:
                    # Determine the actual file system path
                    if path == "DH0:":
                        fs_path = "C:\\"
                    else:
                        # Extract subdirectory path from DH0:subdir format
                        sub_path = path[4:]  # Remove "DH0:" prefix
                        if sub_path.startswith("/"):
                            sub_path = sub_path[1:]
                        fs_path = os.path.join("C:\\", sub_path.replace("/", "\\"))
                    
                    # Try with trailing backslash if path doesn't exist
                    if not os.path.exists(fs_path):
                        if not fs_path.endswith("\\") and not fs_path.endswith("/"):
                            fs_path_alt = fs_path + "\\"
                            if os.path.exists(fs_path_alt):
                                fs_path = fs_path_alt
                    
                    if os.path.exists(fs_path) and os.path.isdir(fs_path):
                        output = f"Directory {path}\n"
                        output += "\n"
                        output += "Name              Size  Protection  Date\n"
                        output += "----              ----  ----------  ----\n"
                        
                        # List actual directories and files in the path
                        try:
                            items = os.listdir(fs_path)
                        except PermissionError:
                            return "Access denied to this directory.\n"
                        except Exception as e:
                            return f"Error reading directory: {e}\n"
                        
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
                        
                        # Print directories first
                        for dir_name in dirs:
                            output += f"{dir_name+'/':<18}DIR   drwx      01-Jan-85\n"
                            
                        # Print files
                        for file_name in files:
                            file_path = os.path.join(fs_path, file_name)
                            try:
                                file_size = os.path.getsize(file_path)
                            except:
                                file_size = 0
                            output += f"{file_name:<18}{file_size:>5}  rwed      01-Jan-85\n"
                            
                        dir_count = len(dirs)
                        file_count = len(files)
                        output += f"\n{dir_count} DIR(s), {file_count} FILE(s)\n"
                        return output
                    else:
                        return f"Directory {path} not found.\n"
                except Exception as e:
                    output = f"Error accessing directory {path}: {e}\n"
                    # Fall back to placeholder content if there's an error
                    pass
            
            # Fallback to placeholder content
            output = f"Directory {path}\n"
            output += "\n"
            output += "Name              Size  Protection  Date\n"
            output += "----              ----  ----------  ----\n"
            
            # List directories
            dirs = self.directories.get(path, [])
            for dir_name in dirs:
                output += f"{dir_name+'/':<18}DIR   drwx      01-Jan-85\n"
                
            # List files in current directory
            file_count = 0
            for file_path in self.files:
                if file_path.startswith(path + "/"):
                    file_name = file_path[len(path) + 1:]
                    if "/" not in file_name:  # Only direct children
                        file_content = self.files[file_path]
                        file_size = len(file_content)
                        output += f"{file_name:<18}{file_size:>5}  rwed      01-Jan-85\n"
                        file_count += 1
                        
            output += f"\n{len(dirs)} DIR(s), {file_count} FILE(s)\n"
            return output
            
        if path not in self.directories:
            return f"Directory {path} not found.\n"
            
        output = f"Directory {path}\n"
        output += "\n"
        output += "Name              Size  Protection  Date\n"
        output += "----              ----  ----------  ----\n"
        
        # List subdirectories
        dirs = self.directories.get(path, [])
        for dir_name in dirs:
            output += f"{dir_name+'/':<18}DIR   drwx      01-Jan-85\n"
            
        # List files in current directory
        file_count = 0
        for file_path in self.files:
            if file_path.startswith(path + "/"):
                file_name = file_path[len(path) + 1:]
                if "/" not in file_name:  # Only direct children
                    file_content = self.files[file_path]
                    file_size = len(file_content)
                    output += f"{file_name:<18}{file_size:>5}  rwed      01-Jan-85\n"
                    file_count += 1
                    
        output += f"\n{len(dirs)} DIR(s), {file_count} FILE(s)\n"
        return output
        
    def change_directory(self, path):
        # Handle DH0: (Windows C: drive)
        if path.upper() == "DH0:":
            self.current_dir = "DH0:"
            self.prompt = self.get_prompt()
            return ""
            
        if not path:
            return "Usage: CD <directory>\n"
            
        # Handle special cases
        if path == "..":
            if self.current_dir == "SYS:":
                return "Already at root directory.\n"
            # Go up one level
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
            self.prompt = self.get_prompt()
            return ""
            
        # Handle absolute paths
        if ":" in path:
            # Special handling for DH0: subdirectories
            if path.upper().startswith("DH0:") and platform.system() == "Windows":
                # Check if the path exists in the actual file system
                try:
                    sub_path = path[4:]  # Remove "DH0:" prefix
                    if sub_path.startswith("/"):
                        sub_path = sub_path[1:]
                    fs_path = os.path.join("C:\\", sub_path.replace("/", "\\"))
                    
                    # Try with trailing backslash if path doesn't exist
                    if not os.path.exists(fs_path):
                        if not fs_path.endswith("\\") and not fs_path.endswith("/"):
                            fs_path_alt = fs_path + "\\"
                            if os.path.exists(fs_path_alt):
                                fs_path = fs_path_alt
                    
                    if os.path.exists(fs_path) and os.path.isdir(fs_path):
                        self.current_dir = path
                        self.prompt = self.get_prompt()
                        return ""
                    else:
                        # Try with trailing slash for the Amiga path
                        if not path.endswith("/"):
                            path_alt = path + "/"
                            sub_path_alt = path_alt[4:]  # Remove "DH0:" prefix
                            if sub_path_alt.startswith("/"):
                                sub_path_alt = sub_path_alt[1:]
                            fs_path_alt = os.path.join("C:\\", sub_path_alt.replace("/", "\\"))
                            if os.path.exists(fs_path_alt) and os.path.isdir(fs_path_alt):
                                self.current_dir = path_alt
                                self.prompt = self.get_prompt()
                                return ""
                except Exception as e:
                    pass
                return f"Directory {path} not found.\n"
                
            if path in self.directories:
                self.current_dir = path
                self.prompt = self.get_prompt()
                return ""
            else:
                return f"Directory {path} not found.\n"
                
        # Handle relative paths
        # Special handling for DH0: subdirectories
        if self.current_dir.startswith("DH0:") and platform.system() == "Windows":
            try:
                # Construct the new path
                if self.current_dir == "DH0:":
                    new_path = f"DH0:{path}"
                else:
                    new_path = f"{self.current_dir}/{path}"
                
                # Check if the path exists in the actual file system
                sub_path = new_path[4:]  # Remove "DH0:" prefix
                if sub_path.startswith("/"):
                    sub_path = sub_path[1:]
                fs_path = os.path.join("C:\\", sub_path.replace("/", "\\"))
                
                # Try with trailing backslash if path doesn't exist
                if not os.path.exists(fs_path):
                    if not fs_path.endswith("\\") and not fs_path.endswith("/"):
                        fs_path_alt = fs_path + "\\"
                        if os.path.exists(fs_path_alt):
                            fs_path = fs_path_alt
                
                if os.path.exists(fs_path) and os.path.isdir(fs_path):
                    self.current_dir = new_path
                    self.prompt = self.get_prompt()
                    return ""
                else:
                    # Try with trailing slash for the Amiga path
                    if not new_path.endswith("/"):
                        new_path_alt = new_path + "/"
                        sub_path_alt = new_path_alt[4:]  # Remove "DH0:" prefix
                        if sub_path_alt.startswith("/"):
                            sub_path_alt = sub_path_alt[1:]
                        fs_path_alt = os.path.join("C:\\", sub_path_alt.replace("/", "\\"))
                        if os.path.exists(fs_path_alt) and os.path.isdir(fs_path_alt):
                            self.current_dir = new_path_alt
                            self.prompt = self.get_prompt()
                            return ""
            except Exception as e:
                pass
            return f"Directory {path} not found.\n"
            
        if self.current_dir == "SYS:":
            new_path = f"SYS:{path}"
        else:
            new_path = f"{self.current_dir}/{path}"
            
        # Check if the new path exists in directories
        if new_path in self.directories:
            self.current_dir = new_path
            self.prompt = self.get_prompt()
            return ""
        else:
            # Check if it's a subdirectory of current directory
            if self.current_dir in self.directories and path in self.directories[self.current_dir]:
                if self.current_dir == "SYS:":
                    new_path = f"SYS:{path}"
                else:
                    new_path = f"{self.current_dir}/{path}"
                self.current_dir = new_path
                self.prompt = self.get_prompt()
                return ""
            else:
                return f"Directory {path} not found.\n"
            
    def execute_command(self, command_text):
        parts = command_text.strip().split()
        if not parts:
            return ""
            
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Handle device names as CD commands (Amiga behavior)
        # If the command is just a device name (ends with :), treat it as CD
        if cmd.endswith(':') and cmd.upper() in [d.upper() for d in self.directories]:
            return self.change_directory(cmd)
        
        # Add to command history
        self.command_history.append(command_text)
        
        # Handle commands
        if cmd == "dir":
            return self.list_files()
        elif cmd == "cd":
            return self.change_directory(" ".join(args))
        elif cmd == "info":
            return self.info_command()
        elif cmd == "avail":
            return self.avail_command()
        elif cmd == "status":
            return self.status_command()
        elif cmd == "mount":
            return self.mount_command()
        elif cmd == "echo":
            return " ".join(args) + "\n"
        elif cmd == "date":
            return str(datetime.now()) + "\n"
        elif cmd == "help":
            return self.help_command()
        elif cmd == "amiga":
            return self.amiga_command()
        elif cmd == "ping":
            return self.ping_command(args)
        elif cmd == "pattern":
            return self.pattern_command(args)
        elif cmd == "cls" or cmd == "clear":
            return {"action": "clear"}
        else:
            return f"Command '{cmd}' not found. Type 'help' for available commands.\n"
            
    def get_available_commands(self):
        """Return list of available commands for autocomplete"""
        return sorted(["info", "avail", "status", "mount", "ed", "dir", "cd", "pattern", 
                      "date", "echo", "help", "amiga", "ping", "cls", "clear"])
                      
    def get_directory_contents(self, path_prefix):
        """Get directory contents for autocomplete"""
        # Handle DH0: with actual file system access
        if path_prefix.startswith("DH0:"):
            if platform.system() == "Windows":
                try:
                    # Determine the actual file system path
                    if path_prefix == "DH0:":
                        fs_path = "C:\\"
                        search_prefix = ""
                    else:
                        # Extract subdirectory path from DH0:subdir format
                        sub_path = path_prefix[4:]  # Remove "DH0:" prefix
                        if sub_path.startswith("/"):
                            sub_path = sub_path[1:]
                        fs_path = os.path.join("C:\\", sub_path.replace("/", "\\"))
                        search_prefix = path_prefix
                        
                    if os.path.exists(fs_path) and os.path.isdir(fs_path):
                        # Get parent directory to list contents
                        if search_prefix and not search_prefix.endswith("/") and not search_prefix.endswith("\\"):
                            parent_path = os.path.dirname(fs_path)
                            # Get the partial name we're matching
                            partial_name = os.path.basename(fs_path)
                        else:
                            parent_path = fs_path
                            partial_name = ""
                            
                        items = os.listdir(parent_path)
                        matches = []
                        for item in items:
                            if not partial_name or item.startswith(partial_name):
                                item_path = os.path.join(parent_path, item)
                                if search_prefix:
                                    if partial_name:
                                        # Replace the partial name with the full match
                                        base_prefix = search_prefix.rsplit("/", 1)[0]
                                        if base_prefix == "DH0:":
                                            full_path = f"DH0:{item}"
                                        else:
                                            full_path = f"{base_prefix}/{item}"
                                    else:
                                        if search_prefix.endswith("/") or search_prefix.endswith(":"):
                                            full_path = f"{search_prefix}{item}"
                                        else:
                                            full_path = f"{search_prefix}/{item}"
                                else:
                                    full_path = f"DH0:{item}"
                                
                                # Add trailing slash for directories
                                if os.path.isdir(item_path):
                                    matches.append(full_path + "/")
                                else:
                                    matches.append(full_path)
                        return matches
                except Exception as e:
                    # Fall back to placeholder content if there's an error
                    pass
            
            # Fallback to placeholder content for DH0:
            matches = []
            # Add directories
            for dir_name in self.directories.get("DH0:", []):
                full_path = f"DH0:{dir_name}/"
                if full_path.startswith(path_prefix):
                    matches.append(full_path)
            
            # Add files
            for file_path in self.files:
                if file_path.startswith("DH0:"):
                    file_name = file_path[4:]  # Remove "DH0:" prefix
                    if "/" not in file_name:  # Only direct children
                        full_path = f"DH0:{file_name}"
                        if full_path.startswith(path_prefix):
                            matches.append(full_path)
            return matches
            
        # Handle other devices with placeholder content
        for device in self.directories:
            if path_prefix.startswith(device):
                matches = []
                # Add directories
                for dir_name in self.directories[device]:
                    full_path = f"{device}{dir_name}/"
                    if full_path.startswith(path_prefix):
                        matches.append(full_path)
                
                # Add files
                for file_path in self.files:
                    if file_path.startswith(device):
                        file_name = file_path[len(device):]
                        if "/" not in file_name:  # Only direct children
                            full_path = f"{device}{file_name}"
                            if full_path.startswith(path_prefix):
                                matches.append(full_path)
                return matches
        
        # Handle relative paths (no device specified)
        # For relative paths, we autocomplete with items in current directory
        matches = []
        
        # Handle DH0: with actual file system
        if self.current_dir == "DH0:" and platform.system() == "Windows":
            try:
                fs_path = "C:\\"
                if os.path.exists(fs_path) and os.path.isdir(fs_path):
                    items = os.listdir(fs_path)
                    for item in items:
                        if item.startswith(path_prefix):
                            item_path = os.path.join(fs_path, item)
                            if os.path.isdir(item_path):
                                matches.append(item + "/")
                            else:
                                matches.append(item)
                    return matches
            except Exception:
                pass  # Fall back to placeholder matching
        
        # Handle other devices with placeholder content
        # Add directories in current directory
        if self.current_dir in self.directories:
            for dir_name in self.directories[self.current_dir]:
                if dir_name.startswith(path_prefix):
                    matches.append(dir_name + "/")
        
        # Add files in current directory
        for file_path in self.files:
            if file_path.startswith(self.current_dir + "/"):
                file_name = file_path[len(self.current_dir) + 1:]
                if "/" not in file_name and file_name.startswith(path_prefix):  # Only direct children
                    matches.append(file_name)
        
        return matches
            
    def info_command(self):
        """System information command with actual machine info"""
        # Get system information
        system_info = f"""System: {platform.system()} {platform.release()}
Processor: {platform.processor() or 'Unknown'}
Machine: {platform.machine()}
Node Name: {platform.node()}
Python Version: {platform.python_version()}
"""
        
        # Try to get memory information on Windows
        memory_info = ""
        if platform.system() == "Windows":
            try:
                import psutil
                memory = psutil.virtual_memory()
                memory_info = f"Memory: {memory.total // (1024**3)}GB RAM\n"
            except ImportError:
                memory_info = "Memory: Unknown (install psutil for detailed info)\n"
        else:
            memory_info = "Memory: Unknown\n"
            
        return f"""Amiga 3.1
Copyright (C) 1985-1995 Commodore-Amiga, Inc.
WSA Terminal - Windows Subsystem for Amiga v{WSA_VERSION}

System Information:
  CPU: Motorola 68020 @ 25MHz
  RAM: 8MB Chip + 4MB Fast
  OS: AmigaOS 3.1
  WB: Workbench 3.1
  CLI: Amiga Shell 3.1

Actual System Information:
  {system_info}  {memory_info}"""
        
    def avail_command(self):
        output = "Available commands:\n"
        commands = sorted(["info", "avail", "status", "mount", "ed", "dir", "cd", "pattern", 
                          "date", "echo", "help", "amiga", "ping", "cls", "clear", "execute"])
        for cmd in commands:
            output += f"  {cmd}\n"
        return output
        
    def status_command(self):
        return """System Status:
  CPU: Motorola 68020 @ 25MHz
  Memory: 8MB Chip + 4MB Fast
  Task: Shell Process
  Priority: 0
  Stack: 8000 bytes
  Processors: 1
  Tasks: 12 running

"""
        
    def mount_command(self):
        output = "Mounted volumes:\n"
        for vol in self.directories:
            if vol == "DH0:":
                output += f"  {vol} (Windows C: Drive)\n"
            else:
                output += f"  {vol}\n"
        return output
        
    def help_command(self):
        return """Available commands:
  INFO     - Display system information
  AVAIL    - List available commands
  STATUS   - Show system status
  MOUNT    - Show mounted volumes
  ED       - Text editor (not implemented)
  DIR      - List directory contents (Amiga format with Name, Size, Protection, Date)
  CD       - Change directory
  PATTERN  - Pattern matching utility
  DATE     - Show current date and time
  ECHO     - Echo text to terminal
  HELP     - Display this help
  AMIGA    - Amiga easter egg
  PING     - Network ping utility
  CLS      - Clear screen

Amiga Features:
  Type a device name (e.g., 'dh0:') to automatically CD to that directory
  Startup sequence execution at terminal startup (SYS:S/Startup-Sequence)
"""
        
    def amiga_command(self):
        return """                    /\\
                   /  \\
                  /    \\
                 /      \\
                /        \\
               /__________\\
              /            \\
             /              \\
            /                \\
           /                  \\
          /                    \\
         /                      \\
        /                        \\
       /                          \\
      /                            \\
     /                              \\
    /                                \\
   /                                  \\
  /                                    \\
 /______________________________________\\

Welcome to the WSA Terminal - Windows Subsystem for Amiga!
This is an emulation of the classic AmigaOS terminal experience.

"""
        
    def ping_command(self, args):
        if not args:
            return "Usage: PING <host>\n"
        return f"Pinging {args[0]}... (simulated)\nReply from {args[0]}: bytes=32 time<1ms TTL=64\n"
        
    def pattern_command(self, args):
        if not args:
            return """Usage: PATTERN <pattern>
Examples:
  PATTERN #?        (matches single character files)
  PATTERN ~pattern  (matches files starting with pattern)
  PATTERN *         (matches all files)
"""
            
        pattern = args[0]
        output = f"Files matching pattern \"{pattern}\" in {self.current_dir}:\n"
        found = False
        
        # Handle DH0: with actual file system access
        if self.current_dir == "DH0:" and platform.system() == "Windows":
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
                        if not found:
                            output += "  No files match the pattern.\n"
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

# HTML content for the terminal interface
HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WSA Terminal - Amiga 3.1 Shell</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background-color: #999; /* Amiga 3.1 darker gray background */
            color: #000;
            font-family: 'Courier New', monospace;
            height: 100vh;
            overflow: hidden;
            margin: 5px;
        }

        /* Amiga 3.1 window style - enhanced Workbench look */
        #window {
            border: 2px solid;
            border-top-color: #ddd;
            border-left-color: #ddd;
            border-right-color: #666;
            border-bottom-color: #666;
            background-color: #999;
            height: 100%;
            display: flex;
            flex-direction: column;
            box-shadow: 3px 3px 5px rgba(0, 0, 0, 0.5);
            margin: 10px;
        }

        /* Title bar - enhanced Amiga 3.1 Workbench style */
        #title-bar {
            background: linear-gradient(to right, #0000aa, #0000cc, #0000aa);
            color: #fff;
            padding: 4px 8px;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #000;
            font-size: 14px;
            text-shadow: 1px 1px 1px #000;
            height: 24px;
        }

        #title-text {
            font-size: 14px;
            text-shadow: 1px 1px 1px #000;
        }

        #window-controls {
            display: flex;
        }

        .window-button {
            width: 18px;
            height: 14px;
            margin-left: 4px;
            border: 1px solid;
            border-top-color: #ddd;
            border-left-color: #ddd;
            border-right-color: #666;
            border-bottom-color: #666;
            background-color: #bbb;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
            cursor: pointer;
            color: #000;
            text-shadow: none;
            box-shadow: inset 1px 1px 0px #eee, inset -1px -1px 0px #888;
            font-family: 'Courier New', monospace;
        }

        .window-button:hover {
            background-color: #ccc;
        }

        /* Terminal area - enhanced Amiga 3.1 Workbench style */
        #terminal {
            position: relative;
            flex: 1;
            padding: 12px;
            background-color: #000;
            overflow-y: auto;
            font-size: 14px;
            line-height: 1.3;
            margin: 6px;
            border: 2px solid;
            border-top-color: #666;
            border-left-color: #666;
            border-right-color: #ddd;
            border-bottom-color: #ddd;
        }

        /* Improve text readability in terminal */
        #output, #prompt {
            color: #0f0; /* Green text for better contrast on black */
            text-shadow: 0 0 1px rgba(0, 255, 0, 0.5); /* Subtle glow for better readability */
        }

        #output {
            white-space: pre-wrap;
            word-break: break-word;
        }

        #input-line {
            display: flex;
            align-items: center;
            margin-top: 6px;
            padding: 4px;
            background-color: #222;
            border: 1px solid #444;
        }

        #prompt {
            color: #0f0;
            margin-right: 8px;
            font-weight: bold;
            min-width: 80px;
        }

        #input {
            background: transparent;
            border: none;
            color: #0f0;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            outline: none;
            flex: 1;
            padding: 2px;
        }

        .cursor {
            display: inline-block;
            width: 8px;
            height: 14px;
            background-color: #0f0;
            animation: blink 1s infinite;
            vertical-align: middle;
            margin-left: 2px;
        }

        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0; }
        }

        .output-text {
            color: #0f0;
        }

        .output-text.red {
            color: #f00;
        }

        .output-text.yellow {
            color: #ff0;
        }

        .output-text.cyan {
            color: #0ff;
        }

        .output-text.magenta {
            color: #f0f;
        }

        /* Workbench-style status bar */
        #status-bar {
            background: linear-gradient(to right, #0000aa, #0000cc, #0000aa);
            color: #fff;
            padding: 3px 8px;
            font-size: 12px;
            border-top: 1px solid #000;
            text-shadow: 1px 1px 1px #000;
            height: 20px;
            display: flex;
            align-items: center;
        }

        /* Removed CRT effects for better readability */
        #terminal {
            background-color: #000;
        }
    </style>
</head>
<body>
    <div id="window">
        <div id="title-bar">
            <div id="title-text">Amiga 3.1 Shell - WSA Terminal</div>
            <div id="window-controls">
                <div class="window-button">←</div>
                <div class="window-button">□</div>
                <div class="window-button">×</div>
            </div>
        </div>
        <div id="terminal">
            <div id="output"></div>
            <div id="input-line">
                <span id="prompt"></span>
                <input type="text" id="input" autofocus>
                <span class="cursor"></span>
            </div>
        </div>
        <div id="status-bar">
            <div>WSA Terminal v1.0.0</div>
        </div>
    </div>

    <script>
        const socket = new WebSocket(`ws://${window.location.host}/ws`);
        const output = document.getElementById('output');
        const input = document.getElementById('input');
        const prompt = document.getElementById('prompt');
        
        // Command history
        let commandHistory = [];
        let historyIndex = -1;
        
        // Available commands for autocomplete
        let availableCommands = [];
        
        // Autocomplete state
        let suggestions = [];
        let selectedSuggestion = -1;
        
        // Simple sound effects using Web Audio API
        let audioContext;
        
        function initAudio() {
            try {
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
            } catch (e) {
                console.log("Web Audio API is not supported in this browser");
            }
        }
        
        function playKeyPressSound() {
            if (!audioContext) return;
            
            try {
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();
                
                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);
                
                oscillator.type = 'square';
                oscillator.frequency.value = 800;
                gainNode.gain.value = 0.1;
                
                oscillator.start();
                oscillator.stop(audioContext.currentTime + 0.05);
            } catch (e) {
                // Silent fail for audio issues
            }
        }
        
        function playEnterSound() {
            if (!audioContext) return;
            
            try {
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();
                
                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);
                
                oscillator.type = 'sine';
                oscillator.frequency.value = 1200;
                gainNode.gain.value = 0.1;
                
                oscillator.start();
                oscillator.stop(audioContext.currentTime + 0.1);
            } catch (e) {
                // Silent fail for audio issues
            }
        }
        
        // Initialize audio on first user interaction
        document.addEventListener('click', initAudio, { once: true });
        document.addEventListener('keydown', initAudio, { once: true });

        // Handle connection open
        socket.onopen = function(event) {
            console.log("WebSocket connection opened");
        };

        // Handle messages from server
        socket.onmessage = function(event) {
            const data = JSON.parse(event.data);
            
            if (data.action === "clear") {
                output.innerHTML = '';
                return;
            }
            
            if (data.type === "prompt") {
                prompt.textContent = data.text;
                return;
            }
            
            if (data.type === "output") {
                const textElement = document.createElement('span');
                textElement.className = `output-text ${data.color || ''}`;
                textElement.textContent = data.text;
                output.appendChild(textElement);
                scrollToBottom();
                return;
            }
            
            // Handle command history updates
            if (data.type === "history") {
                commandHistory = data.commands;
                return;
            }
            
            // Handle available commands for autocomplete
            if (data.type === "commands") {
                availableCommands = data.commands;
                return;
            }
            
            // Handle autocomplete suggestions
            if (data.type === "autocomplete") {
                suggestions = data.matches;
                selectedSuggestion = 0;
                if (suggestions.length > 0) {
                    // Apply first suggestion
                    const firstSuggestion = suggestions[0];
                    const currentInput = input.value;
                    const parts = currentInput.split(' ');
                    if (parts.length > 1) {
                        parts[parts.length - 1] = firstSuggestion;
                        input.value = parts.join(' ');
                    } else {
                        // For single word commands, replace the whole input
                        input.value = firstSuggestion;
                    }
                }
                return;
            }
        };

        // Request autocomplete suggestions
        function requestAutocomplete() {
            const value = input.value;
            const parts = value.split(' ');
            if (parts.length > 1) {
                // We have a command and arguments, autocomplete the last argument
                const lastPart = parts[parts.length - 1];
                socket.send(JSON.stringify({
                    type: "autocomplete",
                    text: lastPart
                }));
            } else {
                // We only have a command, don't autocomplete
                return;
            }
        }

        // Handle command input
        input.addEventListener('keydown', (e) => {
            // Play key press sound for most keys
            if (e.key.length === 1) {
                playKeyPressSound();
            }
            
            // Handle Tab key for autocomplete
            if (e.key === 'Tab') {
                e.preventDefault();
                requestAutocomplete();
                return;
            }
            
            // Handle command history navigation
            if (e.key === 'ArrowUp') {
                e.preventDefault();
                if (commandHistory.length > 0) {
                    if (historyIndex === -1) {
                        // Save current input if any
                        input.dataset.current = input.value;
                    }
                    historyIndex = Math.min(historyIndex + 1, commandHistory.length - 1);
                    input.value = commandHistory[commandHistory.length - 1 - historyIndex];
                }
                return;
            }
            
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                if (historyIndex >= 0) {
                    historyIndex--;
                    if (historyIndex === -1) {
                        // Restore current input if it was saved
                        input.value = input.dataset.current || '';
                    } else {
                        input.value = commandHistory[commandHistory.length - 1 - historyIndex];
                    }
                }
                return;
            }
            
            // Reset history index when typing
            if (e.key.length === 1 && e.key !== ' ') {
                historyIndex = -1;
            }
            
            if (e.key === 'Enter') {
                playEnterSound();
                const command = input.value;
                
                // Reset history navigation
                historyIndex = -1;
                delete input.dataset.current;
                
                // Don't send empty commands
                if (command.trim() === '') {
                    // Add empty line to output
                    const commandElement = document.createElement('div');
                    commandElement.innerHTML = `<span id="prompt">${prompt.textContent}</span>`;
                    output.appendChild(commandElement);
                    scrollToBottom();
                    return;
                }
                
                // Send command to server
                socket.send(JSON.stringify({type: "command", text: command}));
                
                // Add command to output
                const commandElement = document.createElement('div');
                commandElement.innerHTML = `<span id="prompt">${prompt.textContent}</span>${command}`;
                output.appendChild(commandElement);
                
                input.value = '';
                scrollToBottom();
            }
        });

        // Scroll to bottom of terminal
        function scrollToBottom() {
            const terminal = document.getElementById('terminal');
            terminal.scrollTop = terminal.scrollHeight;
        }

        // Focus input when clicking anywhere on terminal
        document.getElementById('terminal').addEventListener('click', () => {
            input.focus();
        });
        
        // Focus input when clicking anywhere on window
        document.getElementById('window').addEventListener('click', () => {
            input.focus();
        });
    </script>
</body>
</html>
"""

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    terminal = AmigaTerminal()
    
    # Send initial prompt
    await ws.send_str(json.dumps({
        "type": "prompt",
        "text": terminal.get_prompt()
    }))
    
    # Send command history
    await ws.send_str(json.dumps({
        "type": "history",
        "commands": terminal.command_history
    }))
    
    # Send available commands for autocomplete
    await ws.send_str(json.dumps({
        "type": "commands",
        "commands": terminal.get_available_commands()
    }))
    
    # Send welcome message and startup sequence output
    welcome_msg = terminal.info_command()
    await ws.send_str(json.dumps({
        "type": "output",
        "text": welcome_msg
    }))
    
    # Execute startup sequence and send output
    startup_output = terminal._execute_startup_sequence()
    if startup_output:
        await ws.send_str(json.dumps({
            "type": "output",
            "text": startup_output
        }))
    
    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            try:
                data = json.loads(msg.data)
                if data.get("type") == "command":
                    command_text = data.get("text", "")
                    
                    # Execute command
                    result = terminal.execute_command(command_text)
                    
                    # Send updated command history
                    await ws.send_str(json.dumps({
                        "type": "history",
                        "commands": terminal.command_history
                    }))
                    
                    # Send updated available commands (in case any were added)
                    await ws.send_str(json.dumps({
                        "type": "commands",
                        "commands": terminal.get_available_commands()
                    }))
                    
                    # Handle special actions like clear
                    if isinstance(result, dict) and result.get("action") == "clear":
                        await ws.send_str(json.dumps({
                            "action": "clear"
                        }))
                    elif result:
                        # Send command output
                        await ws.send_str(json.dumps({
                            "type": "output",
                            "text": result
                        }))
                    
                    # Send updated prompt
                    await ws.send_str(json.dumps({
                        "type": "prompt",
                        "text": terminal.get_prompt()
                    }))
                elif data.get("type") == "autocomplete":
                    # Handle autocomplete request
                    path_prefix = data.get("text", "")
                    matches = terminal.get_directory_contents(path_prefix)
                    await ws.send_str(json.dumps({
                        "type": "autocomplete",
                        "matches": matches
                    }))
            except Exception as e:
                await ws.send_str(json.dumps({
                    "type": "output",
                    "text": f"Error: {str(e)}\n",
                    "color": "red"
                }))
        elif msg.type == WSMsgType.ERROR:
            print(f"WebSocket error: {ws.exception()}")
    
    return ws

async def index_handler(request):
    return web.Response(text=HTML_CONTENT, content_type='text/html')

async def init_app():
    app = web.Application()
    app.router.add_get('/', index_handler)
    app.router.add_get('/ws', websocket_handler)
    return app

def main():
    parser = argparse.ArgumentParser(description='WSA Terminal - Windows Subsystem for Amiga')
    parser.add_argument('--port', type=int, default=3000, help='Port to run the server on (default: 3000)')
    parser.add_argument('--host', default='localhost', help='Host to bind to (default: localhost)')
    
    args = parser.parse_args()
    
    print(f"Starting WSA Terminal on http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop the server")
    
    try:
        app = init_app()
        web.run_app(app, host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("\nServer stopped")

if __name__ == '__main__':
    main()