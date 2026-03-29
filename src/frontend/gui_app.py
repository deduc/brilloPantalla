import tkinter as tk
from tkinter import ttk
import os
from dotenv import load_dotenv
from src.backend.controllers import AppController
from src.backend.services import ConfigService, UIService, DataService, DisplayService, RedshiftService, ReactiveStore
from src.frontend.ui_components.monitor_list import MonitorList
from src.frontend.ui_components.brightness_control import BrightnessControl
from src.frontend.ui_components.contrast_control import ContrastControl


class MainWindowApp:
    def __init__(self):
        load_dotenv()
        self.controller = AppController()
        self._setup_services()
    
    def _setup_services(self):
        """Setup backend services"""
        config_service = ConfigService()
        ui_service = UIService()
        data_service = DataService()
        display_service = DisplayService()
        redshift_service = RedshiftService()
        reactive_store = ReactiveStore()
        
        self.controller.register_service('config', config_service)
        self.controller.register_service('ui', ui_service)
        self.controller.register_service('data', data_service)
        self.controller.register_service('display', display_service)
        self.controller.register_service('redshift', redshift_service)
        self.controller.register_service('store', reactive_store)
        
        # Load initial configuration
        config_service.load_config()
    
    def configure_dark_mode_styles(self, style, root):
        """Configure dark mode styles for the application"""
        # Get configuration from backend service
        config_service = self.controller.get_service('config')
        bg_color = config_service.get_config_value('BG_COLOR', '#2b2b2b')
        fg_color = config_service.get_config_value('FG_COLOR', '#ffffff')
        frame_bg = config_service.get_config_value('FRAME_BG', '#3c3c3c')
        
        # Apply dark mode theme
        root.configure(bg=bg_color)
        
        # Configure style for dark mode
        style.theme_use('clam')
        
        # Get font configuration
        title_font = config_service.get_config_value('TITLE_FONT', 'Arial')
        title_size = config_service.get_config_value('TITLE_SIZE', 16)
        normal_font = config_service.get_config_value('NORMAL_FONT', 'Arial')
        normal_size = config_service.get_config_value('NORMAL_SIZE', 12)
        
        # Configure dark mode styles
        style.configure("Title.TLabel", 
                        font=(title_font, title_size, "bold"),
                        foreground=fg_color,
                        background=frame_bg)
        style.configure("Normal.TLabel", 
                        font=(normal_font, normal_size),
                        foreground=fg_color,
                        background=frame_bg)
        style.configure("TFrame", 
                        background=frame_bg)

    def insert_ui_elements(self, main_frame):
        """Insert UI elements into the main frame"""
        # First row: Title
        title_label = ttk.Label(main_frame, text="BRILLO, CONTRASTE Y LUZ AZUL", style="Title.TLabel")
        title_label.grid(row=0, column=0, pady=10, sticky=(tk.W, tk.E))
        
        # Second row: Monitor list component
        MonitorList(main_frame, self.controller)()
        
        # Third row: Brightness control component
        BrightnessControl(main_frame, self.controller)()
        
        # Fourth row: Contrast control component
        ContrastControl(main_frame, self.controller)()

        # Fifth row: Empty row for spacing

    def window_app(self):
        """Create and run the main window application"""
        # Get configuration from backend
        config_service = self.controller.get_service('config')
        
        # Create the main window
        root = tk.Tk()
        root.title(config_service.get_config_value('WINDOW_TITLE', 'Interfaz Gráfica'))
        root.geometry(config_service.get_config_value('WINDOW_GEOMETRY', '1000x600'))
        
        # Configure dark mode styles
        style = ttk.Style()
        self.configure_dark_mode_styles(style, root)
        
        # Create a frame to hold the content
        main_frame = ttk.Frame(root, padding="20", style="TFrame")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Insert UI elements
        self.insert_ui_elements(main_frame)
        
        # Configure grid weights for proper resizing
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Store UI state in backend service
        ui_service = self.controller.get_service('ui')
        ui_service.update_ui_state('main_window', root)
        ui_service.update_ui_state('main_frame', main_frame)
        
        # Start the GUI event loop
        root.mainloop()

    def run(self):
        """Run the application"""
        self.window_app()
