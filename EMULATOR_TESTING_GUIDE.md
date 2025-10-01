# Test Emulator Shared Folder Integration
# This file demonstrates how to test the new emulator integration features

## 🧪 Testing Instructions

### 1. Test Basic Mount Command
```bash
python3 wsa_console.py --no-intro
mount
```
Should show: "Mounted volumes:" with DH0:, SYS:, RAM:, C: listed

### 2. Test Configuration Listing (if you have WinUAE installed)
```bash
mount list winuae
mount list fs-uae
mount list
```

### 3. Test Manual Configuration Creation (for testing without emulators)

Create a test WinUAE config file:
```bash
mkdir -p /tmp/test-winuae-configs
```

Create `/tmp/test-winuae-configs/test-config.uae`:
```
# Test WinUAE Configuration
filesystem2=rw,DH1:TestShare:/tmp,0
filesystem2=ro,DF0:ReadOnly:/home,0
```

Modify the WINUAE_CONFIG path temporarily:
```python
# In wsa_console.py, line ~25, change:
# 'config_dir': os.environ.get('WINUAE_CONFIG_DIR', r'C:\Users\Public\Documents\Amiga Files\WinUAE\Configurations'),
# To:
'config_dir': '/tmp/test-winuae-configs',
```

### 4. Test Mounting Shared Folder
```bash
mount DH1: FROM WINUAE "test-config.uae"
cd DH1:
dir
```

### 5. Test Directory Navigation
```bash
mount SHARED: FROM WINUAE "test-config.uae"
cd SHARED:
dir
cd subdirectory  # (if exists)
dir
cd ..
```

## 🎯 Expected Results

1. **Configuration Detection**: Should find and parse .uae and .fs-uae files
2. **Shared Folder Mounting**: Should mount configured shared folders as virtual drives
3. **Directory Navigation**: Should allow cd/dir commands within shared folders
4. **Real File Access**: Should show actual files from the host file system
5. **Authentic Formatting**: Should display files in authentic Amiga DIR format

## 🐛 Troubleshooting

### No Configurations Found
- Make sure WinUAE/FS-UAE are installed
- Check configuration directories exist
- Verify .uae/.fs-uae files have valid syntax

### Permission Errors
- Ensure shared folder paths are accessible
- Check file/directory permissions
- Verify paths exist on the file system

### Syntax Errors
- Run: `python3 -c "import wsa_console; print('OK')"`
- Check for missing imports or typos

## 🚀 Advanced Testing

### Create Complex WinUAE Config
```
filesystem2=rw,DH1:Development:C:\Projects,0
filesystem2=rw,DH2:Games:C:\Games,0
filesystem2=ro,DF0:System:C:\Windows\System32,0
```

### Test Multiple Mounts
```bash
mount DEV: FROM WINUAE "config1.uae"
mount GAMES: FROM WINUAE "config2.uae" 
mount SHARED: FROM FS-UAE "workbench.fs-uae"
mount list
cd DEV:
dir
cd ../GAMES:
dir
```

### Test Error Handling
```bash
mount INVALID: FROM WINUAE "nonexistent.uae"
mount DH0: FROM BADEMU "test.config"
cd NONEXISTENT:/invalid/path
```

Should show appropriate error messages for each case.

---
**Status**: Phase 2 Implementation Complete ✅
**Next**: Test with real WinUAE/FS-UAE installations