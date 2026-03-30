#!/bin/bash

# Script de desinstalación para Control de Brillo de Pantallas
# Requiere privilegios de sudo para eliminar archivos del sistema

set -e

echo "=== Desinstalando Control de Pantallas ==="

# Verificar si se ejecuta como root
if [ "$EUID" -ne 0 ]; then
    echo "Este script debe ejecutarse con sudo o como root"
    echo "Ejecuta: sudo ./uninstall.sh"
    exit 1
fi

INSTALL_DIR="/opt/brillo-pantallas"
DESKTOP_FILE="/usr/share/applications/brillo-pantallas.desktop"

# Eliminar directorio de instalación
if [ -d "$INSTALL_DIR" ]; then
    echo "Eliminando directorio $INSTALL_DIR..."
    rm -rf "$INSTALL_DIR"
else
    echo "El directorio $INSTALL_DIR no existe"
fi

# Eliminar archivo .desktop
if [ -f "$DESKTOP_FILE" ]; then
    echo "Eliminando entrada del menú de aplicaciones..."
    rm -f "$DESKTOP_FILE"
else
    echo "El archivo $DESKTOP_FILE no existe"
fi

# Actualizar base de datos de aplicaciones
echo "Actualizando base de datos de aplicaciones..."
update-desktop-database /usr/share/applications/ 2>/dev/null || true

echo ""
echo "=== Desinstalación completada ==="
echo "La aplicación ha sido eliminada completamente del sistema"
