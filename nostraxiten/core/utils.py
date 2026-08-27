import os
import sys
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from core.colors import C, r, g, y, cy, dm, w
from core.env import IS_TERMUX, IS_ROOT, PKG_MGR, BASE_DIR
from core.logo import LOGO

def run(cmd, shell=True, timeout=120):
    try:
        p = subprocess.run(
            cmd, shell=shell, capture_output=True,
            text=True, timeout=timeout, errors='replace'
        )
        return p.stdout, p.stderr, p.returncode
    except subprocess.TimeoutExpired:
        return '', 'TIMEOUT', 1
    except Exception as e:
        return '', str(e), 1

def exists(cmd):
    return shutil.which(cmd) is not None

def pkg_install(name):
    print(f"  {y('→')} {PKG_MGR} install {name}...")
    os.system(f'{PKG_MGR} install -y {name} 2>/dev/null')

def pip_install(name):
    print(f"  {y('→')} pip install {name}...")
    subprocess.run(
        [sys.executable, '-m', 'pip', 'install', name,
         '--break-system-packages', '-q'],
        capture_output=True
    )

def git_clone(url, dest):
    dest = Path(dest)
    if not dest.exists():
        print(f"  {y('→')} git clone {url}...")
        os.system(f'git clone {url} {dest} -q 2>/dev/null')
    else:
        print(f"  {dm(f'→ {dest} ya existe, omitiendo clone')}")

def check_install(binary, pkg=None, pip=None, git_url=None, git_dest=None):
    if exists(binary):
        return True
    print(f"\n  {y('⚠')} {w(binary)} no encontrado.")
    resp = inp(f"¿Instalar {binary}? [s/N]: ")
    if resp.lower() != 's':
        return False
    if pkg:
        pkg_install(pkg)
        if exists(binary):
            return True
    if pip:
        pip_install(pip)
        if exists(binary):
            return True
    if git_url:
        git_clone(git_url, git_dest or f'/opt/{binary}')
        return True
    print(f"  {r('✗')} Instalación fallida. Instala {binary} manualmente.")
    return False

def save_file(path, content):
    with open(path, 'w', errors='replace') as f:
        f.write(str(content))

def shell_out(cmd):
    o, e, _ = run(cmd)
    return o.strip() or e.strip() or '(sin salida)'

def new_session(name='session'):
    ts   = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    path = BASE_DIR / f"{ts}_{name}"
    path.mkdir(parents=True, exist_ok=True)
    return path

def inp(prompt=''):
    try:
        return input(f"  {cy('›')} {prompt}").strip()
    except (KeyboardInterrupt, EOFError):
        return ''

def pause():
    try:
        input(f"\n  {dm('[Enter para volver al menú]')}")
    except (KeyboardInterrupt, EOFError):
        pass

def hdr(num, name, desc=''):
    print(f"\n  {C.BD}{C.CY}[{num:02d}]{C.RS} {C.W}{C.BD}{name}{C.RS}")
    if desc:
        print(f"  {dm(desc)}")
    print(f"  {C.DM}{'─' * 52}{C.RS}")

def warn_termux(skip=False):
    if IS_TERMUX:
        msg = "Herramienta NO disponible en Termux." if skip else "Resultados limitados en Termux."
        print(f"  {y('⚠')} {msg}")
        if skip:
            pause()
        return True
    return False

def banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(LOGO)
    now  = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    env  = f"{C.G}Termux{C.RS}" if IS_TERMUX else f"{C.CY}Kali/Linux{C.RS}"
    priv = f"{C.R}● ROOT{C.RS}" if IS_ROOT else f"{C.Y}● user{C.RS}"
    padding = " " * (18 if not IS_TERMUX else 22)
    print(f"  {C.CY}╔════════════════════════════════════════════════════════════╗")
    print(f"  ║  {C.Y}FORENX{C.CY} / {C.W}NOXFORENS{C.CY} ── Digital Forensics Suite v1.1        ║")
    print(f"  ║  {C.DM}{now}{C.RS}  {env}  {priv} {padding}{C.CY}║")
    print(f"  ╚════════════════════════════════════════════════════════════╝{C.RS}\n")
