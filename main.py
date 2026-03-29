import tkinter as tk
import subprocess
import threading
import re
import sys
from pathlib import Path
from tkinter import ttk

# --- Configuración ---
MONITORS = [1, 2]
STEPS = [0, 5, 10, 15, 20, 25, 30]

# Temperaturas de color: mínimo, máximo y 3 intermedias
TEMPS = [10000, 8716, 7430, 6144, 4858, 3572, 2286, 1000]

# Colores en escala de grises
BG_COLOR = "#2b2b2b"       # fondo principal
FRAME_COLOR = "#3a3a3a"    # fondo de frames
BTN_COLOR = "#5a5a5a"      # botón normal
BTN_HOVER = "#707070"      # botón al pasar mouse
TXT_COLOR = "#ffffff"      # texto blanco


# --- Funciones de control ---
def get_vcp(monitor_id, code):
    """Get VCP value from monitor"""
    try:
        output = subprocess.check_output(
            ['ddcutil', '--display', str(monitor_id), 'getvcp', str(code)],
            stderr=subprocess.DEVNULL
        ).decode()
        match = re.search(r"current value = (\d+), max value = (\d+)", output)
        if match:
            return int(match.group(1)), int(match.group(2))
    except subprocess.CalledProcessError:
        return 50, 100
    return 50, 100


def set_vcp(monitor_id, code, value):
    """Set VCP value for monitor in background thread"""
    def worker():
        subprocess.run(
            ['ddcutil', '--display', str(monitor_id), 'setvcp', str(code), str(value)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    threading.Thread(target=worker, daemon=True).start()


def set_temperature(value):
    """Set color temperature using GNOME settings in background thread"""
    def worker():
        subprocess.run([
            'gsettings', 'set',
            'org.gnome.settings-daemon.plugins.color',
            'night-light-temperature',
            str(value)
        ])
    threading.Thread(target=worker, daemon=True).start()


# --- Funciones de GUI ---
def create_header(root):
    """Create application header"""
    tk.Label(root, text="Control de Brillo, Contraste y Luz Nocturna",
            font=("Arial", 14), bg=BG_COLOR, fg=TXT_COLOR).pack(pady=10)


def create_main_frame(root):
    """Create main container frame"""
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(padx=10, pady=10, fill="both")
    return main_frame


def create_monitor_controls(main_frame, monitor_id):
    """Create controls for a single monitor"""
    frame_monitor = tk.Frame(main_frame, bg=FRAME_COLOR, relief="groove", borderwidth=2, padx=10, pady=10)
    frame_monitor.pack(side='left', padx=10, fill='y')
    
    # Monitor title
    tk.Label(frame_monitor, text=f"Monitor {monitor_id}", font=("Arial", 12, "bold"),
            bg=FRAME_COLOR, fg=TXT_COLOR).pack(pady=5)
    
    # Brightness controls
    create_brightness_controls(frame_monitor, monitor_id)
    
    # Contrast controls
    create_contrast_controls(frame_monitor, monitor_id)
    
    return frame_monitor


def create_brightness_controls(parent_frame, monitor_id):
    """Create brightness control buttons"""
    tk.Label(parent_frame, text="Brillo", bg=FRAME_COLOR, fg=TXT_COLOR).pack()
    current, maximum = get_vcp(monitor_id, 10)
    
    frame_brightness = tk.Frame(parent_frame, bg=FRAME_COLOR)
    frame_brightness.pack(pady=2)
    
    for step in STEPS:
        val = int(maximum * step / 100)
        btn = tk.Button(frame_brightness, text=f"{step}%", width=4,
                        bg=BTN_COLOR, fg=TXT_COLOR,
                        activebackground=BTN_HOVER,
                        command=lambda v=val, m=monitor_id: set_vcp(m, 10, v))
        btn.pack(side='left', padx=2)


def create_contrast_controls(parent_frame, monitor_id):
    """Create contrast control buttons"""
    tk.Label(parent_frame, text="Contraste", bg=FRAME_COLOR, fg=TXT_COLOR).pack()
    current, maximum = get_vcp(monitor_id, 12)
    
    frame_contrast = tk.Frame(parent_frame, bg=FRAME_COLOR)
    frame_contrast.pack(pady=2)
    
    for step in STEPS:
        val = int(maximum * step / 100)
        btn = tk.Button(frame_contrast, text=f"{step}%", width=4,
                        bg=BTN_COLOR, fg=TXT_COLOR,
                        activebackground=BTN_HOVER,
                        command=lambda v=val, m=monitor_id: set_vcp(m, 12, v))
        btn.pack(side='left', padx=2)


def create_temperature_controls(root):
    """Create color temperature control section"""
    frame_temp = tk.Frame(root, bg=FRAME_COLOR, relief="groove", borderwidth=2, padx=10, pady=10)
    frame_temp.pack(pady=15, fill="x")
    
    # Temperature title
    tk.Label(frame_temp, text="Temperatura de color (Luz nocturna GNOME)",
            font=("Arial", 12, "bold"), bg=FRAME_COLOR, fg=TXT_COLOR).pack(padx=10, pady=10)
    
    # Temperature buttons
    frame_temp_buttons = tk.Frame(frame_temp, bg=FRAME_COLOR)
    frame_temp_buttons.pack()
    
    for t in TEMPS:
        btn = tk.Button(frame_temp_buttons, text=str(t), width=8,
                        bg=BTN_COLOR, fg=TXT_COLOR,
                        activebackground=BTN_HOVER,
                        command=lambda v=t: set_temperature(v))
        btn.pack(side='left', padx=5, pady=2)


def setup_gui():
    """Setup and create the complete GUI"""
    root = tk.Tk()
    root.title("Control de Monitores")
    root.configure(bg=BG_COLOR)
    
    # Create GUI components
    create_header(root)
    main_frame = create_main_frame(root)
    
    # Create monitor controls
    for monitor_id in MONITORS:
        create_monitor_controls(main_frame, monitor_id)
    
    # Create temperature controls
    create_temperature_controls(root)
    
    return root


def main():
    """Main entry point - setup and run the application"""
    try:
        # Setup GUI
        root = setup_gui()
        
        # Run application
        root.mainloop()
        
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error running application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
