@echo off
echo WSA Terminal Executable Builder
echo ==============================
echo.

REM Check if we're running in WSL
echo Checking environment...
echo.

REM Try to detect if we're in WSL
where wsl.exe >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Note: You appear to be running in Windows. This script will create Windows executables.
    echo.
) else (
    echo Note: You appear to be running in WSL/Linux. This script will create Linux executables.
    echo To create Windows executables, run this script in Windows Command Prompt.
    echo.
)

echo Installing PyInstaller...
pip install pyinstaller

echo.
echo Creating web executable...
pyinstaller --onefile --name wsa wsa.py

echo.
echo Creating console executable...
pyinstaller --onefile --name wsa_console wsa_console.py

echo.
echo Build complete!
echo =============

if exist dist\wsa.exe (
    echo Web version Windows executable: dist\wsa.exe
) else (
    echo Web version executable: dist\wsa
)

if exist dist\wsa_console.exe (
    echo Console version Windows executable: dist\wsa_console.exe
) else (
    echo Console version executable: dist\wsa_console
)

echo.
echo Note: If you need Windows executables, please run this script in Windows Command Prompt,
echo not in WSL. The current executables are for %OS%.
echo.
pause