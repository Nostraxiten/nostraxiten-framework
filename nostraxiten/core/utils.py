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

def run_and_save(cmd, out_path, shell=True):
    out_path = Path(out_path)
    lines = []
    try:
        proc = subprocess.Popen(
            cmd,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors='replace',
            bufsize=1
        )
        if proc.stdout:
            for line in proc.stdout:
                print(line, end='', flush=True)
                lines.append(line)
        proc.wait()
        save_file(out_path, "".join(lines))
        return proc.returncode
    except Exception as e:
        err_msg = f"Error ejecutando comando: {e}\n"
        print(f"  {r('✗')} {err_msg}")
        save_file(out_path, err_msg)
        return 1

def exists(cmd):
    return shutil.which(cmd) is not None

def pkg_install(name):
    print(f"  {y('→')} {PKG_MGR} install {name}...")
    if os.name == 'nt':
        subprocess.run([PKG_MGR, 'install', '-e', '--id', name], capture_output=True)
    else:
        subprocess.run([PKG_MGR, 'install', '-y', name], capture_output=True)

def pip_install(name):
    print(f"  {y('→')} pip install {name}...")
    cmd = [sys.executable, '-m', 'pip', 'install', name, '-q']
    if os.name != 'nt' and not IS_TERMUX:
        cmd.append('--break-system-packages')
    subprocess.run(cmd, capture_output=True)

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
    with open(path, 'w', encoding='utf-8', errors='replace') as f:
        f.write(str(content))

def shell_out(cmd):
    o, e, _ = run(cmd)
    return o.strip() or e.strip() or '(sin salida)'

def new_session(name='session'):
    ts   = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    path = BASE_DIR / f"{ts}_{name}"
    path.mkdir(parents=True, exist_ok=True)
    try:
        from config.settings import settings
        settings.last_session = str(path)
        settings.save()
    except Exception:
        pass
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
    if IS_TERMUX:
        os_label = "Termux"
        env = f"{C.G}{os_label}{C.RS}"
    elif os.name == 'nt':
        os_label = "Windows"
        env = f"{C.CY}{os_label}{C.RS}"
    elif sys.platform == 'darwin':
        os_label = "macOS"
        env = f"{C.CY}{os_label}{C.RS}"
    else:
        os_label = "Linux"
        env = f"{C.CY}{os_label}{C.RS}"
    priv_label = "● ROOT" if IS_ROOT else "● user"
    priv = f"{C.R}{priv_label}{C.RS}" if IS_ROOT else f"{C.Y}{priv_label}{C.RS}"
    
    # Calculate box spacing cleanly
    inner_len = len(now) + 2 + len(os_label) + 2 + len(priv_label)
    pad = " " * max(2, 58 - inner_len)
    
    print(f"  {C.CY}╔════════════════════════════════════════════════════════════╗")
    print(f"  ║  {C.Y}FORENX{C.CY} / {C.W}NOXFORENS{C.CY} ── Digital Forensics Suite v1.7        ║")
    print(f"  ║  {C.DM}{now}{C.RS}  {env}  {priv}{pad}{C.CY}║")
    print(f"  ╚════════════════════════════════════════════════════════════╝{C.RS}\n")
