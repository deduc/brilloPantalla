"""
Services module for backend business logic
Handles data processing and external integrations
"""

import subprocess
import re
import os
import psutil
from typing import Dict, Any, Callable, List


class BaseService:
    """Base service class for common functionality"""
    
    def __init__(self):
        pass
    
    def process(self, data):
        """Process data"""
        raise NotImplementedError("Subclasses must implement process")


class ConfigService(BaseService):
    """Service for configuration management"""
    
    def __init__(self):
        super().__init__()
        self.config_data = {}
    
    def load_config(self, config_file=None):
        """Load configuration from file or environment"""
        import os
        from dotenv import load_dotenv
        
        load_dotenv(config_file)
        
        self.config_data = {
            'bg_color': os.getenv('BG_COLOR', '#2b2b2b'),
            'fg_color': os.getenv('FG_COLOR', '#ffffff'),
            'frame_bg': os.getenv('FRAME_BG', '#3c3c3c'),
            'window_title': os.getenv('WINDOW_TITLE', 'Interfaz Gráfica'),
            'window_geometry': os.getenv('WINDOW_GEOMETRY', '400x200'),
            'title_font': os.getenv('TITLE_FONT', 'Arial'),
            'title_size': int(os.getenv('TITLE_SIZE', '16')),
            'normal_font': os.getenv('NORMAL_FONT', 'Arial'),
            'normal_size': int(os.getenv('NORMAL_SIZE', '12'))
        }
        
        return self.config_data
    
    def get_config_value(self, key, default=None):
        """Get a specific configuration value"""
        return self.config_data.get(key, default)
    
    def update_config(self, new_config):
        """Update configuration data"""
        self.config_data.update(new_config)
        return self.config_data
    
    def process(self, data):
        """Process configuration requests"""
        action = data.get('action')
        
        if action == 'load':
            return self.load_config(data.get('config_file'))
        elif action == 'get':
            return self.get_config_value(data.get('key'), data.get('default'))
        elif action == 'update':
            return self.update_config(data.get('config_data', {}))
        else:
            return {'error': f'Unknown action: {action}'}


class UIService(BaseService):
    """Service for UI-related operations"""
    
    def __init__(self):
        super().__init__()
        self.ui_state = {}
    
    def update_ui_state(self, key, value):
        """Update UI state"""
        self.ui_state[key] = value
        return self.ui_state
    
    def get_ui_state(self, key=None):
        """Get UI state"""
        if key:
            return self.ui_state.get(key)
        return self.ui_state
    
    def process(self, data):
        """Process UI service requests"""
        action = data.get('action')
        
        if action == 'update_state':
            return self.update_ui_state(data.get('key'), data.get('value'))
        elif action == 'get_state':
            return self.get_ui_state(data.get('key'))
        else:
            return {'error': f'Unknown action: {action}'}


class ReactiveStore(BaseService):
    """Global reactive store for managing application state"""
    
    def __init__(self):
        super().__init__()
        self._state: Dict[str, Any] = {}
        self._subscribers: Dict[str, List[Callable]] = {}
    
    def set_state(self, key: str, value: Any):
        """Set a value in the store and notify subscribers"""
        self._state[key] = value
        self._notify_subscribers(key, value)
        return {'status': 'success', 'key': key, 'value': value}
    
    def get_state(self, key: str, default: Any = None):
        """Get a value from the store"""
        return self._state.get(key, default)
    
    def subscribe(self, key: str, callback: Callable[[Any], None]):
        """Subscribe to changes for a specific key"""
        if key not in self._subscribers:
            self._subscribers[key] = []
        self._subscribers[key].append(callback)
        return {'status': 'success', 'key': key}
    
    def unsubscribe(self, key: str, callback: Callable[[Any], None]):
        """Unsubscribe from changes for a specific key"""
        if key in self._subscribers:
            try:
                self._subscribers[key].remove(callback)
                return {'status': 'success', 'key': key}
            except ValueError:
                return {'status': 'error', 'message': 'Callback not found'}
        return {'status': 'error', 'message': 'Key not found'}
    
    def _notify_subscribers(self, key: str, value: Any):
        """Notify all subscribers of a key change"""
        if key in self._subscribers:
            for callback in self._subscribers[key]:
                try:
                    callback(value)
                except Exception as e:
                    print(f"Error in subscriber callback: {e}")
    
    def get_all_state(self):
        """Get all current state"""
        return {'status': 'success', 'state': self._state.copy()}
    
    def process(self, data):
        """Process reactive store requests"""
        action = data.get('action')
        
        if action == 'set':
            return self.set_state(data.get('key'), data.get('value'))
        elif action == 'get':
            return self.get_state(data.get('key'), data.get('default'))
        elif action == 'subscribe':
            return self.subscribe(data.get('key'), data.get('callback'))
        elif action == 'unsubscribe':
            return self.unsubscribe(data.get('key'), data.get('callback'))
        elif action == 'get_all':
            return self.get_all_state()
        else:
            return {'error': f'Unknown action: {action}'}


