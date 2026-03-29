# BrilloPantallas - Project Overview

## 📋 Summary
Python GUI app for display brightness, contrast, and blue light management.

## 🏗️ Architecture

### Frontend (`src/frontend/gui_app.py`)
- `MainWindowApp` class - tkinter GUI with dark mode
- Uses `AppController` for backend communication
- Stores UI state via `UIService`

### Backend (`src/backend/`)
- `controllers.py` - `AppController` orchestrates services
  - Display methods: `list_monitors()`, `get/set_brightness()`, `get/set_contrast()`, `get/set_blue_light()`
  - Hardware methods: `get/set_hardware_brightness()`
  - Redshift methods: `install_redshift()`, `set_redshift_temperature()`, `reset_redshift()`, `get_redshift_status()`

- `services.py` - Business logic services
  - `ConfigService` - .env configuration
  - `UIService` - UI state management
  - `DataService` - key-value storage
  - `DisplayService` - xrandr + /sys/class/backlight/ operations
  - `RedshiftService` - redshift installation and control

## 🔧 Features

### Display Control
- Monitor listing (`xrandr --listmonitors`)
- Per-monitor brightness (`xrandr --output MONITOR --brightness VALUE`)
- Contrast/gamma (`xrandr --output MONITOR --gamma R:G:B`)
- Blue light (night mode: `1:1:0.7`, normal: `1:1:1`)

### Hardware Brightness
- `/sys/class/backlight/` control
- Current/max value reading
- Sudo-based adjustment

### System Blue Light
- Redshift installation
- Color temperature control
- Process monitoring

## 📁 Structure
```
brilloPantallas/
├── src/
│   ├── frontend/gui_app.py
│   └── backend/
│       ├── controllers.py
│       └── services.py
├── main.py
├── .env
├── requirements.txt
├── comandos_fix.md
└── venv/
```

## 🔄 Flow
```
Frontend → AppController → Service → System Commands
```

## 🎯 Status
- ✅ Architecture complete
- ✅ All comandos_fix.md commands implemented
- ✅ Dark mode GUI working
- ✅ Backend services ready
- ⏳ GUI controls integration pending
