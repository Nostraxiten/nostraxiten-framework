import os
import platform
import shutil
from pathlib import Path
from config.settings import settings

IS_TERMUX = bool(
    os.environ.get('TERMUX_VERSION') or
    'com.termux' in os.environ.get('PREFIX', '')
)

IS_ROOT = (os.geteuid() == 0) if hasattr(os, 'geteuid') else False

def detect_package_manager():
    if IS_TERMUX:
        return 'pkg'
    sys_os = platform.system().lower()
    if sys_os == 'darwin':
        return 'brew'
    if sys_os == 'windows':
        if shutil.which('winget'): return 'winget'
        if shutil.which('choco'): return 'choco'
        return 'winget'
    for mgr in ['apt', 'apt-get', 'pacman', 'dnf', 'yum', 'zypper', 'apk']:
        if shutil.which(mgr):
            return mgr
    return 'apt'

PKG_MGR = detect_package_manager()
HOME = Path.home()

# Utilize the config for BASE_DIR, defaulting to ~/Datos
BASE_DIR = Path(settings.base_dir)
try:
    BASE_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass
