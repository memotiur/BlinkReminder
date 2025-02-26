# Screen Time Manager

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

A desktop application that helps manage screen time using the 20-20-20 rule and hourly breaks, with system tray integration and usage history tracking.

![Application Screenshot](screenshot.png) ## Features

- 🕒 Dual Timers:
  - 20-20-20 Rule Timer (20 minutes interval)
  - Hourly Break Timer (60 minutes interval)
- 🔔 Alert with Fade Animations
- 📊 7-Day Usage History Tracking
- ⚙️ Adjustable Timer Settings
- 📁 Automatic History File Management
- 🖥️ System Tray Integration

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