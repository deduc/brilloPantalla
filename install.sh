#!/bin/bash

# Script de instalación para Control de Brillo de Pantallas
# Requiere privilegios de sudo para instalar en /opt

set -e

echo "=== Instalando Control de Pantallas ==="

# Verificar si se ejecuta como root
if [ "$EUID" -ne 0 ]; then
    echo "Este script debe ejecutarse con sudo o como root"
    echo "Ejecuta: sudo ./install.sh"
    exit 1
fi

# Verificar dependencias
echo "Verificando dependencias..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 no está instalado"
    exit 1
fi

if ! python3 -c "import tkinter" 2>/dev/null; then
    echo "ERROR: tkinter no está disponible. Instala python3-tk:"
    echo "sudo apt install python3-tk"
    exit 1
fi

if ! command -v ddcutil &> /dev/null; then
    echo "ADVERTENCIA: ddcutil no está instalado. Es necesario para controlar monitores:"
    echo "sudo apt install ddcutil"
    echo "Después instala: sudo usermod -a -G i2c \$USER"
    echo "Y reinicia tu sesión"
fi

# Crear directorio de instalación
INSTALL_DIR="/opt/brillo-pantallas"
echo "Creando directorio $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"

# Copiar archivos
echo "Copiando archivos..."
cp main.py "$INSTALL_DIR/"
cp brillo-pantallas.desktop "$INSTALL_DIR/"

# Copiar icono si existe
if [ -f "icon.png" ]; then
    cp icon.png "$INSTALL_DIR/"
else
    echo "Creando icono simple..."
    # Crear un icono simple usando ImageMagick si está disponible
    if command -v convert &> /dev/null; then
        convert -size 64x64 xc:#5a5a5a -fill white -gravity center -pointsize 12 -annotate +0+0 "BRILLO" "$INSTALL_DIR/icon.png" 2>/dev/null || echo "No se pudo crear el icono automáticamente"
    fi
fi

# Establecer permisos
echo "Estableciendo permisos..."
chmod 755 "$INSTALL_DIR"
chmod 644 "$INSTALL_DIR/main.py"
chmod 644 "$INSTALL_DIR/brillo-pantallas.desktop"
if [ -f "$INSTALL_DIR/icon.png" ]; then
    chmod 644 "$INSTALL_DIR/icon.png"
fi

# Instalar archivo .desktop en el sistema
echo "Instalando entrada en el menú de aplicaciones..."
cp "$INSTALL_DIR/brillo-pantallas.desktop" /usr/share/applications/
chmod 644 /usr/share/applications/brillo-pantallas.desktop

# Actualizar base de datos de aplicaciones
update-desktop-database /usr/share/applications/ 2>/dev/null || true

echo ""
echo "=== Instalación completada ==="
echo "La aplicación ahora está disponible en el menú de aplicaciones:"
echo "- Control de Pantalla y Brillo"
echo ""
echo "O puedes ejecutarla directamente con:"
echo "python3 /opt/brillo-pantallas/main.py"
echo ""
echo "NOTA: Si ddcutil no estaba instalado, instálalo y añade tu usuario al grupo i2c:"
echo "sudo apt install ddcutil"
echo "sudo usermod -a -G i2c \$USER"
echo "Luego cierra y vuelve a abrir tu sesión"
