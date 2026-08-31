import tkinter as tk
import subprocess
import threading
import re
import sys
import os
from pathlib import Path
from tkinter import ttk

try:
    from componentes.TemperatureCinnamonManager import TemperatureCinnamonManager
    CINNAMON_MANAGER = TemperatureCinnamonManager()
except (ImportError, FileNotFoundError):
    CINNAMON_MANAGER = None

try:
    from componentes.TemperatureGNOMEManager import set_temperature as gnome_set_temperature
except (ImportError, FileNotFoundError):
    def gnome_set_temperature(value):
        def worker():
            subprocess.run([
                'gsettings', 'set',
                'org.gnome.settings-daemon.plugins.color',
                'night-light-temperature',
                str(value)
            ])
        threading.Thread(target=worker, daemon=True).start()

# --- Configuración de gestores externos ---
MANAGER = None  # "redshift" o "f.lux"
MONITOR_IDS = []  # Lista para guardar los IDs de los monitores

# --- Configuración ---
MONITORS = [1, 2]
STEPS = [0, 5, 10, 15, 20, 25, 30]

# Colores en escala de grises
BG_COLOR = "#2b2b2b"       # fondo principal
FRAME_COLOR = "#3a3a3a"    # fondo de frames
BTN_COLOR = "#5a5a5a"      # botón normal
BTN_HOVER = "#707070"      # botón al pasar mouse
ACTIVE_COLOR = "#3f9d5a"   # botón iluminado (valor actual)
TXT_COLOR = "#ffffff"      # texto blanco

# Responsive: se ajustan al arrancar según el tamaño de pantalla
COMPACT = False          # True = tamaños reducidos en pantallas pequeñas
MONITOR_COLUMNS = 2      # columnas para los paneles de monitores


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


def detect_desktop_environment():
    """Detect the current desktop environment (Cinnamon or GNOME)."""
    xdg = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    session = os.environ.get("DESKTOP_SESSION", "").lower()
    combined = f"{xdg} {session}"

    if "cinnamon" in combined:
        return "cinnamon"
    if "gnome" in combined:
        return "gnome"

    try:
        output = subprocess.check_output(
            ['pgrep', '-l', '.'], stderr=subprocess.DEVNULL
        ).decode().lower()
        if 'cinnamon' in output:
            return 'cinnamon'
        if 'gnome-shell' in output:
            return 'gnome'
    except subprocess.CalledProcessError:
        pass

    return None


DESKTOP_ENVIRONMENT = detect_desktop_environment()


def filter_percent_to_temp(percent):
    """Convert blue light filter percentage (0-100) to temperature in Kelvin.
    0% = sin filtro (6500K neutro), 100% = filtro máximo (1000K cálido)."""
    percent = max(0, min(100, percent))
    return int(6500 - percent * 55)


def set_temperature(value):
    """Set color temperature using the manager for the detected desktop."""
    if (DESKTOP_ENVIRONMENT == "cinnamon"
            and CINNAMON_MANAGER is not None
            and CINNAMON_MANAGER.is_ready()):
        def worker():
            CINNAMON_MANAGER.set_temperature(value)
        threading.Thread(target=worker, daemon=True).start()
    else:
        gnome_set_temperature(value)


# Gamma RGB que redshift aplica para cada preset de filtro (0-100%)
REDSHIFT_GAMMA = {
    0: (1.0, 1.0),
    20: (1.1, 1.2),
    40: (1.2, 1.5),
    60: (1.4, 2.1),
    80: (1.8, 3.8),
    100: (3.5, None),  # el canal B tiende a infinito a 1000 K
}


def read_current_gamma():
    """Reads the current gamma (g, b) of the first monitor or None."""
    try:
        output = subprocess.check_output(
            ['xrandr', '--verbose'], stderr=subprocess.DEVNULL
        ).decode()
        match = re.search(r'Gamma:\s+(\S+):(\S+):(\S+)', output)
        if not match:
            return None
        _, g, b = match.groups()
        b = float(b) if b.lower() != 'inf' else None
        return float(g), b
    except Exception:
        return None


def match_temp_percent():
    """Matches the current screen gamma to a preset filter percentage.

    Returns the matching percent (0-100) or None if it doesn't coincide.
    """
    gamma = read_current_gamma()
    if not gamma:
        return None
    current_g, current_b = gamma
    best, best_error = None, float('inf')
    for percent, (target_g, target_b) in REDSHIFT_GAMMA.items():
        error = abs(current_g - target_g) / target_g
        if target_b is not None and current_b is not None:
            error += abs(current_b - target_b) / target_b
        if error < best_error:
            best, best_error = percent, error
    return best if best_error < 0.08 else None


