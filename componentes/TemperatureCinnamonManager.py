"""
TemperatureCinnamonManager.py

Componente para controlar la temperatura de color (luz azul) en entornos Cinnamon.

Este componente utiliza exclusivamente 'redshift' para ajustar la temperatura
de las pantallas principales y secundarias, sin dependencias adicionales ni
uso de gsettings, light o herramientas nativas del entorno de escritorio.

Para instalar redshift en CachyOS:
    sudo pacman -S redshift

Ejemplo de uso:
    >>> manager = TemperatureCinnamonManager()
    >>> manager.set_temperature(4000)  # Luz cálida (amarillo)
    >>> manager.set_temperature(5500)  # Luz neutra
    >>> manager.set_temperature(6500)  # Luz fría (azul)

Redshift detecta automáticamente el número de monitores conectados y ajusta
la configuración para cada uno de forma individual, lo que garantiza que
ambas pantallas reciban la temperatura correcta.
"""

import subprocess


class TemperatureCinnamonManager:
    def __init__(self):
        """Inicializa el gestor de temperatura."""
        self.current_temperature = 6500  # Por defecto (luz fría/azul)
        self._redshift_installed = False
        self._check_redshift()

    def _check_redshift(self):
        """Comprueba si redshift está instalado y disponible en el sistema."""
        try:
            subprocess.run(['which', 'redshift'], check=True, capture_output=True, timeout=3)
            self._redshift_installed = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  redshift no está instalado o no es accesible.")
            print("    Ejecuta: sudo pacman -S redshift")
            self._redshift_installed = False

    def is_ready(self) -> bool:
        """Verifica si el componente está listo para funcionar."""
        return self._redshift_installed

    def set_temperature(self, temperature: int):
        """
        Establece la temperatura objetivo para las pantallas.
        
        Args:
            temperature: Temperatura en Kelvin (ej: 4000, 5000, 6500).
                         - < 5000: Luz cálida (amarilla/rojiza)
                         - 5000-5500: Luz neutra
                         - > 6000: Luz fría (azulada)
                         
        Redshift aplicará automáticamente este valor a todas las pantallas
        conectadas (principal y secundarias).

        Returns:
            bool: True si la temperatura se aplicó correctamente, False en caso de error.
        """
        if not self._redshift_installed:
            print("❌ redshift no está instalado. No se puede aplicar la temperatura.")
            return False
        
        try:
            # Validar rango de temperatura (0-15000)
            temperature = max(0, min(15000, int(temperature)))
            
            # Aplicar redshift con la temperatura objetivo (valor absoluto)
            # -P restablece la gama previa: evita que el ajuste se acumule y
            # garantiza que 6500K vuelva al color neutro (reset funciona).
            subprocess.run([
                'redshift',
                '-P', '-O', str(temperature)
            ], check=True, capture_output=True, timeout=15)
            
            self.current_temperature = temperature
            print(f"✅ Temperatura ajustada a {temperature}K para todas las pantallas.")
            return True
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode().strip() if hasattr(e, 'stderr') else "Error desconocido"
            print(f"❌ Error al aplicar temperatura: {error_msg}")
            return False
        except Exception as e:
            print(f"⚠️  Error inesperado al configurar temperatura: {e}")
            return False

    def get_current_temperature(self) -> int:
        """
        Obtiene la temperatura actual configurada.
        
        Returns:
            int: Temperatura en Kelvin (por defecto 6500 si no se ha cambiado).
        """
        if self.current_temperature == 6500 and not self._redshift_installed:
            return 6500
        return self.current_temperature

    def cycle_temperatures(self):
        """
        Cicla entre temperaturas predefinidas (luz fría → neutra → cálida).
        
        Ciclo: 6500K → 5500K → 4000K → 6500K ...
        
        Returns:
            bool: True si el ciclo se ejecutó correctamente.
        """
        temperatures = [6500, 5500, 4000]
        current_index = temperatures.index(self.current_temperature) if self.current_temperature in temperatures else 0
        
        next_index = (current_index + 1) % len(temperatures)
        new_temp = temperatures[next_index]
        
        return self.set_temperature(new_temp)

    def reset_to_default(self):
        """
        Reinicia redshift a los valores por defecto (luz fría).
        
        Returns:
            bool: True si se reinició correctamente, False si hubo error.
        """
        if not self._redshift_installed:
            return False
            
        try:
            subprocess.run(['redshift', '-P', '-O', '6500'], check=True, capture_output=True, timeout=10)
            self.current_temperature = 6500
            print("✅ Configuración restablecida a valores por defecto (6500K).")
            return True
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode().strip() if hasattr(e, 'stderr') else "Error desconocido"
            print(f"❌ Error al reiniciar configuración: {error_msg}")
            return False

    def apply_profile(self, profile_name: str):
        """
        Aplica un perfil de temperatura predefinido.
        
        Args:
            profile_name: Nombre del perfil ('cold', 'neutral', 'warm', 'auto').
                         
        Returns:
            bool: True si se aplicó correctamente, False en caso de error.
        """
        profiles = {
            'cold': 6500,      # Luz azulada (por defecto)
            'neutral': 5500,   # Temperatura neutra
            'warm': 4500,      # Luz cálida
            'cozy': 3800,      # Muy cálida
            'auto': None       # Dejar que redshift detecte la hora (si está configurado)
        }
        
        if profile_name not in profiles:
            print(f"❌ Perfil '{profile_name}' no reconocido.")
            return False
        
        temp = profiles[profile_name]
        if temp is None:
            print("⚠️  Modo 'auto' requiere configuración manual en redshift (ej: -l).")
            self.current_temperature = 6500  # Placeholder
            return True
            
        return self.set_temperature(temp)
