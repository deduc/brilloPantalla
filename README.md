# Control de Pantallas

Aplicación Python/Tkinter para controlar el brillo, contraste y temperatura de color de múltiples monitores en Ubuntu/Linux.

## Características

- Control de brillo y contraste para múltiples monitores (usando DDC/CI)
- Control de temperatura de color (integrado con GNOME Night Light)
- Interfaz gráfica intuitiva con botones de acceso rápido
- Soporte para configuraciones predefinidas (0%, 5%, 10%, 15%, 20%, 25%, 30%)

## Dependencias

- Python 3
- tkinter (usualmente incluido con Python)
- ddcutil (para control de monitor DDC/CI)
- GNOME settings-daemon (para control de temperatura de color)

## Instalación

### 1. Instalar dependencias del sistema

```bash
sudo apt update
sudo apt install python3 python3-tk ddcutil
```

### 2. Configurar permisos para ddcutil

```bash
sudo usermod -a -G i2c $USER
```

**Importante**: Cierra y vuelve a abrir tu sesión después de ejecutar este comando.

### 3. Instalar la aplicación

```bash
# Clonar o descargar este repositorio
cd brilloPantallas

# Ejecutar script de instalación
sudo ./install.sh
```

## Uso

Una vez instalada, puedes acceder a la aplicación de dos formas:

1. **Desde el menú de aplicaciones**: Sistema → Control de Pantallas
2. **Desde terminal**: `python3 /opt/brillo-pantallas/main.py`

## Desinstalación

Para desinstalar completamente la aplicación:

```bash
sudo ./uninstall.sh
```

## Configuración

Puedes personalizar los monitores y valores predeterminados editando las constantes en `main.py`:

```python
MONITORS = [1, 2]  # IDs de tus monitores
STEPS = [0, 5, 10, 15, 20, 25, 30]  # Porcentajes de brillo/contraste
TEMPS = [10000, 8716, 7430, 6144, 4858, 3572, 2286, 1000]  # Temperaturas de color
```

## Troubleshooting

### ddcutil no detecta monitores

1. Verifica que tu monitor soporte DDC/CI
2. Asegúrate de estar usando un cable de video compatible (DisplayPort o HDMI)
3. Ejecuta `ddcutil detect` para verificar detección

### Permisos insuficientes

Si recibes errores de permisos, verifica que tu usuario esté en el grupo i2c:

```bash
groups $USER | grep i2c
```

Si no aparece i2c, ejecuta nuevamente:
```bash
sudo usermod -a -G i2c $USER
```

Y reinicia tu sesión.

## Licencia

Este software es libre y de código abierto.
