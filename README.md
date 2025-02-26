# Screen Time Manager

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

A desktop application that helps manage screen time using the 20-20-20 rule and hourly breaks, with system tray integration and usage history tracking.

![Application Screenshot](https://raw.githubusercontent.com/memotiur/BlinkReminder/refs/heads/main/screenshots/screentime.png) ## Features

🕒 Dual Timers:
20-20-20 Rule Timer (every 20 minutes)
Hourly Break Timer (every 60 minutes)
🔔 Custom Alerts:
Optional screen dimming for 20 seconds
📊 7-Day Usage History:
Tracks and displays screen time history
⚙️ Customizable Timers:
Adjustable intervals for both timers
📁 History Management:
Automatically saves and cleans up history files
🖥️ System Tray Support:
Minimizes to tray for easy access

## Installation

### Prerequisites

- Python 3.8+
- pip package manager

### Dependencies

```bash
pip install plyer pystray Pillow
```


## Generate .exe file

```
powershell -ExecutionPolicy Bypass -File .\build_commands.ps1
```

## RESET Default Setting

```
Set-ExecutionPolicy Restricted -Scope CurrentUser
