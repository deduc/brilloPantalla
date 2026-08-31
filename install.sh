#!/bin/bash

# Script de instalación para Control de Brillo de Pantallas
# Instala dependencias según el entorno de escritorio (GNOME vs Cinnamon)
# y según la distro (pacman/Arch-CachyOS, apt/Debian, dnf/Fedora).
# Requiere ejecutarse como root: sudo ./install.sh

set -e

echo "=== Instalando Control de Pantallas ==="

# Verificar root
if [ "$EUID" -ne 0 ]; then
    echo "Este script debe ejecutarse con sudo o como root"
    echo "Ejecuta: sudo ./install.sh"
    exit 1
fi

TARGET_USER="${SUDO_USER:-$(logname 2>/dev/null || echo root)}"

# --- Detectar gestor de paquetes ---
if command -v pacman &>/dev/null; then
    PKG="pacman"
elif command -v apt-get &>/dev/null; then
    PKG="apt"
elif command -v dnf &>/dev/null; then
    PKG="dnf"
else
    echo "ERROR: gestor de paquetes no soportado (se espera pacman, apt o dnf)."
    exit 1
fi

# --- Detectar entorno de escritorio (Cinnamon, GNOME u otro) ---
DESKTOP_ENV="$(echo "${XDG_CURRENT_DESKTOP:-$DESKTOP_SESSION}" | tr '[:upper:]' '[:lower:]')"
case "$DESKTOP_ENV" in
    *cinnamon*) DE="cinnamon" ;;
    *gnome*)    DE="gnome" ;;
    *)          DE="desconocido" ;;
esac

echo ""
echo "Gestor de paquetes: $PKG"
echo "Entorno de escritorio: ${DE:-no detectado}"
echo ""

# --- Helper de instalación ---
APTS_UPDATED=0
install_pkgs() {
    case "$PKG" in
        pacman)
            pacman -S --needed --noconfirm "$@"
            ;;
        apt)
            if [ "$APTS_UPDATED" -eq 0 ]; then
                apt-get update -y
                APTS_UPDATED=1
            fi
            apt-get install -y "$@"
            ;;
        dnf)
            dnf install -y "$@"
            ;;
    esac
}

# --- Dependencias comunes (python + tkinter + ddcutil) ---
echo "Instalando dependencias comunes (python, tkinter, ddcutil)..."
case "$PKG" in
    pacman) install_pkgs python tk ddcutil i2c-tools ;;
    apt)    install_pkgs python3 python3-tk ddcutil ;;
    dnf)    install_pkgs python3 python3-tkinter ddcutil ;;
esac

# --- Dependencias según escritorio ---
case "$DE" in
    cinnamon)
        echo "Cinnamon detectado: instalando redshift (control de temperatura de color)..."
        install_pkgs redshift
        ;;
    gnome)
        echo "GNOME detectado: no necesita paquete extra (usa night-light de GNOME)."
        if command -v gsettings &>/dev/null && [ -n "$TARGET_USER" ]; then
            echo "Activando night-light para el usuario $TARGET_USER..."
            sudo -u "$TARGET_USER" gsettings set \
                org.gnome.settings-daemon.plugins.color night-light-enabled true || true
        fi
        ;;
    *)
        echo "Escritorio no reconocido: instalando redshift como opción segura."
        install_pkgs redshift
        ;;
esac

# --- Grupo i2c (necesario para ddcutil) ---
if [ -n "$TARGET_USER" ]; then
    if getent group i2c >/dev/null 2>&1; then
        if ! id -G -n "$TARGET_USER" | grep -qw i2c; then
            echo "Añadiendo $TARGET_USER al grupo i2c..."
            gpasswd -a "$TARGET_USER" i2c
            echo "⚠️  Reinicia tu sesión para que ddcutil funcione."
        fi
    else
        echo "⚠️  El grupo 'i2c' no existe en este sistema."
        echo "   En Arch/CachyOS:  sudo modprobe i2c-dev"
        echo "                     sudo groupadd i2c && sudo gpasswd -a $TARGET_USER i2c"
        echo "   En Debian/Ubuntu: sudo addgroup i2c && sudo adduser $TARGET_USER i2c"
    fi
fi

# --- Copia de archivos a /opt ---
echo ""
INSTALL_DIR="/opt/brillo-pantallas"
echo "Creando directorio $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"

echo "Copiando archivos..."
cp main.py "$INSTALL_DIR/"
cp -r componentes "$INSTALL_DIR/"
cp brillo-pantallas.desktop "$INSTALL_DIR/"

# Copiar icono si existe
if [ -f "icon.png" ]; then
    cp icon.png "$INSTALL_DIR/"
else
    echo "Creando icono simple..."
    if command -v convert &>/dev/null; then
        convert -size 64x64 xc:#5a5a5a -fill white -gravity center -pointsize 12 \
            -annotate +0+0 "BRILLO" "$INSTALL_DIR/icon.png" 2>/dev/null || true
    fi
fi

# Establecer permisos
echo "Estableciendo permisos..."
chmod 755 "$INSTALL_DIR"
chmod 644 "$INSTALL_DIR/main.py"
chmod 644 "$INSTALL_DIR/brillo-pantallas.desktop"
chmod 644 "$INSTALL_DIR/componentes/"*.py 2>/dev/null || true
if [ -f "$INSTALL_DIR/icon.png" ]; then
    chmod 644 "$INSTALL_DIR/icon.png"
fi

# Instalar entrada en el menú
echo "Instalando entrada en el menú de aplicaciones..."
cp "$INSTALL_DIR/brillo-pantallas.desktop" /usr/share/applications/
chmod 644 /usr/share/applications/brillo-pantallas.desktop
update-desktop-database /usr/share/applications/ 2>/dev/null || true

echo ""
echo "=== Instalación completada ==="
echo "La aplicación está disponible en el menú de aplicaciones (Control de Pantallas)."
echo "O ejecutala directamente con: python3 /opt/brillo-pantallas/main.py"
echo ""
echo "NOTA: si ddcutil no detecta tus monitores, comprueba el grupo i2c"
echo "y reinicia tu sesión."