@echo off
echo WSA Terminal Windows Executable Builder
echo =====================================
echo.

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
    echo Web version executable: dist\wsa ^(This may not be a Windows executable^)
)

if exist dist\wsa_console.exe (
    echo Console version Windows executable: dist\wsa_console.exe
) else (
    echo Console version executable: dist\wsa_console ^(This may not be a Windows executable^)
)

echo.
echo To ensure you get Windows executables:
echo 1. Run this script in Windows Command Prompt ^(not WSL^)
echo 2. Make sure you have Python for Windows installed
echo.
pause