"""
Controllers module for backend logic
Handles user interactions and application flow
"""

import subprocess
import re
import os
import psutil
from .services import BaseService


class BaseController:
    """Base controller class for common functionality"""
    
    def __init__(self):
        pass
    
    def handle_request(self, request_data):
        """Handle incoming requests"""
        raise NotImplementedError("Subclasses must implement handle_request")


class AppController(BaseController):
    """Main application controller"""
    
    def __init__(self):
        super().__init__()
        self.services = {}
    
    def register_service(self, service_name, service_instance):
        """Register a service instance"""
        self.services[service_name] = service_instance
    
    def get_service(self, service_name):
        """Get a registered service"""
        return self.services.get(service_name)
    
    def handle_request(self, request_data):
        """Handle application requests"""
        request_type = request_data.get('type')
        
        if request_type == 'get_config':
            return self.handle_get_config()
        elif request_type == 'update_ui':
            return self.handle_update_ui(request_data)
        else:
            return {'status': 'error', 'message': f'Unknown request type: {request_type}'}
    
    def handle_get_config(self):
        """Handle configuration requests"""
        return {'status': 'success', 'data': 'config_data'}
    
    def handle_update_ui(self, request_data):
        """Handle UI update requests"""
        return {'status': 'success', 'message': 'UI updated'}
    
    # Display methods
    def list_monitors(self):
        """Get list of connected monitors"""
        display_service = self.get_service('display')
        return display_service.list_monitors()
    
    def get_brightness(self, monitor):
        """Get current brightness for monitor"""
        display_service = self.get_service('display')
        return display_service.get_brightness(monitor)
    
    def set_brightness(self, monitor, value):
        """Set brightness for monitor"""
        display_service = self.get_service('display')
        return display_service.set_brightness(monitor, value)
    
    def get_contrast(self, monitor):
        """Get current contrast for monitor"""
        display_service = self.get_service('display')
        return display_service.get_contrast(monitor)
    
    def set_contrast(self, monitor, value):
        """Set contrast for monitor"""
        display_service = self.get_service('display')
        return display_service.set_contrast(monitor, value)
    
    def get_blue_light(self, monitor):
        """Get current blue light settings"""
        display_service = self.get_service('display')
        return display_service.get_blue_light(monitor)
    
    def set_blue_light(self, monitor, mode):
        """Set blue light mode (normal/night)"""
        display_service = self.get_service('display')
        return display_service.set_blue_light(monitor, mode)
    
    def get_hardware_brightness(self):
        """Get hardware brightness info"""
        display_service = self.get_service('display')
        return display_service.get_hardware_brightness()
    
    def set_hardware_brightness(self, value):
        """Set hardware brightness"""
        display_service = self.get_service('display')
        return display_service.set_hardware_brightness(value)
    
    # Redshift methods
    def install_redshift(self):
        """Install redshift"""
        redshift_service = self.get_service('redshift')
        return redshift_service.install()
    
    def set_redshift_temperature(self, temperature):
        """Set color temperature"""
        redshift_service = self.get_service('redshift')
        return redshift_service.set_temperature(temperature)
    
    def reset_redshift(self):
        """Reset redshift settings"""
        redshift_service = self.get_service('redshift')
        return redshift_service.reset()
    
    # Reactive store methods
    def set_state(self, key, value):
        """Set a value in the reactive store"""
        store = self.get_service('store')
        return store.set_state(key, value)
    
    def get_state(self, key, default=None):
        """Get a value from the reactive store"""
        store = self.get_service('store')
        return store.get_state(key, default)
    
    def subscribe_to_state(self, key, callback):
        """Subscribe to changes in the reactive store"""
        store = self.get_service('store')
        return store.subscribe(key, callback)
    
    def get_redshift_status(self):
        """Get current redshift status"""
        redshift_service = self.get_service('redshift')
        return redshift_service.get_status()
