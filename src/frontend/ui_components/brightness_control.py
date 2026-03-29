"""
Brightness control component with range sliders for each monitor
"""

import tkinter as tk
from tkinter import ttk


class BrightnessControl:
    """Component for controlling brightness of multiple monitors"""
    
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.monitors = []
        self.sliders = {}
        self.labels = {}
        
    def create_ui(self):
        """Create the brightness control UI and return the frame"""
        # Main frame for brightness controls
        self.frame = ttk.Frame(self.parent)
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(self.frame, text="Control de Brillo:", style="Normal.TLabel")
        title_label.grid(row=0, column=0, pady=5, sticky=tk.W)
        
        # Controls frame - horizontal layout for monitors
        self.controls_frame = ttk.Frame(self.frame)
        self.controls_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Load and create controls for each monitor
        self.refresh_controls()
        
        return self.frame
    
    def refresh_controls(self):
        """Refresh brightness controls for all monitors"""
        # Clear existing widgets
        for widget in self.controls_frame.winfo_children():
            widget.destroy()
        self.sliders.clear()
        self.labels.clear()
        
        # Get monitors from reactive store
        stored_monitors = self.controller.get_state('monitors', [])
        
        if not stored_monitors:
            # Fallback: get monitors directly
            result = self.controller.list_monitors()
            if result['status'] == 'success':
                self.monitors = result['monitors']
            else:
                error_label = ttk.Label(self.controls_frame, 
                                       text=f"Error: {result['message']}", 
                                       style="Normal.TLabel")
                error_label.grid(row=0, column=0, pady=5)
                return
        else:
            self.monitors = stored_monitors
        
        # Create control for each monitor
        for i, monitor in enumerate(self.monitors):
            self._create_monitor_control(monitor, i)
    
    def _create_monitor_control(self, monitor_name, index):
        """Create brightness control for a single monitor with styling like monitor_list"""
        # Simple container with gray border like monitor_list
        monitor_container = ttk.Frame(self.controls_frame, relief="solid", borderwidth=1)
        monitor_container.grid(row=0, column=index, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N))
        
        # Monitor name
        name_label = ttk.Label(monitor_container, text=f"{monitor_name}", 
                              style="Normal.TLabel", foreground="light gray")
        name_label.grid(row=0, column=0, padx=10, pady=(5, 2), sticky=tk.W)
        
        # Get current brightness
        brightness_result = self.controller.get_brightness(monitor_name)
        if brightness_result['status'] == 'success':
            current_brightness = brightness_result['brightness']
            # Convert to percentage (0-100)
            brightness_percent = int(current_brightness * 100)
        else:
            brightness_percent = 50  # Default to 50% if error
        
        # Current brightness level
        level_label = ttk.Label(monitor_container, text=f"Brillo: {brightness_percent}%", 
                               style="Normal.TLabel", foreground="light gray")
        level_label.grid(row=1, column=0, padx=10, pady=2, sticky=tk.W)
        self.labels[monitor_name] = level_label
        
        # Brightness slider (longer)
        slider = ttk.Scale(monitor_container, 
                          from_=0, to=200,  # 0-200% range
                          orient=tk.HORIZONTAL,
                          value=brightness_percent,
                          command=lambda val, monitor=monitor_name: self._on_brightness_change(monitor, val))
        slider.grid(row=2, column=0, padx=10, pady=(2, 5), sticky=(tk.W, tk.E))
        self.sliders[monitor_name] = slider
        
        # Configure slider to be longer
        slider.configure(length=300)
    
    def _on_brightness_change(self, monitor_name, value):
        """Handle brightness slider change"""
        try:
            # Convert percentage to 0-2 range (200% = 2.0)
            brightness_value = float(value) / 100.0
            
            # Update label with new format
            if monitor_name in self.labels:
                self.labels[monitor_name].config(text=f"Brillo: {int(float(value))}%")
            
            # Set brightness via controller
            result = self.controller.set_brightness(monitor_name, brightness_value)
            
            if result['status'] == 'error':
                print(f"Error setting brightness for {monitor_name}: {result['message']}")
            else:
                # Store updated brightness in reactive store
                brightness_key = f"{monitor_name}_brightness"
                self.controller.set_state(brightness_key, brightness_value)
                
        except ValueError as e:
            print(f"Invalid brightness value: {e}")
    
    def get_stored_brightness(self, monitor_name):
        """Get stored brightness value for monitor"""
        brightness_key = f"{monitor_name}_brightness"
        return self.controller.get_state(brightness_key, None)
    
    def __call__(self, row=2, column=0, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S)):
        """Make the class callable to create, grid, and return the UI"""
        frame = self.create_ui()
        frame.grid(row=row, column=column, pady=pady, sticky=sticky)
        return frame
