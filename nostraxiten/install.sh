#!/usr/bin/env bash

# NOSTRAXITEN Installer for Linux/Kali/Termux

# Colores
R="\033[91m"
G="\033[92m"
Y="\033[93m"
CY="\033[96m"
RS="\033[0m"

echo -e "${CY}=================================================${RS}"
echo -e "${CY}      NOSTRAXITEN Installer (Linux / Termux)       ${RS}"
echo -e "${CY}=================================================${RS}\n"

# 1. Detectar entorno
IS_TERMUX=0
if [[ -n "$TERMUX_VERSION" ]] || [[ "$PREFIX" == *"com.termux"* ]]; then
    IS_TERMUX=1
    PKG_MGR="pkg"
    echo -e "${Y}[*] Entorno Termux detectado.${RS}"
else
    PKG_MGR="apt"
    echo -e "${Y}[*] Entorno Kali/Debian/Linux detectado.${RS}"
fi

# 2. Instalar dependencias del sistema y Python
echo -e "\n${CY}[+] Instalando dependencias base del sistema...${RS}"
if [ $IS_TERMUX -eq 1 ]; then
    $PKG_MGR update -y
    $PKG_MGR install -y python git nmap
else
    if [ "$EUID" -ne 0 ]; then
        echo -e "${R}[!] Debes ejecutar este script como root (sudo) en Linux para instalar paquetes del sistema.${RS}"
        exit 1
    fi
    apt update -y
    apt install -y python3 python3-venv python3-pip nmap exiftool tshark steghide foremost bulk-extractor lynis chkrootkit git
fi

# 3. Crear entorno virtual
echo -e "\n${CY}[+] Configurando Entorno Virtual (.venv)...${RS}"
cd "$(dirname "$0")" || exit
python3 -m venv .venv
source .venv/bin/activate

# 4. Instalar dependencias Python
echo -e "\n${CY}[+] Instalando dependencias de Python (requirements.txt)...${RS}"
pip install --upgrade pip
pip install -r requirements.txt

# 7. Generar lanzador global
echo -e "\n${CY}[+] Creando script lanzador...${RS}"
if [ $IS_TERMUX -eq 1 ]; then
    BIN_DIR="$PREFIX/bin"
else
    BIN_DIR="/usr/local/bin"
fi

cat << 'EOF' > "$BIN_DIR/nostraxiten"
#!/usr/bin/env bash
SCRIPT_DIR="$(dirname "$(realpath "$0")")"
# Si el script está en bin, buscamos la ruta real de instalación
INSTALL_DIR=$(dirname "$(realpath "$(which nostraxiten)")")
# Ajuste de ruta basado en la creación del lanzador
if [ -d "$INSTALL_DIR/.venv" ]; then
    source "$INSTALL_DIR/.venv/bin/activate"
    python3 "$INSTALL_DIR/nostraxiten.py" "$@"
else
    # Fallback si se mueve de carpeta pero el lanzador apunta a otra
    # Aquí buscamos la ruta original donde se instaló:
EOF
echo "    INSTALL_DIR=\"$(pwd)\"" >> "$BIN_DIR/nostraxiten"
cat << 'EOF' >> "$BIN_DIR/nostraxiten"
    source "$INSTALL_DIR/.venv/bin/activate"
    python3 "$INSTALL_DIR/nostraxiten.py" "$@"
fi
EOF

chmod +x "$BIN_DIR/nostraxiten"

echo -e "\n${G}[✓] ¡Instalación completa!${RS}"
echo -e "${G}[✓] Ejecuta ${CY}nostraxiten${G} desde cualquier lugar para iniciar.${RS}"
