"""
Contrast control component with range sliders for each monitor
"""

import tkinter as tk
from tkinter import ttk


class ContrastControl:
    """Component for controlling contrast of multiple monitors"""
    
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.monitors = []
        self.sliders = {}
        self.labels = {}
        
    def create_ui(self):
        """Create the contrast control UI and return the frame"""
        # Main frame for contrast controls
        self.frame = ttk.Frame(self.parent)
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(self.frame, text="Control de Contraste:", style="Normal.TLabel")
        title_label.grid(row=0, column=0, pady=5, sticky=tk.W)
        
        # Controls frame - horizontal layout for monitors
        self.controls_frame = ttk.Frame(self.frame)
        self.controls_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Load and create controls for each monitor
        self.refresh_controls()
        
        return self.frame
    
    def refresh_controls(self):
        """Refresh contrast controls for all monitors"""
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
        """Create contrast control for a single monitor with styling like monitor_list"""
        # Simple container with gray border like monitor_list
        monitor_container = ttk.Frame(self.controls_frame, relief="solid", borderwidth=1)
        monitor_container.grid(row=0, column=index, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N))
        
        # Monitor name
        name_label = ttk.Label(monitor_container, text=f"{monitor_name}", 
                              style="Normal.TLabel", foreground="light gray")
        name_label.grid(row=0, column=0, padx=10, pady=(5, 2), sticky=tk.W)
        
        # Get current contrast
        contrast_result = self.controller.get_contrast(monitor_name)
        if contrast_result['status'] == 'success':
            gamma = contrast_result['gamma']
            # Use the red channel as representative (all should be same for contrast)
            current_contrast = gamma['r']
            # Convert to percentage (0-100) where 1.0 = 100%
            contrast_percent = int(current_contrast * 100)
        else:
            contrast_percent = 100  # Default to 100% (1.0) if error
        
        # Current contrast level
        level_label = ttk.Label(monitor_container, text=f"Contraste: {contrast_percent}%", 
                               style="Normal.TLabel", foreground="light gray")
        level_label.grid(row=1, column=0, padx=10, pady=2, sticky=tk.W)
        self.labels[monitor_name] = level_label
        
        # Contrast slider (longer)
        slider = ttk.Scale(monitor_container, 
                          from_=10, to=200,  # 0.1 to 2.0 range
                          orient=tk.HORIZONTAL,
                          value=contrast_percent,
                          command=lambda val, monitor=monitor_name: self._on_contrast_change(monitor, val))
        slider.grid(row=2, column=0, padx=10, pady=(2, 5), sticky=(tk.W, tk.E))
        self.sliders[monitor_name] = slider
        
        # Configure slider to be longer
        slider.configure(length=300)
    
    def _on_contrast_change(self, monitor_name, value):
        """Handle contrast slider change"""
        try:
            # Convert percentage to gamma range (0.1 to 2.0)
            contrast_value = float(value) / 100.0
            
            # Update label with new format
            if monitor_name in self.labels:
                self.labels[monitor_name].config(text=f"Contraste: {int(float(value))}%")
            
            # Set contrast via controller
            result = self.controller.set_contrast(monitor_name, contrast_value)
            
            if result['status'] == 'error':
                print(f"Error setting contrast for {monitor_name}: {result['message']}")
            else:
                # Store updated contrast in reactive store
                contrast_key = f"{monitor_name}_contrast"
                self.controller.set_state(contrast_key, contrast_value)
                
        except ValueError as e:
            print(f"Invalid contrast value: {e}")
    
    def get_stored_contrast(self, monitor_name):
        """Get stored contrast value for monitor"""
        contrast_key = f"{monitor_name}_contrast"
        return self.controller.get_state(contrast_key, None)
    
    def __call__(self, row=3, column=0, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S)):
        """Make the class callable to create, grid, and return the UI"""
        frame = self.create_ui()
        frame.grid(row=row, column=column, pady=pady, sticky=sticky)
        return frame
