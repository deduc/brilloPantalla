import subprocess
import threading
import sys
from pathlib import Path


def set_temperature(value):
    """Set color temperature using GNOME settings in background thread"""
    def worker():
        try:
            subprocess.run([
                'gsettings', 'set',
                'org.gnome.settings-daemon.plugins.color',
                'night-light-temperature',
                str(value)
            ])
        except Exception as e:
            print(f"Error setting temperature: {e}")
    
    threading.Thread(target=worker, daemon=True).start()


def get_current_temperature():
    """Get current color temperature setting"""
    try:
        output = subprocess.check_output(
            ['gsettings', 'get', 'org.gnome.settings-daemon.plugins.color', 'night-light-temperature']
        )
        if 'night-light-temperature' in str(output):
            # Parse the output to extract the value
            match = None
            try:
                import re
                match = re.search(r'(\\d+)', str(output))
                if match:
                    return int(match.group(1))
            except ImportError:
                pass
        return None
    except Exception as e:
        print(f"Error getting temperature: {e}")
        return None


def get_available_temperatures():
    """Get available color temperature range"""
    try:
        import re
        # GNOME typically accepts temperatures in the range 1000-50000K
        return (1000, 50000)
    except Exception as e:
        print(f"Error getting available temperatures: {e}")
        return (1000, 50000)


class TemperatureManager:
    """Manages temperature settings for GNOME/Cinnamon desktop environments"""
    
    def __init__(self):
        self.supported_desktops = ['gnome', 'cinnamon']
        self.temperature_range = (1000, 50000)
    
    def is_supported(self):
        """Check if the current desktop environment is supported (always True)"""
        return True
    
    def set_temperature_sync(self, value):
        """Set temperature synchronously"""
        if not self.is_supported():
            raise RuntimeError("Desktop environment is not GNOME or Cinnamon")
        
        try:
            subprocess.run([
                'gsettings', 'set',
                'org.gnome.settings-daemon.plugins.color',
                'night-light-temperature',
                str(value)
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to set temperature: {e}")
            return False
    
    def set_temperature_async(self, value):
        """Set temperature asynchronously in a background thread"""
        def worker():
            try:
                self.set_temperature_sync(value)
            except Exception as e:
                print(f"Error setting temperature: {e}")
        
        threading.Thread(target=worker, daemon=True).start()
    
    def get_current_temperature(self):
        """Get current temperature setting"""
        return get_current_temperature()
    
    def validate_temperature(self, value):
        """Validate if a temperature value is within acceptable range"""
        if not isinstance(value, (int, float)):
            return False
        min_temp, max_temp = self.temperature_range
        return min_temp <= value <= max_temp
    
    def get_temperature_info(self):
        """Get information about current temperature setting"""
        current = self.get_current_temperature()
        min_temp, max_temp = self.temperature_range
        is_dark = current < 3000 if current else None
        
        return {
            'current': current,
            'min': min_temp,
            'max': max_temp,
            'is_dark_mode': is_dark,
            'unit': 'K'
        }