def read_gnome_percent():
    """Reads the current night-light temperature from GNOME as a percentage."""
    try:
        output = subprocess.check_output([
            'gsettings', 'get',
            'org.gnome.settings-daemon.plugins.color',
            'night-light-temperature'
        ]).decode()
        match = re.search(r'\d+', output)
        if not match:
            return None
        temp = max(1000, min(6500, int(match.group())))
        return round((6500 - temp) / 55)
    except Exception:
        return None


def read_current_filter_percent():
    """Returns the currently applied filter percentage, or None if unknown."""
    if (DESKTOP_ENVIRONMENT == "cinnamon"
            and CINNAMON_MANAGER is not None
            and CINNAMON_MANAGER.is_ready()):
        return match_temp_percent()
    return read_gnome_percent()


def make_highlight_group():
    """Creates a highlighter for one group of buttons (brillo, contraste, etc.).

    Returns a function that highlights a button in its own group, clearing
    the previously active one. Passing None clears the highlight.
    """
    active = {"button": None}

    def set_active(button):
        if active["button"] is not None:
            active["button"].config(bg=BTN_COLOR)
        active["button"] = button
        if button is not None:
            button.config(bg=ACTIVE_COLOR)

    return set_active


# --- Funciones de GUI ---
def make_scrollable(parent):
    """Envuelve el contenido en un canvas con scroll vertical.

    Permite usar la app en pantallas pequeñas sin que los controles
    se corten: si el contenido no cabe, aparece una barra de scroll.
    """
    canvas = tk.Canvas(parent, bg=BG_COLOR, highlightthickness=0)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    content = tk.Frame(canvas, bg=BG_COLOR)
    window_id = canvas.create_window((0, 0), window=content, anchor="nw")

    def update_scrollregion(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def sync_width(event):
        canvas.itemconfig(window_id, width=event.width)

    content.bind("<Configure>", update_scrollregion)
    canvas.bind("<Configure>", sync_width)

    def on_mousewheel(event):
        canvas.yview_scroll(int(-event.delta / 120), "units")

    def on_linux_scroll(event):
        canvas.yview_scroll(-1 if event.num == 4 else 1, "units")

    canvas.bind_all("<MouseWheel>", on_mousewheel)
    canvas.bind_all("<Button-4>", on_linux_scroll)
    canvas.bind_all("<Button-5>", on_linux_scroll)

    return canvas, content


def create_header(parent):
    """Create application header"""
    font = ("Arial", 13) if COMPACT else ("Arial", 14)
    tk.Label(parent, text="Control de Brillo, Contraste y Luz Nocturna",
            font=font, bg=BG_COLOR, fg=TXT_COLOR).pack(pady=8)


def create_main_frame(parent):
    """Create main container frame with responsive monitor columns"""
    main_frame = tk.Frame(parent, bg=BG_COLOR)
    main_frame.pack(padx=10, pady=10, fill="both")
    for col in range(MONITOR_COLUMNS):
        main_frame.grid_columnconfigure(col, weight=1, uniform="monitor")
    return main_frame


def create_monitor_controls(main_frame, monitor_id, column):
    """Create controls for a single monitor"""
    pad = 8 if COMPACT else 10
    frame_monitor = tk.Frame(main_frame, bg=FRAME_COLOR, relief="groove", borderwidth=2, padx=pad, pady=pad)
    frame_monitor.grid(row=0, column=column, padx=6, pady=6, sticky="nsew")
    
    # Monitor title
    title_font = ("Arial", 11, "bold") if COMPACT else ("Arial", 12, "bold")
    tk.Label(frame_monitor, text=f"Monitor {monitor_id}", font=title_font,
            bg=FRAME_COLOR, fg=TXT_COLOR).pack(pady=5)
    
    # Brightness controls
    create_brightness_controls(frame_monitor, monitor_id)
    
    # Contrast controls
    create_contrast_controls(frame_monitor, monitor_id)
    
    return frame_monitor


def create_brightness_controls(parent_frame, monitor_id):
    """Create brightness control buttons"""
    entry_w = 4 if COMPACT else 5
    step_w = 3 if COMPACT else 4
    tk.Label(parent_frame, text="Brillo", bg=FRAME_COLOR, fg=TXT_COLOR).pack()
    current, maximum = get_vcp(monitor_id, 10)

    set_active = make_highlight_group()

    def apply_step(step):
        set_vcp(monitor_id, 10, int(maximum * step / 100))
        set_active(step_buttons[step])

    step_buttons = {}
    frame_brightness = tk.Frame(parent_frame, bg=FRAME_COLOR)
    frame_brightness.pack(pady=2)

    for step in STEPS:
        btn = tk.Button(frame_brightness, text=f"{step}%", width=step_w,
                        bg=BTN_COLOR, fg=TXT_COLOR,
                        activebackground=BTN_HOVER,
                        command=lambda s=step: apply_step(s))
        btn.pack(side='left', padx=2)
        step_buttons[step] = btn
    
    # Custom brightness control
    frame_custom = tk.Frame(parent_frame, bg=FRAME_COLOR)
    frame_custom.pack(pady=5)
    
    tk.Label(frame_custom, text="Personalizado:", bg=FRAME_COLOR, fg=TXT_COLOR).pack(side='left')
    
    brightness_entry = tk.Entry(frame_custom, width=entry_w, bg=BTN_COLOR, fg=TXT_COLOR, insertbackground=TXT_COLOR, font=("Arial", 12))
    brightness_entry.pack(side='left', padx=2)
    brightness_entry.insert(0, "50")
    
    def set_custom_brightness():
        try:
            value = int(brightness_entry.get())
            if 0 <= value <= 100:
                set_vcp(monitor_id, 10, int(maximum * value / 100))
                set_active(None)  # valor arbitrario: no coincide, se ignora
            else:
                brightness_entry.delete(0, tk.END)
                brightness_entry.insert(0, "50")
        except ValueError:
            brightness_entry.delete(0, tk.END)
            brightness_entry.insert(0, "50")
    
    tk.Button(frame_custom, text="Aplicar", width=6,
              bg=BTN_COLOR, fg=TXT_COLOR,
              activebackground=BTN_HOVER,
              command=set_custom_brightness).pack(side='left', padx=2)
    
    # Resalta el botón cuyo % coincide con el valor actual del monitor
    for step in STEPS:
        if int(maximum * step / 100) == current:
            set_active(step_buttons[step])
            break


def create_contrast_controls(parent_frame, monitor_id):
    """Create contrast control buttons"""
    entry_w = 4 if COMPACT else 5
    step_w = 3 if COMPACT else 4
    tk.Label(parent_frame, text="Contraste", bg=FRAME_COLOR, fg=TXT_COLOR).pack()
    current, maximum = get_vcp(monitor_id, 12)

    set_active = make_highlight_group()

    def apply_step(step):
        set_vcp(monitor_id, 12, int(maximum * step / 100))
        set_active(step_buttons[step])

    step_buttons = {}
    frame_contrast = tk.Frame(parent_frame, bg=FRAME_COLOR)
    frame_contrast.pack(pady=2)

    for step in STEPS:
        btn = tk.Button(frame_contrast, text=f"{step}%", width=step_w,
                        bg=BTN_COLOR, fg=TXT_COLOR,
                        activebackground=BTN_HOVER,
                        command=lambda s=step: apply_step(s))
        btn.pack(side='left', padx=2)
        step_buttons[step] = btn
    
    # Custom contrast control
    frame_custom = tk.Frame(parent_frame, bg=FRAME_COLOR)
    frame_custom.pack(pady=5)
    
    tk.Label(frame_custom, text="Personalizado:", bg=FRAME_COLOR, fg=TXT_COLOR).pack(side='left')
    
    contrast_entry = tk.Entry(frame_custom, width=entry_w, bg=BTN_COLOR, fg=TXT_COLOR, insertbackground=TXT_COLOR, font=("Arial", 12))
    contrast_entry.pack(side='left', padx=2)
    contrast_entry.insert(0, "50")
    
    def set_custom_contrast():
        try:
            value = int(contrast_entry.get())
            if 0 <= value <= 100:
                set_vcp(monitor_id, 12, int(maximum * value / 100))
                set_active(None)  # valor arbitrario: no coincide, se ignora
            else:
                contrast_entry.delete(0, tk.END)
                contrast_entry.insert(0, "50")
        except ValueError:
            contrast_entry.delete(0, tk.END)
            contrast_entry.insert(0, "50")
    
    tk.Button(frame_custom, text="Aplicar", width=6,
              bg=BTN_COLOR, fg=TXT_COLOR,
              activebackground=BTN_HOVER,
              command=set_custom_contrast).pack(side='left', padx=2)
    
    # Resalta el botón cuyo % coincide con el valor actual del monitor
    for step in STEPS:
        if int(maximum * step / 100) == current:
            set_active(step_buttons[step])
            break


def create_temperature_controls(parent):
    """Create color temperature (blue light filter) control section"""
    preset_w = 5 if COMPACT else 8
    stepper_w = 6 if COMPACT else 8
    title_font = ("Arial", 11, "bold") if COMPACT else ("Arial", 12, "bold")
    frame_temp = tk.Frame(parent, bg=FRAME_COLOR, relief="groove", borderwidth=2, padx=10, pady=10)
    frame_temp.pack(pady=15, fill="x")
    
    # Temperature title
    desktop_name = DESKTOP_ENVIRONMENT.capitalize() if DESKTOP_ENVIRONMENT else "Desktop"
    tk.Label(frame_temp, text=f"Temperatura de color (Luz nocturna {desktop_name})",
            font=title_font, bg=FRAME_COLOR, fg=TXT_COLOR).pack(padx=10, pady=10)
    
    # Current filter status
    percent = tk.IntVar(value=0)
    set_active = make_highlight_group()
    preset_buttons = {}
    
    def refresh_highlight():
        active_pct = percent.get() if percent.get() in preset_buttons else None
        set_active(preset_buttons.get(active_pct) if active_pct is not None else None)
    
    def update_label():
        kelvin = filter_percent_to_temp(percent.get())
        status_label.config(text=f"Filtro de luz azul: {percent.get()}%  ({kelvin} K)")
    
    def set_filter(value):
        percent.set(max(0, min(100, value)))
        kelvin = filter_percent_to_temp(percent.get())
        set_temperature(kelvin)
        update_label()
        refresh_highlight()
    
    def change(delta):
        set_filter(percent.get() + delta)
    
    status_label = tk.Label(frame_temp, text="Filtro de luz azul: 0%  (6500 K)",
                           bg=FRAME_COLOR, fg=TXT_COLOR, font=("Arial", 11, "bold"))
    status_label.pack(pady=6)
    
    # Preset filter levels (0% = sin filtro, 100% = filtro cálido máximo)
    frame_presets = tk.Frame(frame_temp, bg=FRAME_COLOR)
    frame_presets.pack()
    
    for p in (0, 20, 40, 60, 80, 100):
        btn = tk.Button(frame_presets, text=f"{p}%", width=preset_w,
                        bg=BTN_COLOR, fg=TXT_COLOR,
                        activebackground=BTN_HOVER,
                        command=lambda v=p: set_filter(v))
        btn.pack(side='left', padx=5, pady=2)
        preset_buttons[p] = btn
    
    # +/- stepper buttons
    frame_stepper = tk.Frame(frame_temp, bg=FRAME_COLOR)
    frame_stepper.pack(pady=8)
    
    tk.Button(frame_stepper, text="- 10%", width=stepper_w,
              bg=BTN_COLOR, fg=TXT_COLOR,
              activebackground=BTN_HOVER,
              command=lambda: change(-10)).pack(side='left', padx=5)
    tk.Button(frame_stepper, text="+ 10%", width=stepper_w,
              bg=BTN_COLOR, fg=TXT_COLOR,
              activebackground=BTN_HOVER,
              command=lambda: change(10)).pack(side='left', padx=5)
    
    # Reset button: filter back to 0%
    tk.Button(frame_temp, text="Reiniciar luz azul (0%)", width=(18 if COMPACT else 22),
              bg=BTN_COLOR, fg=TXT_COLOR,
              activebackground=BTN_HOVER,
              command=lambda: set_filter(0)).pack(pady=6)
    
    tk.Label(frame_temp, text="0% = sin filtro (6500K)  ·  100% = máximo (1000K)",
            bg=FRAME_COLOR, fg="#bbbbbb").pack()
    
    # Muestra el estado real al abrir (si coincide con un preset se ilumina)
    initial = read_current_filter_percent()
    if initial is not None:
        percent.set(initial)
        update_label()
        refresh_highlight()


def setup_gui():
    """Setup and create the complete GUI"""
    global COMPACT, MONITOR_COLUMNS
    root = tk.Tk()
    root.title("Control de Monitores")
    root.configure(bg=BG_COLOR)
    
    # Responsive: adapta el diseño al tamaño de la pantalla
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    COMPACT = screen_w < 1280
    MONITOR_COLUMNS = 1 if screen_w < 1000 else 2
    
    # Contenido con scroll vertical (para pantallas pequeñas/altas)
    canvas, content = make_scrollable(root)
    
    # Create GUI components
    create_header(content)
    main_frame = create_main_frame(content)
    
    # Create monitor controls (ordenados en columnas responsive)
    for index, monitor_id in enumerate(MONITORS):
        create_monitor_controls(main_frame, monitor_id, index % MONITOR_COLUMNS)
    
    # Create temperature controls
    create_temperature_controls(content)
    
    # Ajusta la ventana a la pantalla sin cortar contenidos.
    # El canvas no reporta el tamaño real, así que se mide el contenido interno.
    root.update_idletasks()
    req_w = content.winfo_reqwidth() + 24  # margen + scrollbar
    req_h = content.winfo_reqheight() + 8
    root.geometry(f"{min(req_w, screen_w)}x{min(req_h, screen_h)}+0+0")
    
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
