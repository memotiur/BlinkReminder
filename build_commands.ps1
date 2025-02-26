$ErrorActionPreference = "Stop"

# Clean previous builds
Remove-Item -Path "build", "dist" -Recurse -Force -ErrorAction SilentlyContinue

# Install requirements
pip install pyinstaller plyer pystray Pillow

# Build executable
pyinstaller --noconfirm --onefile --windowed `
    --icon "icon.ico" `
    --name "ScreenTimeReminder" `
    --hidden-import "pystray._win32" `
    --hidden-import "plyer.platforms.win.notification" `
    --hidden-import "plyer.platforms.win.libs.balloontip" `
    screentime.py

# Open output directory
explorer.exe ".\dist"