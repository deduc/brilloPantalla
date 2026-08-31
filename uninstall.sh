#!/bin/bash

# Script de desinstalación para Control de Brillo de Pantallas
# Elimina la aplicación y (opcionalmente) las dependencias que install.sh añadió.
# Requiere privilegios de sudo: sudo ./uninstall.sh

set -e

echo "=== Desinstalando Control de Pantallas ==="

# Verificar root
if [ "$EUID" -ne 0 ]; then
    echo "Este script debe ejecutarse con sudo o como root"
    echo "Ejecuta: sudo ./uninstall.sh"
    exit 1
fi

# --- Detectar gestor de paquetes (igual que install.sh) ---
if command -v pacman &>/dev/null; then
    PKG="pacman"
elif command -v apt-get &>/dev/null; then
    PKG="apt"
elif command -v dnf &>/dev/null; then
    PKG="dnf"
else
    echo "ADVERTENCIA: gestor de paquetes no soportado; solo se eliminarán los archivos de la app."
    PKG="none"
fi

# --- Detectar entorno de escritorio ---
DESKTOP_ENV="$(echo "${XDG_CURRENT_DESKTOP:-$DESKTOP_SESSION}" | tr '[:upper:]' '[:lower:]')"
case "$DESKTOP_ENV" in
    *cinnamon*) DE="cinnamon" ;;
    *gnome*)    DE="gnome" ;;
    *)          DE="desconocido" ;;
esac

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
update-desktop-database /usr/share/applications/ 2>/dev/null || true

# --- Eliminación opcional de dependencias (solo si se instalaron antes) ---
remove_pkgs() {
    case "$PKG" in
        pacman) pacman -Rns --noconfirm "$@" 2>/dev/null || echo "  (alguno ya no estaba instalado)" ;;
        apt)    apt-get remove -y "$@" 2>/dev/null || true ;;
        dnf)    dnf remove -y "$@" 2>/dev/null || true ;;
    esac
}

ask_remove() {
    # $1 = nombre visible, resto = paquetes
    local label="$1"; shift
    if ! command -v "$1" &>/dev/null; then
        return 0  # no está instalado, no preguntar
    fi
    read -r -p "¿Eliminar $label? [s/N] " reply
    if [[ "$reply" =~ ^[Ss]$ ]]; then
        remove_pkgs "$@"
    fi
}

echo ""
echo "--- Dependencias instaladas por install.sh (opcional) ---"

if command -v redshift &>/dev/null; then
    ask_remove "redshift (dependencia de Cinnamon)" redshift
fi

if command -v ddcutil &>/dev/null; then
    ask_remove "ddcutil (control de brillo/contraste)" ddcutil
fi

echo ""
echo "=== Desinstalación completada ==="
echo "La aplicación ha sido eliminada."