class DataService(BaseService):
    """Service for data management"""
    
    def __init__(self):
        super().__init__()
        self.data_store = {}
    
    def store_data(self, key, value):
        """Store data"""
        self.data_store[key] = value
        return True
    
    def retrieve_data(self, key):
        """Retrieve data"""
        return self.data_store.get(key)
    
    def process(self, data):
        """Process data service requests"""
        action = data.get('action')
        
        if action == 'store':
            return self.store_data(data.get('key'), data.get('value'))
        elif action == 'retrieve':
            return self.retrieve_data(data.get('key'))
        else:
            return {'error': f'Unknown action: {action}'}


class DisplayService(BaseService):
    """Service for display-related operations"""
    
    def __init__(self):
        super().__init__()
        self.monitors = []
    
    def list_monitors(self):
        """Get list of connected monitors"""
        try:
            result = subprocess.run(['xrandr', '--listmonitors'], 
                                  capture_output=True, text=True, check=True)
            output = result.stdout
            
            monitors = []
            for line in output.split('\n'):
                if ':' in line and not line.startswith('Monitors:'):
                    # Use Linux commands to extract the actual monitor name
                    # Get the last field (field 6) which contains the actual monitor name
                    echo_process = subprocess.run(['echo', line], capture_output=True, text=True)
                    cut_process = subprocess.run(['cut', '-d', ' ', '-f', '6'], 
                                              input=echo_process.stdout, 
                                              capture_output=True, text=True)
                    
                    monitor_name = cut_process.stdout.strip()
                    if monitor_name:  # Only add non-empty names
                        monitors.append(monitor_name)
            
            self.monitors = monitors
            return {'status': 'success', 'monitors': monitors}
        except subprocess.CalledProcessError as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_brightness(self, monitor):
        """Get current brightness for monitor"""
        try:
            result = subprocess.run(['xrandr', '--verbose'], 
                                  capture_output=True, text=True, check=True)
            output = result.stdout
            
            # Find brightness for specific monitor
            monitor_section = re.search(rf'{re.escape(monitor)}.*?(?=\n\n|\n\S|\Z)', output, re.DOTALL)
            if monitor_section:
                brightness_match = re.search(r'Brightness:\s*([\d.]+)', monitor_section.group())
                if brightness_match:
                    brightness = float(brightness_match.group(1))
                    return {'status': 'success', 'brightness': brightness}
            
            return {'status': 'error', 'message': f'Could not find brightness for {monitor}'}
        except subprocess.CalledProcessError as e:
            return {'status': 'error', 'message': str(e)}
    
    def set_brightness(self, monitor, value):
        """Set brightness for monitor"""
        try:
            subprocess.run(['xrandr', '--output', monitor, '--brightness', str(value)], 
                          check=True)
            return {'status': 'success', 'message': f'Brightness set to {value} for {monitor}'}
        except subprocess.CalledProcessError as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_contrast(self, monitor):
        """Get current contrast (gamma) for monitor"""
        try:
            result = subprocess.run(['xrandr', '--verbose'], 
                                  capture_output=True, text=True, check=True)
            output = result.stdout
            
            # Find gamma for specific monitor
            monitor_section = re.search(rf'{re.escape(monitor)}.*?(?=\n\n|\n\S|\Z)', output, re.DOTALL)
            if monitor_section:
                gamma_match = re.search(r'Gamma:\s*([\d.]+):([\d.]+):([\d.]+)', monitor_section.group())
                if gamma_match:
                    r, g, b = gamma_match.groups()
                    return {'status': 'success', 'gamma': {'r': float(r), 'g': float(g), 'b': float(b)}}
            
            return {'status': 'error', 'message': f'Could not find gamma for {monitor}'}
        except subprocess.CalledProcessError as e:
            return {'status': 'error', 'message': str(e)}
    
    def set_contrast(self, monitor, value):
        """Set contrast (gamma) for monitor"""
        try:
            gamma_value = f"{value}:{value}:{value}"
            subprocess.run(['xrandr', '--output', monitor, '--gamma', gamma_value], 
                          check=True)
            return {'status': 'success', 'message': f'Contrast set to {value} for {monitor}'}
        except subprocess.CalledProcessError as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_blue_light(self, monitor):
        """Get current blue light settings"""
        # Blue light is controlled via gamma, same as contrast
        return self.get_contrast(monitor)
    
    def set_blue_light(self, monitor, mode):
        """Set blue light mode"""
        try:
            if mode == 'night':
                # Reduce blue channel: 1:1:0.7
                gamma_value = "1:1:0.7"
            else:  # normal
                # Normal: 1:1:1
                gamma_value = "1:1:1"
            
            subprocess.run(['xrandr', '--output', monitor, '--gamma', gamma_value], 
                          check=True)
            return {'status': 'success', 'message': f'Blue light set to {mode} for {monitor}'}
        except subprocess.CalledProcessError as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_hardware_brightness(self):
        """Get hardware brightness info"""
        try:
            # Check available backlight devices
            backlight_dir = '/sys/class/backlight/'
            if not os.path.exists(backlight_dir):
                return {'status': 'error', 'message': 'No backlight devices found'}
            
            devices = [d for d in os.listdir(backlight_dir) 
                      if os.path.isdir(os.path.join(backlight_dir, d))]
            
            if not devices:
                return {'status': 'error', 'message': 'No backlight devices found'}
            
            device = devices[0]  # Use first device
            brightness_path = os.path.join(backlight_dir, device, 'brightness')
            max_brightness_path = os.path.join(backlight_dir, device, 'max_brightness')
            
            with open(brightness_path, 'r') as f:
                current = int(f.read().strip())
            
            with open(max_brightness_path, 'r') as f:
                maximum = int(f.read().strip())
            
            return {
                'status': 'success', 
                'device': device,
                'current_brightness': current,
                'max_brightness': maximum,
                'percentage': (current / maximum) * 100
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def set_hardware_brightness(self, value):
        """Set hardware brightness"""
        try:
            backlight_dir = '/sys/class/backlight/'
            devices = [d for d in os.listdir(backlight_dir) 
                      if os.path.isdir(os.path.join(backlight_dir, d))]
            
            if not devices:
                return {'status': 'error', 'message': 'No backlight devices found'}
            
            device = devices[0]
            brightness_path = os.path.join(backlight_dir, device, 'brightness')
            
            # Write brightness value (requires sudo)
            process = subprocess.run(['sudo', 'tee', brightness_path], 
                                   input=str(value), text=True, check=True)
            
            return {'status': 'success', 'message': f'Hardware brightness set to {value}'}
        except subprocess.CalledProcessError as e:
            return {'status': 'error', 'message': str(e)}
    
    def process(self, data):
        """Process display service requests"""
        action = data.get('action')
        
        if action == 'list_monitors':
            return self.list_monitors()
        elif action == 'get_brightness':
            return self.get_brightness(data.get('monitor'))
        elif action == 'set_brightness':
            return self.set_brightness(data.get('monitor'), data.get('value'))
        elif action == 'get_contrast':
            return self.get_contrast(data.get('monitor'))
        elif action == 'set_contrast':
            return self.set_contrast(data.get('monitor'), data.get('value'))
        elif action == 'get_blue_light':
            return self.get_blue_light(data.get('monitor'))
        elif action == 'set_blue_light':
            return self.set_blue_light(data.get('monitor'), data.get('mode'))
        elif action == 'get_hardware_brightness':
            return self.get_hardware_brightness()
        elif action == 'set_hardware_brightness':
            return self.set_hardware_brightness(data.get('value'))
        else:
            return {'error': f'Unknown action: {action}'}


class RedshiftService(BaseService):
    """Service for Redshift operations"""
    
    def __init__(self):
        super().__init__()
        self.is_installed = False
        self._check_installation()
    
    def _check_installation(self):
        """Check if redshift is installed"""
        try:
            subprocess.run(['which', 'redshift'], 
                          capture_output=True, check=True)
            self.is_installed = True
        except subprocess.CalledProcessError:
            self.is_installed = False
    
    def install(self):
        """Install redshift"""
        if self.is_installed:
            return {'status': 'success', 'message': 'Redshift is already installed'}
        
        try:
            subprocess.run(['sudo', 'apt', 'update'], check=True)
            subprocess.run(['sudo', 'apt', 'install', '-y', 'redshift'], check=True)
            self.is_installed = True
            return {'status': 'success', 'message': 'Redshift installed successfully'}
        except subprocess.CalledProcessError as e:
            return {'status': 'error', 'message': f'Installation failed: {str(e)}'}
    
    def set_temperature(self, temperature):
        """Set color temperature"""
        if not self.is_installed:
            return {'status': 'error', 'message': 'Redshift is not installed'}
        
        try:
            subprocess.run(['redshift', '-O', str(temperature)], check=True)
            return {'status': 'success', 'message': f'Temperature set to {temperature}K'}
        except subprocess.CalledProcessError as e:
            return {'status': 'error', 'message': str(e)}
    
    def reset(self):
        """Reset redshift settings"""
        if not self.is_installed:
            return {'status': 'error', 'message': 'Redshift is not installed'}
        
        try:
            subprocess.run(['redshift', '-x'], check=True)
            return {'status': 'success', 'message': 'Redshift settings reset'}
        except subprocess.CalledProcessError as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_status(self):
        """Get current redshift status"""
        if not self.is_installed:
            return {'status': 'error', 'message': 'Redshift is not installed'}
        
        # Check if redshift is running
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'redshift' in proc.info['name']:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    return {
                        'status': 'success', 
                        'running': True,
                        'pid': proc.info['pid'],
                        'command': cmdline
                    }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return {'status': 'success', 'running': False}
    
    def process(self, data):
        """Process redshift service requests"""
        action = data.get('action')
        
        if action == 'install':
            return self.install()
        elif action == 'set_temperature':
            return self.set_temperature(data.get('temperature'))
        elif action == 'reset':
            return self.reset()
        elif action == 'get_status':
            return self.get_status()
        else:
            return {'error': f'Unknown action: {action}'}
