# How to Use WSA Terminal Startup Sequences

This guide shows you how to make WSA Terminal fully functional with custom startup sequences.

## Prerequisites

Make sure you have WSA Terminal installed and working:

```bash
cd /path/to/wsa
python wsa_console.py
```

## Editing the Startup Sequence

1. **Start WSA Terminal**

   ```bash
   python wsa_console.py
   ```

2. **Edit the startup sequence**

   ```bash
   ed SYS:S/Startup-Sequence
   ```

3. **Add your custom commands**
   Replace the existing content with your custom startup sequence. For example:

   ```
   ; My Custom WSA Terminal Startup
   echo "Welcome to WSA Terminal!"
   date
   echo "Terminal is ready for use"
   ```

4. **Save the file**

   - Press `Ctrl+X` to save and exit
   - Press `Ctrl+C` to cancel without saving

5. **Exit WSA Terminal**

   ```bash
   exit
   ```

6. **Restart to see your changes**
   ```bash
   python wsa_console.py
   ```

## Example Startup Sequences

### Basic Example

```
; Basic Startup Sequence
echo "WSA Terminal Starting..."
echo "Have a productive session!"
```

### Advanced Example

```
; Advanced Startup Sequence
echo "=================================="
echo "  WSA Terminal - Fully Functional"
echo "=================================="
echo ""
echo "System Information:"
info
echo ""
echo "Current Date and Time:"
date
echo ""
echo "Mounted Volumes:"
mount
echo ""
echo "Terminal Ready!"
```

### Practical Example

```
; Practical Startup Sequence
echo "Loading development environment..."
; cd DH0:Projects  ; Uncomment to start in your projects directory
echo "Development environment ready"
```

## Supported Commands in Startup Sequences

You can use any valid Amiga commands in your startup sequence:

- `echo <text>` - Display text
- `date` - Show current date and time
- `info` - Display system information
- `mount` - Show mounted volumes
- `cd <directory>` - Change directory
- `dir` - List directory contents
- `avail` - List available commands
- `status` - Show system status
- `ping <host>` - Network ping (simulated)
- `pattern <pattern>` - Pattern matching
- `execute <script>` - Run another script

## Script Locations

WSA Terminal looks for startup sequences in this order:

1. `SYS:S/Startup-Sequence` (virtual file system)
2. `DH0:S/Startup-Sequence` (Windows C: drive)
3. `S:Startup-Sequence`
4. `SYS:S/startup-sequence`

## Manual Script Execution

You can manually execute any script with the EXECUTE command:

```bash
execute SYS:S/Startup-Sequence
```

## Verifying Your Changes

To verify your startup sequence is working:

1. Add a distinctive echo command:

   ```
   echo "=== MY CUSTOM STARTUP ==="
   ```

2. Save and restart WSA Terminal
3. You should see your message at startup

## Troubleshooting

### If your startup sequence doesn't execute:

1. Check that you saved the file correctly (Ctrl+X)
2. Verify the file path is correct (`SYS:S/Startup-Sequence`)
3. Ensure there are no syntax errors in your commands
4. Check that WSA Terminal is reading from the correct location

### If you want to reset to default:

1. Edit the startup sequence:

   ```bash
   ed SYS:S/Startup-Sequence
   ```

2. Replace with the default content:

   ```
   ; AmigaOS-style startup sequence
   ; This script runs when the WSA Terminal starts

   ; Mount additional volumes
   ; mount RAM: FROM RAM SIZE=1024

   ; Set environment variables
   ; setenv PATH C: SYS:S

   ; Run system tools
   ; execute SYS:Tools/Shell-Startup
   ```

## Making WSA Fully Functional

This startup sequence feature makes WSA Terminal fully functional because:

1. **Persistence**: Changes are saved and persist between sessions
2. **Automation**: Commands execute automatically at startup
3. **Customization**: You can tailor the environment to your needs
4. **Integration**: Works with the actual file system (DH0:)
5. **Extensibility**: Supports all Amiga commands and custom scripts

WSA Terminal is not a mockup - it's a fully functional Amiga-style terminal with real startup sequence capabilities!
