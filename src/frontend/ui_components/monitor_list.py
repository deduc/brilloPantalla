"""
Monitor list component for displaying connected monitors
"""

import tkinter as tk
from tkinter import ttk


class MonitorList:
    """Component for displaying and managing monitor list"""
    
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.monitors = []
        self.monitor_widgets = []
        
    def create_ui(self):
        """Create the monitor list UI and return the frame"""
        # Main frame for monitor list
        self.frame = ttk.Frame(self.parent)
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(self.frame, text="Monitores del sistema:", style="Normal.TLabel")
        title_label.grid(row=0, column=0, pady=5, sticky=tk.W)
        
        # Monitor list frame - single row for horizontal layout
        self.list_frame = ttk.Frame(self.frame)
        self.list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure row to expand
        self.list_frame.rowconfigure(0, weight=1)
        
        # Load and display monitors
        self.refresh_monitors()
        
        return self.frame
    
    def refresh_monitors(self):
        """Refresh the monitor list"""
        # Clear existing widgets
        for widget in self.monitor_widgets:
            widget.destroy()
        self.monitor_widgets.clear()
        
        # Get monitors from backend
        result = self.controller.list_monitors()
        
        if result['status'] == 'success':
            self.monitors = result['monitors']
            
            # Store monitor names in reactive store
            self.controller.set_state('monitors', self.monitors)
            
            # Display each monitor with raw output and formatted info
            for i, monitor in enumerate(self.monitors):
                self._create_monitor_widget(monitor, i)
        else:
            # Show error message
            error_label = ttk.Label(self.list_frame, text=f"Error: {result['message']}", 
                                  style="Normal.TLabel")
            error_label.grid(row=0, column=0, columnspan=2, pady=5)
            self.monitor_widgets.append(error_label)
    
    def _create_monitor_widget(self, monitor_name, index):
        """Create widget for a single monitor with horizontal layout"""
        # Simple dark gray container
        monitor_container = ttk.Frame(self.list_frame, relief="solid", borderwidth=1)
        monitor_container.grid(row=0, column=index, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N))
        self.monitor_widgets.append(monitor_container)
        
        # Monitor name
        name_label = ttk.Label(monitor_container, text=f"{monitor_name}", 
                              style="Normal.TLabel", foreground="light gray")
        name_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        
        # Brightness
        brightness_result = self.controller.get_brightness(monitor_name)
        if brightness_result['status'] == 'success':
            brightness_text = f"Brillo: {brightness_result['brightness']:.2f}"
        else:
            brightness_text = "Brillo: Error"
        
        brightness_label = ttk.Label(monitor_container, text=brightness_text, 
                                   style="Normal.TLabel", foreground="light gray")
        brightness_label.grid(row=1, column=0, padx=10, pady=2, sticky=tk.W)
        
        # Contrast
        contrast_result = self.controller.get_contrast(monitor_name)
        if contrast_result['status'] == 'success':
            gamma = contrast_result['gamma']
            contrast_text = f"Contraste: R:{gamma['r']:.2f} G:{gamma['g']:.2f} B:{gamma['b']:.2f}"
        else:
            contrast_text = "Contraste: Error"
        
        contrast_label = ttk.Label(monitor_container, text=contrast_text, 
                                 style="Normal.TLabel", foreground="light gray")
        contrast_label.grid(row=2, column=0, padx=10, pady=2, sticky=tk.W)
    
    def _get_brightness(self, monitor_name):
        """Get current brightness for monitor"""
        result = self.controller.get_brightness(monitor_name)
        if result['status'] == 'success':
            brightness = result['brightness']
            print(f"Brightness for {monitor_name}: {brightness}")
        else:
            print(f"Error getting brightness: {result['message']}")
    
    def get_stored_monitors(self):
        """Get monitor names from reactive store"""
        return self.controller.get_state('monitors', [])
    
    def on_monitors_changed(self, new_monitors):
        """Callback for when monitor list changes in store"""
        print(f"Monitors updated in store: {new_monitors}")
        self.refresh_monitors()
    
    def subscribe_to_monitor_changes(self):
        """Subscribe to monitor list changes"""
        self.controller.subscribe_to_state('monitors', self.on_monitors_changed)
    
    def __call__(self, row=1, column=0, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S)):
        """Make the class callable to create, grid, and return the UI"""
        frame = self.create_ui()
        frame.grid(row=row, column=column, pady=pady, sticky=sticky)
        
        # Subscribe to reactive store changes
        self.subscribe_to_monitor_changes()
        
        return frame
