@echo off
echo Installing PyInstaller...
pip install pyinstaller

echo Creating console executable...
pyinstaller --onefile --name wsa_console wsa_console.py

echo.
echo Console executable created in the 'dist' folder.
echo You can run it with: dist\wsa_console.exe
pause