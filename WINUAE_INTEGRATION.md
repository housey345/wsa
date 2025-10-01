# WinUAE Integration for WSA Terminal

## Overview

WSA Terminal now includes WinUAE integration, allowing you to launch the WinUAE Amiga emulator directly from the Amiga-style command line interface.

## Configuration

The WinUAE integration uses environment variables for configuration, making it easily customizable for different users and installations.

### Environment Variables

Set these environment variables to customize WinUAE paths for your system:

```cmd
rem WinUAE executable path
set WINUAE_PATH=C:\Program Files\WinUAE\winuae.exe

rem Configuration files directory
set WINUAE_CONFIG_DIR=C:\Users\Public\Documents\Amiga Files\WinUAE\Configurations

rem Default configuration file (without .uae extension)
set WINUAE_DEFAULT_CONFIG=MY AGS CONFIG

rem Kickstart ROM directory
set WINUAE_KICKSTART_DIR=C:\Users\Public\Documents\Amiga Files\WinUAE\Kickstarts

rem Hard disk files directory
set WINUAE_HDF_DIR=C:\Users\Public\Documents\Amiga Files\WinUAE\Hardfiles
```

### PowerShell Configuration

For PowerShell users:

```powershell
$env:WINUAE_PATH = "C:\Program Files\WinUAE\winuae.exe"
$env:WINUAE_CONFIG_DIR = "C:\Users\Public\Documents\Amiga Files\WinUAE\Configurations"
$env:WINUAE_DEFAULT_CONFIG = "MY AGS CONFIG"
$env:WINUAE_KICKSTART_DIR = "C:\Users\Public\Documents\Amiga Files\WinUAE\Kickstarts"
$env:WINUAE_HDF_DIR = "C:\Users\Public\Documents\Amiga Files\WinUAE\Hardfiles"
```

### Default Paths

If no environment variables are set, the following defaults are used:

- **Executable**: `C:\Program Files\WinUAE\winuae.exe`
- **Config Directory**: `C:\Users\Public\Documents\Amiga Files\WinUAE\Configurations`
- **Default Config**: `MY AGS CONFIG.uae`
- **Kickstart Directory**: `C:\Users\Public\Documents\Amiga Files\WinUAE\Kickstarts`
- **HDF Directory**: `C:\Users\Public\Documents\Amiga Files\WinUAE\Hardfiles`

## Usage

### Basic Commands

1. **Launch with default configuration:**

   ```
   SYS:> winuae
   ```

2. **Launch with specific configuration:**

   ```
   SYS:> winuae "My Custom Config"
   ```

3. **List available configurations:**

   ```
   SYS:> winuae list
   ```

4. **Show configuration information:**

   ```
   SYS:> winuae config
   ```

5. **Get help:**
   ```
   SYS:> help winuae
   ```

### Configuration File Access

WinUAE configurations are accessed from the C: directory:

```
SYS:> C:
C:> dir
```

You'll see WinUAE listed among the available commands.

## Example Setup

### For Your Configuration

Based on your setup with the path `C:\Users\Public\Documents\Amiga Files\WinUAE\Configurations\MY AGS CONFIG.uae`:

1. **Set environment variables** (if needed):

   ```cmd
   set WINUAE_PATH=C:\Program Files\WinUAE\winuae.exe
   set WINUAE_CONFIG_DIR=C:\Users\Public\Documents\Amiga Files\WinUAE\Configurations
   set WINUAE_DEFAULT_CONFIG=MY AGS CONFIG
   ```

2. **Launch WSA Terminal:**

   ```cmd
   python wsa_console.py
   ```

3. **Run WinUAE:**
   ```
   SYS:> winuae
   ```

This will automatically use your "MY AGS CONFIG.uae" configuration file.

### For Different Users

Users with different installations can set their own environment variables:

**User with WinUAE in Program Files (x86):**

```cmd
set WINUAE_PATH=C:\Program Files (x86)\WinUAE\winuae.exe
set WINUAE_CONFIG_DIR=C:\Users\%USERNAME%\Documents\WinUAE\Configurations
```

**User with WinUAE in a custom directory:**

```cmd
set WINUAE_PATH=D:\Emulators\WinUAE\winuae.exe
set WINUAE_CONFIG_DIR=D:\Emulators\WinUAE\Configs
set WINUAE_DEFAULT_CONFIG=Workbench31
```

## Features

- **Automatic executable detection** with fallback paths
- **Environment variable configuration** for portability
- **Configuration file listing** and validation
- **Background process launch** - WinUAE runs independently
- **Error handling** with helpful messages
- **Cross-platform path handling**

## Troubleshooting

### WinUAE Not Found

If you see "WinUAE executable not found":

1. Install WinUAE from http://www.winuae.net/
2. Set the `WINUAE_PATH` environment variable to your WinUAE installation
3. Check that the path exists and the file is accessible

### Configuration File Not Found

If your configuration file isn't found:

1. Use `winuae list` to see available configurations
2. Check that the configuration directory exists
3. Verify the configuration file has a `.uae` extension
4. Set `WINUAE_CONFIG_DIR` to the correct directory

### Launch Issues

If WinUAE fails to launch:

1. Try running WinUAE manually first to ensure it works
2. Check that the configuration file is valid
3. Ensure you have proper permissions to execute WinUAE

## Integration Benefits

- **Authentic Amiga experience**: Launch real Amiga emulation from a simulated Amiga environment
- **Seamless workflow**: No need to exit WSA Terminal to access your Amiga systems
- **Configuration management**: Easy access to multiple Amiga setups
- **Portable setup**: Environment variables make it work across different user configurations
