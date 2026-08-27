import os
from pathlib import Path
from config.settings import settings

IS_TERMUX = bool(
    os.environ.get('TERMUX_VERSION') or
    'com.termux' in os.environ.get('PREFIX', '')
)

IS_ROOT = (os.geteuid() == 0) if hasattr(os, 'geteuid') else False
PKG_MGR = 'pkg' if IS_TERMUX else 'apt'
HOME = Path.home()

# Utilize the config for BASE_DIR, defaulting to ~/Datos
BASE_DIR = Path(settings.base_dir)
BASE_DIR.mkdir(parents=True, exist_ok=True)
