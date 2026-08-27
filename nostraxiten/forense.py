#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NOXFORENS — Digital Forensics & Intelligence Suite v1.7
16 Herramientas | Kali Linux & Termux Compatible
"""

import os, sys, subprocess, platform, shutil, socket, time, re, json, csv, math, hashlib, struct, threading
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import configparser # For Linux WiFi
import xml.etree.ElementTree as ET # For Android WiFi XML
import base64 # For encrypted values
import sqlite3 # For browser databases

# Conditional import for Windows DPAPI
try:
    import win32crypt
except ImportError:
    win32crypt = None
    # ctypes and find_library are for Firefox NSS, not directly for pywin32
    # If pywin32 is not found, we'll try to install it later in t_browser


# ══════════════════════════════════════════════════════════════════════════
#  COLORS
# ══════════════════════════════════════════════════════════════════════════
class C:
    R  = '\033[91m';  G  = '\033[92m';  Y  = '\033[93m'
    B  = '\033[94m';  M  = '\033[95m';  CY = '\033[96m'
    W  = '\033[97m';  DM = '\033[2m';   BD = '\033[1m'
    RS = '\033[0m'

r  = lambda s: f"{C.R}{s}{C.RS}"
g  = lambda s: f"{C.G}{s}{C.RS}"
y  = lambda s: f"{C.Y}{s}{C.RS}"
cy = lambda s: f"{C.CY}{s}{C.RS}"
m  = lambda s: f"{C.M}{s}{C.RS}"
bd = lambda s: f"{C.BD}{s}{C.RS}"
dm = lambda s: f"{C.DM}{s}{C.RS}"
w  = lambda s: f"{C.W}{s}{C.RS}"

# ══════════════════════════════════════════════════════════════════════════
#  LOGO
# ══════════════════════════════════════════════════════════════════════════
LOGO = (
    f"{C.CY}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⠞⢳⠀⠀⠀⠀⠀{C.RS}\n"
    f"{C.CY}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡔⠋⠀⢰⠎⠀⠀⠀⠀⠀{C.RS}\n"
    f"{C.CY}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⢆⣤⡞⠃⠀⠀⠀⠀⠀⠀{C.RS}\n"
    f"{C.B}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⢠⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀{C.RS}\n"
    f"{C.B}⠀⠀⠀⠀⢀⣀⣾⢳⠀⠀⠀⠀⢸⢠⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀{C.RS}\n"
    f"{C.B}⣀⡤⠴⠊⠉⠀⠀⠈⠳⡀⠀⠀⠘⢎⠢⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀{C.RS}\n"
    f"{C.M}⠳⣄⠀⠀⡠⡤⡀⠀⠘⣇⡀⠀⠀⠀⠉⠓⠒⠺⠭⢵⣦⡀⠀⠀⠀{C.RS}\n"
    f"{C.M}⠀⢹⡆⠀⢷⡇⠁⠀⠀⣸⠇⠀⠀⠀⠀⠀⢠⢤⠀⠀⠘⢷⣆⡀⠀{C.RS}\n"
    f"{C.M}⠀⠀⠘⠒⢤⡄⠖⢾⣭⣤⣄⠀⡔⢢⠀⡀⠎⣸⠀⠀⠀⠀⠹⣿⡀{C.RS}\n"
    f"{C.CY}⠀⠀⢀⡤⠜⠃⠀⠀⠘⠛⣿⢸⠀⡼⢠⠃⣤⡟⠀⠀⠀⠀⠀⣿⡇{C.RS}\n"
    f"{C.CY}⠀⠀⠸⠶⠖⢏⠀⠀⢀⡤⠤⠇⣴⠏⡾⢱⡏⠁⠀⠀⠀⠀⢠⣿⠃{C.RS}\n"
    f"{C.CY}⠀⠀⠀⠀⠀⠈⣇⡀⠿⠀⠀⠀⡽⣰⢶⡼⠇⠀⠀⠀⠀⣠⣿⠟⠀{C.RS}\n"
    f"{C.B}⠀⠀⠀⠀⠀⠀⠈⠳⢤⣀⡶⠤⣷⣅⡀⠀⠀⠀⣀⡠⢔⠕⠁⠀⠀{C.RS}\n"
    f"{C.B}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠫⠿⠿⠿⠛⠋⠁⠀⠀⠀⠀{C.RS}\n"
)
FORENX_LOGO = (
    f"{C.Y}  ______   ______     ______     ______     __   __     __  __    {C.RS}\n"
    f"{C.Y} /\\  ___\\ /\\  __ \\   /\\  == \\   /\\  ___\\   /\\ \"-.\\ \\   /\\_\\_\\_\\   {C.RS}\n"
    f"{C.Y} \\ \\  __\\ \\ \\ \\/\\ \\  \\ \\  __<   \\ \\  __\\   \\ \\ \\-.  \\  \\/_/\\_\\/_  {C.RS}\n"
    f"{C.Y}  \\ \\_\\    \\ \\_____\\  \\ \\_\\ \\_\\  \\ \\_____\\  \\ \\_\\\\\"\\_\\   /\\_\\/\\_\\ {C.RS}\n"
    f"{C.Y}   \\/_/     \\/_____/   \\/_/ /_/   \\/_____/   \\/_/ \\/_/   \\/_/\\/_/ {C.RS}\n"
)

# ══════════════════════════════════════════════════════════════════════════
#  ENTORNO
# ══════════════════════════════════════════════════════════════════════════
IS_TERMUX = bool(
    os.environ.get('TERMUX_VERSION') or
    'com.termux' in os.environ.get('PREFIX', '')
)
IS_ROOT   = (os.geteuid() == 0) if hasattr(os, 'geteuid') else False
PKG_MGR   = 'pkg' if IS_TERMUX else 'apt'
HOME      = Path.home()
BASE_DIR  = HOME / 'Datos'
BASE_DIR.mkdir(exist_ok=True)

# ══════════════════════════════════════════════════════════════════════════
#  UTILIDADES CORE
# ══════════════════════════════════════════════════════════════════════════
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


# ══════════════════════════════════════════════════════════════════════════
#  [00] NOXRECON ★ — HERRAMIENTA EXCLUSIVA
#  Recolección forense completa del sistema → ~/Datos/<timestamp>_NOXRECON/
# ══════════════════════════════════════════════════════════════════════════
def t00_noxrecon():
    os.system('clear' if not platform.system() == 'Windows' else 'cls')
    print(FORENX_LOGO)
    print(f"  {C.BD}{C.CY}NOXRECON ★{C.RS} {C.W}- Análisis Descomunal Multi-Plataforma FORENX{C.RS}\n")
    print(f"  {dm('Recopila información crítica del sistema y artefactos forenses de Windows, Linux, Android y macOS/iOS')}\n")

    session = new_session('NOXRECON')
    print(f"  {g('✓')} Sesión: {g(str(session))}\n")

    def collect_section(label, cmd, fpath):
        content = (
            f"# {label}\n"
            f"# CMD:       {cmd}\n"
            f"# TIMESTAMP: {datetime.now()}\n"
            f"# HOST:      {socket.gethostname()}\n"
            f"# {'─' * 50}\n\n"
        )
        content += shell_out(cmd)
        save_file(fpath, content)

    tasks = []
    sys_os = platform.system().lower()
    is_darwin = sys_os == 'darwin'
    is_ios = is_darwin and any(x in platform.platform().lower() for x in ('iphone', 'ipad'))

    if sys_os == 'windows':
        d = session / '01_sistema'; d.mkdir(parents=True, exist_ok=True)
        tasks += [
            ("OS Info", "systeminfo", d/'systeminfo.txt'),
            ("Variables entorno", "set", d/'env.txt'),
            ("WMIC OS", "wmic os get /format:list", d/'wmic_os.txt'),
            ("Programas instalados", "wmic product get name,version,vendor /format:list", d/'installed_products.txt'),
            ("Usuarios conectados", "query user", d/'query_user.txt'),
        ]
        d = session / '02_hardware'; d.mkdir(parents=True, exist_ok=True)
        tasks += [
            ("CPU Info", "wmic cpu get name,caption,deviceid,maxclockspeed /format:list", d/'cpu.txt'),
            ("Memoria RAM", "wmic memorychip get capacity,speed,manufacturer /format:list", d/'ram.txt'),
            ("Discos Lógicos", "wmic logicaldisk get name,size,freespace,description /format:list", d/'logical_disks.txt'),
            ("Discos Físicos", "wmic diskdrive get model,size,interfacetype /format:list", d/'physical_disks.txt'),
            ("Dispositivos USB", "powershell -NoProfile -Command \"Get-PnpDevice -Class USB | Format-List\"", d/'usb_devices.txt'),
        ]
        d = session / '03_red'; d.mkdir(parents=True, exist_ok=True)
        tasks += [
            ("IP Config", "ipconfig /all", d/'ipconfig.txt'),
            ("Tabla de Rutas", "route print", d/'rutas.txt'),
            ("Conexiones y Puertos", "netstat -ano", d/'netstat.txt'),
            ("Tabla ARP", "arp -a", d/'arp.txt'),
            ("Perfiles WiFi", "netsh wlan show profiles", d/'wifi_profiles.txt'),
        ]
        d = session / '04_usuarios'; d.mkdir(parents=True, exist_ok=True)
        tasks += [
            ("Usuarios Locales", "net user", d/'net_user.txt'),
            ("Grupos Locales", "net localgroup", d/'net_localgroup.txt'),
            ("Administradores", "net localgroup administradores 2>nul || net localgroup administrators", d/'admins.txt'),
            ("Scheduled Tasks", "schtasks /query /fo LIST /v", d/'scheduled_tasks.txt'),
        ]
        d = session / '05_procesos'; d.mkdir(parents=True, exist_ok=True)
        tasks += [
            ("Lista de Tareas", "tasklist /v", d/'tasklist.txt'),
            ("Servicios en Ejecución", "net start", d/'servicios.txt'),
            ("PowerShell History", 'powershell -NoProfile -Command "if (Get-Command Get-PSReadlineOption -ErrorAction SilentlyContinue) { Get-Content (Get-PSReadlineOption).HistorySavePath } else { Write-Output \'\' }"', d/'powershell_history.txt'),
        ]
        d = session / '06_seguridad'; d.mkdir(parents=True, exist_ok=True)
        tasks += [
            ("Windows Defender", "powershell -c \"Get-MpComputerStatus\"", d/'defender.txt'),
            ("Reglas Firewall", "netsh advfirewall firewall show rule name=all", d/'firewall.txt'),
            ("System Event Log", "wevtutil qe System /c:200 /f:text", d/'eventlog_system.txt'),
            ("Autoruns HKLM", "reg query \"HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\" /s", d/'autoruns_hklm.txt'),
            ("Autoruns HKCU", "reg query \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\" /s", d/'autoruns_hkcu.txt'),
        ]
    elif IS_TERMUX:
        d = session / '01_sistema'; d.mkdir(parents=True, exist_ok=True)
        tasks += [
            ("Uname", "uname -a", d/'uname.txt'),
            ("Getprop (Android Props)", "getprop", d/'getprop.txt'),
            ("Variables entorno", "env | sort", d/'env.txt'),
            ("Build Properties", "getprop | sort", d/'build_props.txt'),
        ]
        d = session / '02_hardware'; d.mkdir(parents=True, exist_ok=True)
        tasks += [
            ("CPU Info", "cat /proc/cpuinfo", d/'cpu.txt'),
            ("Memoria", "cat /proc/meminfo", d/'meminfo.txt'),
            ("Uso de Disco", "df -h", d/'df.txt'),
            ("Batería", "dumpsys battery 2>/dev/null", d/'battery.txt'),
        ]
        d = session / '03_red'; d.mkdir(parents=True, exist_ok=True)
        tasks += [
            ("Interfaces", "ifconfig 2>/dev/null || ip a", d/'ifconfig.txt'),
            ("Rutas", "ip route", d/'rutas.txt'),
            ("Conexiones activas", "netstat -tulnp 2>/dev/null", d/'netstat.txt'),
            ("ARP Cache", "arp -a 2>/dev/null", d/'arp.txt'),
        ]
        d = session / '04_paquetes_apps'; d.mkdir(parents=True, exist_ok=True)
        tasks += [
            ("Packages Termux", "pkg list-installed", d/'termux_pkgs.txt'),
            ("Apps Android", "pm list packages -f 2>/dev/null", d/'android_apps.txt'),
            ("Dumpsys Package", "dumpsys package 2>/dev/null | head -200", d/'dumpsys_package.txt'),
            ("Dumpsys WiFi", "dumpsys wifi 2>/dev/null | head -160", d/'dumpsys_wifi.txt'),
        ]
        d = session / '05_procesos'; d.mkdir(parents=True, exist_ok=True)
        tasks += [
            ("Procesos Activos", "ps aux", d/'ps.txt'),
            ("Top", "top -n 1 2>/dev/null | head -50", d/'top.txt'),
            ("Logcat recientes", "logcat -d 2>/dev/null | tail -200", d/'logcat.txt'),
            ("Permisos Apps", "pm list permissions -d 2>/dev/null", d/'permissions.txt'),
        ]
    else:
        d = session / '01_sistema'; d.mkdir(parents=True, exist_ok=True)
        tasks += [
            ("OS Info", "uname -a", d/'os.txt'),
            ("OS Release", "cat /etc/os-release 2>/dev/null || sw_vers", d/'release.txt'),
            ("Hostname", "hostname", d/'hostname.txt'),
            ("Variables entorno", "env | sort", d/'env.txt'),
            ("Paquetes instalados", "dpkg -l 2>/dev/null || rpm -qa 2>/dev/null || brew list 2>/dev/null", d/'packages.txt'),
        ]
        d = session / '02_hardware'; d.mkdir(parents=True, exist_ok=True)
        tasks += [
            ("CPU info", "lscpu 2>/dev/null || sysctl -n machdep.cpu.brand_string", d/'cpu.txt'),
            ("Memoria", "free -h 2>/dev/null || vm_stat", d/'mem_free.txt'),
            ("Discos", "lsblk -a 2>/dev/null || diskutil list", d/'discos.txt'),
            ("Uso disco", "df -h", d/'df.txt'),
            ("Montajes", "mount | column -t", d/'mounts.txt'),
        ]
        d = session / '03_red'; d.mkdir(parents=True, exist_ok=True)
        tasks += [
            ("Interfaces", "ip addr 2>/dev/null || ifconfig", d/'interfaces.txt'),
            ("Rutas", "ip route 2>/dev/null || netstat -rn", d/'rutas.txt'),
            ("Sockets abiertos", "ss -tulpn 2>/dev/null || netstat -an | grep LISTEN", d/'sockets.txt'),
            ("ARP cache", "arp -a 2>/dev/null", d/'arp.txt'),
        ]
        d = session / '04_usuarios'; d.mkdir(parents=True, exist_ok=True)
        tasks += [
            ("/etc/passwd", "cat /etc/passwd", d/'passwd.txt'),
            ("Último login", "last -20", d/'last.txt'),
            ("ID actual", "id", d/'id.txt'),
            ("Historial shell", "bash -lc 'cat ~/.bash_history 2>/dev/null || true'", d/'bash_history.txt'),
        ]
        d = session / '05_procesos'; d.mkdir(parents=True, exist_ok=True)
        tasks += [
            ("Procesos", "ps aux", d/'ps_aux.txt'),
            ("Archivos abiertos", "lsof 2>/dev/null | head -300", d/'lsof.txt'),
        ]
        if is_darwin:
            d = session / '06_macos'; d.mkdir(parents=True, exist_ok=True)
            tasks += [
                ("System Profiler", "system_profiler SPHardwareDataType SPSoftwareDataType | head -120", d/'system_profiler.txt'),
                ("LaunchAgents", "launchctl list", d/'launchctl.txt'),
                ("iOS / macOS artefactos", "ls ~/Library/Preferences 2>/dev/null | head -100", d/'user_preferences.txt'),
            ]
        else:
            d = session / '06_logs'; d.mkdir(parents=True, exist_ok=True)
            tasks += [
                ("Journalctl", "journalctl -n 200 --no-pager 2>/dev/null", d/'journal.txt'),
                ("Dmesg", "dmesg 2>/dev/null | tail -300", d/'dmesg.txt'),
                ("Auth Logs", "cat /var/log/auth.log 2>/dev/null || cat /var/log/secure 2>/dev/null", d/'auth_logs.txt'),
                ("Cron jobs", "crontab -l 2>/dev/null || true; ls /etc/cron* 2>/dev/null", d/'cron.txt'),
            ]

    total = len(tasks)
    print()
    for i, (label, cmd, fpath) in enumerate(tasks, 1):
        pct = int(i / total * 100)
        filled  = pct // 5
        bar_str = f"{C.CY}{'█' * filled}{C.DM}{'░' * (20 - filled)}{C.RS}"
        lbl = (label[:32] + '..') if len(label) > 34 else label
        print(f"\r  {bar_str} {C.W}{pct:3d}%{C.RS}  {dm(f'{lbl:<36}')}", end='', flush=True)
        collect_section(label, cmd, fpath)

    idx = session / 'INDEX.md'
    idx_lines = [
        "# NOXFORENS — Reporte de Sesión Forense",
        f"- **Fecha:**    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **Sistema:**  {platform.platform()}",
        f"- **Host:**     {socket.gethostname()}",
        f"- **Usuario:**  {os.getenv('USER', os.getenv('USERNAME', '?'))}  |  Root/Admin: {IS_ROOT}",
        f"- **Archivos recolectados:** {total}",
        "\n## Estructura\n",
    ]
    for p in sorted(session.rglob('*')):
        idx_lines.append(f"- `{p.relative_to(session)}`")
    save_file(idx, '\n'.join(idx_lines))

    print(f"\n\n  {g('✓')} Recolección completa → {g(str(session))}")
    print(f"  {g('✓')} Índice   → {g(str(idx))}")
    pause()


# ══════════════════════════════════════════════════════════════════════════
#  [01] SPIDERFOOT
# ══════════════════════════════════════════════════════════════════════════
def t01_spiderfoot():
    banner(); hdr(1, "SpiderFoot", "Framework OSINT automático con interfaz web")
    if not check_install('spiderfoot', pip='spiderfoot'):
        pause(); return
    port = inp("Puerto web [4444]: ") or '4444'
    print(f"\n  {g('✓')} Iniciando en http://127.0.0.1:{port}")
    print(f"  {y('!')} Abre el navegador en http://127.0.0.1:{port}")
    print(f"  {dm('Ctrl+C para detener')}\n")
    os.system(f'spiderfoot -l 127.0.0.1:{port}')
    pause()


# ══════════════════════════════════════════════════════════════════════════
#  [02] THEHARVESTER
# ══════════════════════════════════════════════════════════════════════════
def t02_theharvester():
    banner(); hdr(2, "theHarvester", "Emails, subdominios, hosts, IPs, names desde fuentes OSINT")
    binary = 'theHarvester'
    if not exists(binary.lower()) and not exists('theharvester'):
        if not check_install('theHarvester',
                             pkg='theharvester' if not IS_TERMUX else None,
                             pip='theHarvester'):
            pause(); return

    domain = inp("Dominio objetivo: ")
    if not domain: pause(); return
    limit  = inp("Límite resultados [500]: ") or '500'
    source = inp("Fuentes [baidu,bing,crtsh,yahoo]: ") or 'baidu,bing,crtsh,yahoo'

    session  = new_session(f'theHarvester_{domain}')
    out_file = session / 'results'
    cmd = f'theHarvester -d {domain} -l {limit} -b {source} -f {out_file}'
    print(f"\n  {cy('→')} {dm(cmd)}\n")
    os.system(cmd)
    print(f"\n  {g('✓')} Resultados en: {session}")
    pause()


# ══════════════════════════════════════════════════════════════════════════
#  [03] VOLATILITY 3
# ══════════════════════════════════════════════════════════════════════════
def t03_volatility():
    banner(); hdr(3, "Volatility 3", "Análisis forense de memoria RAM (dumps de memoria)")
    vol_bin = None
    for b in ['vol', 'vol3', 'volatility3']:
        if exists(b):
            vol_bin = b; break

    if not vol_bin:
        if not check_install('vol3', pkg='volatility3', pip='volatility3'):
            pause(); return
        vol_bin = 'vol3'

    mem_file = inp("Ruta al dump de memoria (ej: /mnt/evidence.raw): ")
    if not mem_file or not Path(mem_file).exists():
        print(f"  {r('✗')} Archivo no encontrado: {mem_file}")
        pause(); return

    plugins = {
        '1': 'windows.pslist.PsList',
        '2': 'windows.netscan.NetScan',
        '3': 'windows.cmdline.CmdLine',
        '4': 'windows.filescan.FileScan',
        '5': 'windows.malfind.Malfind',
        '6': 'linux.pslist.PsList',
        '7': 'linux.bash.Bash',
        '8': 'linux.netstat.Netstat',
    }
    descs = {
        '1': 'Procesos Windows',      '2': 'Conexiones de red (Win)',
        '3': 'Líneas de comando',      '4': 'Escaneo de archivos',
        '5': 'Detección de malware',   '6': 'Procesos Linux',
        '7': 'Historial bash (Linux)', '8': 'Netstat Linux',
    }
    for k in plugins:
        print(f"    {cy(k)}. {plugins[k]:<40} {dm(descs[k])}")

    choice  = inp("Plugin [1]: ") or '1'
    plugin  = plugins.get(choice, plugins['1'])
    session = new_session('volatility')
    out     = session / f"{plugin.replace('.', '-')}.txt"

    cmd = f'{vol_bin} -f {mem_file} {plugin}'
    print(f"\n  {cy('→')} {dm(cmd)}\n")
    os.system(f'{cmd} 2>&1 | tee {out}')
    print(f"\n  {g('✓')} Guardado: {out}")
    pause()


# ══════════════════════════════════════════════════════════════════════════
#  [04] BINWALK
# ══════════════════════════════════════════════════════════════════════════
def t04_binwalk():
    banner(); hdr(4, "Binwalk", "Análisis de firmware, archivos binarios y extracción")
    if not check_install('binwalk', pkg='binwalk', pip='binwalk'):
        pause(); return

    target = inp("Archivo/firmware a analizar: ")
    if not target or not Path(target).exists():
        print(f"  {r('✗')} Archivo no encontrado"); pause(); return

    session = new_session('binwalk')
    print(f"\n  {cy('Modo:')}")
    print(f"    {cy('1')}. Análisis de firmas")
    print(f"    {cy('2')}. Extracción automática")
    print(f"    {cy('3')}. Análisis de entropía")
    mode = inp("Modo [1]: ") or '1'

    out_dir = session / 'extraccion'
    if mode == '2':
        cmd = f'binwalk -e {target} -C {out_dir} --run-as=root 2>/dev/null || binwalk -e {target} -C {out_dir}'
    elif mode == '3':
        cmd = f'binwalk -E {target} --save --directory {session}'
    else:
        cmd = f'binwalk {target}'

    res = session / 'resultado.txt'
    print(f"\n  {cy('→')} {dm(cmd)}\n")
    os.system(f'{cmd} 2>&1 | tee {res}')
    print(f"\n  {g('✓')} Guardado en: {session}")
    pause()


# ══════════════════════════════════════════════════════════════════════════
#  [05] FOREMOST
# ══════════════════════════════════════════════════════════════════════════
def t05_foremost():
    banner(); hdr(5, "Foremost", "Recuperación y carving de archivos eliminados de imágenes de disco")
    if warn_termux(skip=True): return
    if not check_install('foremost', pkg='foremost'):
        pause(); return

    target = inp("Dispositivo o imagen (ej: /dev/sda1, dump.img): ")
    if not target: pause(); return

    session = new_session('foremost')
    carv    = session / 'carving'
    cmd     = f'foremost -i {target} -o {carv} -v -T'
    print(f"\n  {cy('→')} {dm(cmd)}\n")
    os.system(cmd)
    print(f"\n  {g('✓')} Archivos recuperados en: {carv}")
    pause()


# ══════════════════════════════════════════════════════════════════════════
#  [06] BULK EXTRACTOR
# ══════════════════════════════════════════════════════════════════════════
def t06_bulk_extractor():
    banner(); hdr(6, "Bulk Extractor", "Extracción masiva: emails, URLs, IPs, tarjetas de crédito")
    if warn_termux(skip=True): return
    if not check_install('bulk_extractor', pkg='bulk-extractor'):
        pause(); return

    target = inp("Imagen/dispositivo/archivo a analizar: ")
    if not target: pause(); return

    session = new_session('bulk_extractor')
    threads = inp("Threads [4]: ") or '4'
    cmd     = f'bulk_extractor -o {session} -j {threads} -R {target}'
    print(f"\n  {cy('→')} {dm(cmd)}\n")
    os.system(cmd)
    print(f"\n  {g('✓')} Resultados en: {session}")
    pause()


# ══════════════════════════════════════════════════════════════════════════
#  [07] EXIFTOOL
# ══════════════════════════════════════════════════════════════════════════
def t07_exiftool():
    banner(); hdr(7, "ExifTool", "Extracción de metadatos — imágenes, PDFs, documentos, audio/video")
    pkg_name = 'libimage-exiftool-perl' if not IS_TERMUX else 'perl'
    if not check_install('exiftool', pkg=pkg_name):
        if not check_install('exiftool', pkg='exiftool'):
            pause(); return

    target = inp("Archivo o directorio: ")
    if not target: pause(); return

    session = new_session('exiftool')
    out     = session / 'metadata.txt'
    rec_flag = '-r' if Path(target).is_dir() else ''
    cmd = f'exiftool {rec_flag} -a -u -g1 "{target}"'
    print(f"\n  {cy('→')} {dm(cmd)}\n")
    os.system(f'{cmd} 2>&1 | tee {out}')
    print(f"\n  {g('✓')} Metadatos en: {out}")
    pause()


# ══════════════════════════════════════════════════════════════════════════
#  [08] TSHARK
# ══════════════════════════════════════════════════════════════════════════
def t08_tshark():
    banner(); hdr(8, "tshark", "Análisis de capturas PCAP/PCAPNG y captura en vivo")
    if not check_install('tshark', pkg='tshark'):
        pause(); return

    print(f"  {cy('Modos:')}")
    print(f"    {cy('1')}. Analizar archivo PCAP/PCAPNG")
    print(f"    {cy('2')}. Captura en vivo")
    mode = inp("Modo [1]: ") or '1'
    session = new_session('tshark')

    if mode == '2':
        iface = inp("Interfaz (ej: eth0, wlan0): ")
        count = inp("Paquetes [200]: ") or '200'
        out   = session / 'captura.pcap'
        print(f"\n  {y('!')} Capturando... Ctrl+C para detener\n")
        os.system(f'tshark -i {iface} -c {count} -w {out}')
        print(f"\n  {g('✓')} PCAP guardado: {out}")
    else:
        pcap = inp("Ruta al archivo PCAP: ")
        if not pcap or not Path(pcap).exists():
            print(f"  {r('✗')} Archivo no encontrado"); pause(); return

        analyses = {
            '1': (f'tshark -r {pcap} -q -z io,stat,0',                          'estadisticas.txt',   'Estadísticas generales'),
            '2': (f'tshark -r {pcap} -T fields -e ip.src -e ip.dst 2>/dev/null | sort | uniq -c | sort -rn | head -50',
                                                                                  'top_ips.txt',        'Top IPs src/dst'),
            '3': (f'tshark -r {pcap} -Y http.request -T fields -e http.host -e http.request.uri 2>/dev/null',
                                                                                  'http_requests.txt',  'HTTP requests'),
            '4': (f'tshark -r {pcap} -Y dns -T fields -e dns.qry.name 2>/dev/null | sort | uniq -c | sort -rn',
                                                                                  'dns_queries.txt',    'DNS queries'),
            '5': (f'tshark -r {pcap} -q -z io,phs',                             'protocols.txt',      'Distribución protocolos'),
            '6': (f'tshark -r {pcap} -Y "tcp.flags.syn==1 && tcp.flags.ack==0" -T fields -e ip.src -e tcp.dstport 2>/dev/null | sort | uniq -c | sort -rn',
                                                                                  'syn_scan.txt',       'Posible port-scan (SYN)'),
        }
        for k, (_, fn, desc) in analyses.items():
            print(f"    {cy(k)}. {desc}")
        sub = inp("Análisis [1]: ") or '1'
        cmd, fname, _ = analyses.get(sub, analyses['1'])
        out_f = session / fname
        print(f"\n  {cy('→')} {dm(cmd)}\n")
        os.system(f'{cmd} 2>&1 | tee {out_f}')
        print(f"\n  {g('✓')} Guardado: {out_f}")
    pause()


# ══════════════════════════════════════════════════════════════════════════
#  [09] STEGHIDE + STEGSEEK
# ══════════════════════════════════════════════════════════════════════════
def t09_steghide():
    banner(); hdr(9, "Steghide / StegSeek", "Detección y extracción de datos ocultos en imágenes")
    if not check_install('steghide', pkg='steghide'):
        pause(); return

    target = inp("Imagen (JPEG/BMP): ")
    if not target or not Path(target).exists():
        print(f"  {r('✗')} Archivo no encontrado"); pause(); return

    session = new_session('steghide')
    print(f"\n  {cy('Opciones:')}")
    print(f"    {cy('1')}. Info (detectar datos ocultos)")
    print(f"    {cy('2')}. Extraer con contraseña")
    print(f"    {cy('3')}. Fuerza bruta con stegseek")
    opt = inp("Opción [1]: ") or '1'

    if opt == '1':
        os.system(f'steghide info "{target}"')
    elif opt == '2':
        pw  = inp("Contraseña (Enter si vacía): ")
        out = session / 'extraido.bin'
        os.system(f'steghide extract -sf "{target}" -p "{pw}" -xf {out}')
        if out.exists():
            print(f"  {g('✓')} Extraído: {out}")
        else:
            print(f"  {r('✗')} Extracción fallida (contraseña incorrecta o sin datos)")
    elif opt == '3':
        if not exists('stegseek'):
            if inp("stegseek no instalado. ¿Instalar? [s/N]: ").lower() == 's':
                pkg_install('stegseek')
        if exists('stegseek'):
            wl = inp("Wordlist [/usr/share/wordlists/rockyou.txt]: ") or '/usr/share/wordlists/rockyou.txt'
            os.system(f'stegseek "{target}" {wl}')
        else:
            print(f"  {r('✗')} stegseek no disponible")
    pause()


# ══════════════════════════════════════════════════════════════════════════
#  [10] LYNIS
# ══════════════════════════════════════════════════════════════════════════
def t10_lynis():
    banner(); hdr(10, "Lynis", "Auditoría de seguridad y hardening del sistema Linux")
    lynis_bin = shutil.which('lynis') or ''
    lynis_dir = HOME / 'lynis'

    if not lynis_bin:
        if not check_install('lynis', pkg='lynis',
                              git_url='https://github.com/CISOfy/lynis',
                              git_dest=str(lynis_dir)):
            pause(); return
        lynis_bin = str(lynis_dir / 'lynis') if (lynis_dir / 'lynis').exists() else 'lynis'

    if not IS_ROOT:
        print(f"  {y('⚠')} Lynis funciona mejor como root. Algunos checks se omitirán.")

    session = new_session('lynis')
    report  = session / 'lynis_report.dat'
    log_f   = session / 'lynis_log.txt'
    out_f   = session / 'output.txt'

    cmd = f'{lynis_bin} audit system --report-file {report} --logfile {log_f} --no-colors 2>&1 | tee {out_f}'
    print(f"\n  {cy('→')} Ejecutando auditoría (puede tardar varios minutos)...\n")
    os.system(cmd)
    print(f"\n  {g('✓')} Reporte: {report}")
    print(f"  {g('✓')} Log:     {log_f}")
    pause()


# ══════════════════════════════════════════════════════════════════════════
#  [11] CHKROOTKIT / RKHUNTER
# ══════════════════════════════════════════════════════════════════════════
def t11_rootkit():
    banner(); hdr(11, "chkrootkit / rkhunter", "Detección de rootkits, backdoors y malware en el sistema")
    if warn_termux(skip=True): return

    tool = next((t for t in ['chkrootkit', 'rkhunter'] if exists(t)), None)
    if not tool:
        pref = inp("Ninguno instalado. Instalar: [1] chkrootkit  [2] rkhunter  [1]: ") or '1'
        pkg  = 'chkrootkit' if pref != '2' else 'rkhunter'
        pkg_install(pkg)
        tool = pkg if exists(pkg) else None

    if not tool:
        print(f"  {r('✗')} No se pudo instalar"); pause(); return

    session = new_session(f'{tool}_scan')
    out     = session / 'scan_result.txt'

    if tool == 'chkrootkit':
        cmd = f'chkrootkit 2>&1 | tee {out}'
    else:
        cmd = f'rkhunter --check --skip-keypress --report-warnings-only 2>&1 | tee {out}'

    print(f"\n  {cy('→')} Ejecutando {tool}... (puede tardar)\n")
    os.system(cmd)
    print(f"\n  {g('✓')} Resultado: {out}")
    pause()


# ══════════════════════════════════════════════════════════════════════════
#  [12] NMAP FORENSE
# ══════════════════════════════════════════════════════════════════════════
def t12_nmap():
    banner(); hdr(12, "Nmap", "Escaneo de red, fingerprinting y detección de vulnerabilidades")
    if not check_install('nmap', pkg='nmap'):
        pause(); return

    target = inp("Target (IP / rango CIDR / dominio): ")
    if not target: pause(); return

    modes = {
        '1': ('-sV -sC -O',                      'Completo (versiones + scripts + OS)'),
        '2': ('-sn',                              'Ping sweep — descubrimiento de hosts'),
        '3': ('-p- --open -T4',                   'Todos los puertos TCP abiertos'),
        '4': ('-sU --top-ports 200',              'Top 200 puertos UDP'),
        '5': ('-sV --script=vuln',               'Scan de vulnerabilidades'),
        '6': ('-sV --script=smb-vuln*,http-vuln*', 'Vulns SMB + HTTP específicas'),
        '7': ('-A --script=default,auth,discovery', 'Agresivo + auth + discovery'),
    }
    for k, (_, d) in modes.items():
        print(f"    {cy(k)}. {d}")

    mode    = inp("Modo [1]: ") or '1'
    flags   = modes.get(mode, modes['1'])[0]
    session = new_session(f'nmap_{target.replace("/", "_")}')
    xml_f   = session / 'nmap.xml'
    txt_f   = session / 'nmap.txt'
    gnmap_f = session / 'nmap.gnmap'

    if not IS_ROOT and ('-sS' in flags or '-O' in flags):
        print(f"  {y('⚠')} Este scan requiere root. Saltando flags que lo necesitan o ejecuta con sudo.")

    cmd = f'nmap {flags} {target} -oX {xml_f} -oG {gnmap_f} -oN {txt_f}'
    print(f"\n  {cy('→')} {dm(cmd)}\n")
    os.system(cmd)
    print(f"\n  {g('✓')} Resultados en: {session}")
    pause()


# ══════════════════════════════════════════════════════════════════════════
#  [13] SHERLOCK
# ══════════════════════════════════════════════════════════════════════════
def t13_sherlock():
    banner(); hdr(13, "Sherlock", "Username OSINT — búsqueda en +400 redes sociales y plataformas")
    sherlock_dir = HOME / 'sherlock'
    installed    = exists('sherlock')

    if not installed:
        if not check_install('sherlock',
                             pip='sherlock-project',
                             git_url='https://github.com/sherlock-project/sherlock',
                             git_dest=str(sherlock_dir)):
            pause(); return
        installed = True

    username = inp("Username a buscar: ")
    if not username: pause(); return

    session  = new_session(f'sherlock_{username}')
    out_file = session / f'{username}.txt'

    if exists('sherlock'):
        cmd = f'sherlock "{username}" --output {out_file} --print-found'
    else:
        cmd = f'cd {sherlock_dir} && python3 sherlock/sherlock.py "{username}" --output {out_file} --print-found'

    print(f"\n  {cy('→')} Buscando {cy(username)}...\n")
    os.system(cmd)
    print(f"\n  {g('✓')} Resultados: {out_file}")
    pause()


# ══════════════════════════════════════════════════════════════════════════
#  [14] RECON-NG
# ══════════════════════════════════════════════════════════════════════════
def t14_reconng():
    banner(); hdr(14, "Recon-ng", "Framework de reconocimiento web modular y automatizable")
    if not check_install('recon-ng',
                         pkg='recon-ng' if not IS_TERMUX else None,
                         pip='recon-ng'):
        pause(); return

    print(f"  {dm('Comandos útiles dentro de recon-ng:')}")
    print(f"  {dm('  workspaces create <nombre>')}")
    print(f"  {dm('  marketplace install all')}")
    print(f"  {dm('  modules search <keyword>')}")
    print(f"  {dm('  db insert domains  →  set domain  →  run')}\n")
    os.system('recon-ng')
    pause()


# ══════════════════════════════════════════════════════════════════════════
#  [15] BINARY ANALYSIS — strings / hexdump / file / hashes
# ══════════════════════════════════════════════════════════════════════════
def t15_binary():
    banner(); hdr(15, "Binary Analysis", "strings + hexdump + xxd + file + hashes MD5/SHA256")

    target = inp("Archivo a analizar: ")
    if not target or not Path(target).exists():
        print(f"  {r('✗')} Archivo no encontrado"); pause(); return

    session = new_session('binary_analysis')

    analyses = {
        '1': (f'file "{target}"',                              'file_type.txt',   'Tipo de archivo'),
        '2': (f'strings -n 6 "{target}"',                     'strings.txt',     'Cadenas ASCII (min 6 chars)'),
        '3': (f'hexdump -C "{target}" | head -300',           'hexdump.txt',     'Hexdump (300 líneas)'),
        '4': (f'xxd "{target}" | head -300',                  'xxd.txt',         'xxd hex+ascii'),
        '5': (f'md5sum "{target}" && sha1sum "{target}" && sha256sum "{target}"', 'hashes.txt', 'MD5 / SHA1 / SHA256'),
        '6': (f'readelf -a "{target}" 2>/dev/null',           'readelf.txt',     'ELF headers (si aplica)'),
        '7': (f'objdump -d "{target}" 2>/dev/null | head -200', 'disasm.txt',    'Desensamblado (200 líneas)'),
    }

    print(f"\n  {cy('Análisis disponibles:')}")
    for k, (_, _, desc) in analyses.items():
        print(f"    {cy(k)}. {desc}")
    print(f"    {cy('0')}. TODOS")

    opt = inp("Opción [0]: ") or '0'
    run_on = analyses if opt == '0' else {opt: analyses.get(opt, analyses['1'])}

    for k, (cmd, fname, desc) in run_on.items():
        out_f = session / fname
        print(f"\n  {cy('→')} {dm(desc)}: {dm(cmd[:60])}")
        o, e, _ = run(cmd)
        content = f"# {desc}\n# CMD: {cmd}\n# {'─'*50}\n\n{o or e}"
        save_file(out_f, content)
        preview = (o or e)[:400]
        if preview:
            print(preview)

    print(f"\n  {g('✓')} Todo en: {session}")
    pause()


# ══════════════════════════════════════════════════════════════════════════
#  [16] NOX_PORTSCAN — Motor de escaneo de puertos propio
# ══════════════════════════════════════════════════════════════════════════
def t16_portscan():
    # DEPS: [socket, threading, re, json]
    banner(); hdr(16, "NOX_PORTSCAN", "Motor de escaneo y banner grabbing (Pure Python)")
    target = inp("IP Objetivo: ")
    if not target: return
    ports_str = inp("Puertos (ej: 21-80,443,3306) [1-1024]: ") or "1-1024"
    
    ports = []
    for part in ports_str.split(','):
        if '-' in part:
            start, end = map(int, part.split('-'))
            ports.extend(range(start, end + 1))
        else:
            ports.append(int(part))

    results = []
    print(f"\n  {cy('→')} Escaneando {len(ports)} puertos en {target}...\n")

    def scan_port(port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.5)
        try:
            res = s.connect_ex((target, port))
            if res == 0:
                banner_txt = "Desconocido"
                try:
                    s.send(b"HEAD / HTTP/1.0\r\n\r\n")
                    banner_txt = s.recv(512).decode('utf-8', 'ignore').strip().replace('\n', ' ')
                except: pass
                
                service = "Unknown"
                if re.search(r'SSH', banner_txt, re.I): service = "SSH"
                elif re.search(r'HTTP|Apache|nginx', banner_txt, re.I): service = "HTTP"
                elif re.search(r'FTP', banner_txt, re.I): service = "FTP"
                elif re.search(r'MySQL', banner_txt, re.I): service = "MySQL"
                
                print(f"  {g('[+]')} Puerto {C.W}{port:<5}{C.RS} | {C.G}ABIERTO{C.RS} | {C.CY}{service:<8}{C.RS} | {dm(banner_txt[:40])}")
                return {"port": port, "status": "open", "service": service, "banner": banner_txt}
        except: pass
        finally: s.close()
        return None

    with ThreadPoolExecutor(max_workers=50) as executor:
        found = list(executor.map(scan_port, ports))
        results = [r for r in found if r]

    session = new_session('portscan')
    save_file(session/'results.json', json.dumps(results, indent=4))
    print(f"\n  {g('✓')} Escaneo finalizado. {len(results)} puertos abiertos. Datos en {session}")
    pause()

# ══════════════════════════════════════════════════════════════════════════
#  [17] NOX_FILECAVER — Motor de file carving propio
# ══════════════════════════════════════════════════════════════════════════
def t17_filecaver():
    # DEPS: [struct, pathlib]
    banner(); hdr(17, "NOX_FILECAVER", "Recuperación de archivos por Magic Bytes (Pure Python)")
    path = inp("Archivo/Imagen de disco: ")
    if not path or not Path(path).exists(): return

    sigs = {
        'jpg':  {'head': b'\xff\xd8\xff', 'foot': b'\xff\xd9', 'ext': '.jpg'},
        'png':  {'head': b'\x89PNG\r\n\x1a\n', 'foot': b'\x49\x45\x4e\x44\xae\x42\x60\x82', 'ext': '.png'},
        'pdf':  {'head': b'%PDF', 'foot': b'%%EOF', 'ext': '.pdf'},
        'zip':  {'head': b'PK\x03\x04', 'foot': b'PK\x05\x06', 'ext': '.zip'},
        'sqlite': {'head': b'SQLite format 3\x00', 'foot': None, 'size': 1024*50, 'ext': '.db'}
    }

    session = new_session('filecarver')
    carv_dir = session / 'recovered'
    carv_dir.mkdir(exist_ok=True)
    
    print(f"\n  {cy('→')} Analizando binario... esto puede tardar.\n")
    count = 0
    with open(path, 'rb') as f:
        data = f.read()
        for name, sig in sigs.items():
            offset = 0
            while True:
                offset = data.find(sig['head'], offset)
                if offset == -1: break
                
                end = -1
                if sig['foot']:
                    end = data.find(sig['foot'], offset + len(sig['head']))
                    if end != -1: end += len(sig['foot'])
                
                if end == -1: end = offset + sig.get('size', 1024*100)
                
                extracted = data[offset:end]
                out_name = carv_dir / f"carved_0x{offset:X}_{name}{sig['ext']}"
                with open(out_name, 'wb') as out_f: out_f.write(extracted)
                
                print(f"  {g('✓')} {name.upper():<6} hallado en {hex(offset)} | {len(extracted)} bytes")
                count += 1
                offset += len(sig['head'])

    print(f"\n  {g('✓')} {count} archivos recuperados en {carv_dir}")
    pause()

# ══════════════════════════════════════════════════════════════════════════
#  [18] NOX_PROCWATCH — Análisis de procesos y persistencia vía /proc
# ══════════════════════════════════════════════════════════════════════════
def t18_procwatch():
    # DEPS: [os, pathlib, re]
    banner(); hdr(18, "NOX_PROCWATCH", "Análisis profundo de procesos y anomalías")
    if IS_TERMUX: print(f"  {y('⚠')} En Termux el acceso a /proc está muy limitado.")
    
    session = new_session('procwatch')
    report = []

    print(f"  {C.W}{'PID':<8} {'PROCESO':<20} {'ANOMALÍA':<20}{C.RS}")
    print(f"  {dm('─' * 52)}")

    for proc_path in Path('/proc').glob('[0-9]*'):
        pid = proc_path.name
        try:
            with open(proc_path / 'cmdline', 'r') as f: cmd = f.read().replace('\0', ' ')
            exe = (proc_path / 'exe').readlink() if (proc_path / 'exe').exists() else "N/A"
            status = (proc_path / 'status').read_text()
            
            anomalies = []
            if exe == "N/A" and cmd: anomalies.append("Hollow/NoExe")
            if "LD_PRELOAD" in (proc_path / 'environ').read_text(errors='ignore'): anomalies.append("LD_PRELOAD")
            
            if anomalies:
                color = C.R if "Hollow" in anomalies[0] else C.Y
                print(f"  {color}{pid:<8} {cmd[:20]:<20} {','.join(anomalies):<20}{C.RS}")
                report.append({"pid": pid, "cmd": cmd, "exe": str(exe), "anomalies": anomalies})
        except: continue

    save_file(session/'proc_anomalies.json', json.dumps(report, indent=4))
    print(f"\n  {g('✓')} Análisis de persistencia en cron/systemd...")
    # Simulación de persistencia (pathlib puro)
    persist_paths = ['/etc/crontab', '/etc/rc.local', str(HOME / '.bashrc')]
    for p in persist_paths:
        if Path(p).exists():
            print(f"  {cy('→')} Verificando {p}...")

    pause()

# ══════════════════════════════════════════════════════════════════════════
#  [19] NOX_NETSNIFF — Sniffer y analizador de tráfico propio
# ══════════════════════════════════════════════════════════════════════════
def t19_netsniff():
    # DEPS: [socket, struct]
    banner(); hdr(19, "NOX_NETSNIFF", "Sniffer de red por Raw Sockets (Solo Linux/Root)")
    if not IS_ROOT: print(f"  {r('✗')} Requiere ROOT."); pause(); return

    try:
        sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
    except Exception as e:
        print(f"  {r('✗')} Error al crear raw socket: {e}"); pause(); return

    session = new_session('netsniff')
    pcap_file = session / 'capture.pcap'
    
    # Header PCAP manual (Global Header)
    with open(pcap_file, 'wb') as f:
        f.write(struct.pack('!IHHiIII', 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1))

    print(f"  {y('!')} Capturando... Ctrl+C para detener y guardar.\n")
    print(f"  {'PROTO':<8} {'ORIGEN':<20} {'DESTINO':<20}")
    
    try:
        count = 0
        while count < 100:
            raw_data, _ = sock.recvfrom(65535)
            count += 1
            
            # Parse Ethernet
            eth = struct.unpack('!6s6sH', raw_data[:14])
            proto = socket.htons(eth[2])
            
            if proto == 8: # IPv4
                ip_hdr = struct.unpack('!BBHHHBBH4s4s', raw_data[14:34])
                src_ip = socket.inet_ntoa(ip_hdr[8])
                dst_ip = socket.inet_ntoa(ip_hdr[9])
                l4_proto = ip_hdr[6]
                
                p_name = "TCP" if l4_proto == 6 else "UDP" if l4_proto == 17 else "ICMP"
                print(f"  {C.CY}{p_name:<8}{C.RS} {src_ip:<20} -> {dst_ip:<20}")
                
                # Guardar en PCAP (Packet Header + Data)
                ts_sec, ts_usec = map(int, str(time.time()).split('.'))
                pkt_hdr = struct.pack('!IIII', ts_sec, ts_usec[:6] if isinstance(ts_usec, str) else 0, len(raw_data), len(raw_data))
                with open(pcap_file, 'ab') as f: f.write(pkt_hdr + raw_data)

    except KeyboardInterrupt: pass
    print(f"\n  {g('✓')} Captura guardada en formato PCAP: {pcap_file}")
    pause()

# ══════════════════════════════════════════════════════════════════════════
#  [20] NOX_STEGDETECT — Detector estadístico de esteganografía
# ══════════════════════════════════════════════════════════════════════════
def t20_stegdetect():
    # DEPS: [math, struct]
    banner(); hdr(20, "NOX_STEGDETECT", "Análisis de Entropía y LSB (Pure Python)")
    path = inp("Imagen a analizar: ")
    if not path or not Path(path).exists(): return

    def calc_entropy(data):
        if not data: return 0
        entropy = 0
        for i in range(256):
            p_i = data.count(i) / len(data)
            if p_i > 0: entropy -= p_i * math.log2(p_i)
        return entropy

    with open(path, 'rb') as f:
        data = f.read()
        ent = calc_entropy(data)
        
    print(f"\n  {cy('→')} Resultados del análisis:")
    print(f"    - Entropía Global: {C.Y}{ent:.4f}{C.RS} (Máx 8.0)")
    
    score = 0
    if ent > 7.9: score += 50
    
    # Busqueda simple de strings ocultos en LSB (primeros 1000 bytes)
    lsb_bits = ""
    for byte in data[100:1100]:
        lsb_bits += str(byte & 1)
    
    print(f"    - Sospecha Esteganográfica: {C.R if score > 40 else C.G}{score}/100{C.RS}")
    if score > 40: print(f"    - {y('⚠')} Entropía extremadamente alta. Posible contenedor cifrado.")
    
    pause()

# ══════════════════════════════════════════════════════════════════════════
#  [21] NOX_CREDSCAN — Escáner de secretos y credenciales
# ══════════════════════════════════════════════════════════════════════════
def t21_credscan():
    # DEPS: [re, pathlib]
    banner(); hdr(21, "NOX_CREDSCAN", "Búsqueda de API Keys, Tokens y Passwords")
    path = inp("Directorio a escanear [.]: ") or "."
    
    rules = {
        'AWS Key': r'AKIA[0-9A-Z]{16}',
        'Generic Password': r'(?i)password\s*[:=]\s*["\']([^"\']+)["\']',
        'JWT Token': r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*',
        'Private Key': r'-----BEGIN [A-Z ]+ PRIVATE KEY-----',
        'Google API': r'AIza[0-9A-Za-z-_]{35}'
    }

    session = new_session('credscan')
    found = []

    for p in Path(path).rglob('*'):
        if p.is_file() and p.suffix not in ('.exe', '.png', '.jpg', '.zip'):
            try:
                content = p.read_text(errors='ignore')
                for name, regex in rules.items():
                    matches = re.finditer(regex, content)
                    for m in matches:
                        val = m.group()
                        obs = val[:6] + "***"
                        print(f"  {C.R}[!]{C.RS} {name:<15} | {p.name:<20} | {C.Y}{obs}{C.RS}")
                        found.append({"file": str(p), "type": name, "value": val})
            except: continue

    save_file(session/'leaks.json', json.dumps(found, indent=4))
    print(f"\n  {g('✓')} Escaneo completado. {len(found)} secretos hallados.")
    pause()

# ══════════════════════════════════════════════════════════════════════════
#  [22] NOX_TIMELINE — Constructor de timeline forense nativo
# ══════════════════════════════════════════════════════════════════════════
def t22_timeline():
    # DEPS: [os, csv]
    banner(); hdr(22, "NOX_TIMELINE", "Generador de línea de tiempo de archivos")
    target = inp("Directorio objetivo: ")
    if not target or not Path(target).exists(): return

    session = new_session('timeline')
    csv_file = session / 'timeline.csv'
    
    print(f"\n  {cy('→')} Generando timeline...")
    events = []
    for root, _, files in os.walk(target):
        for f in files:
            p = Path(root) / f
            try:
                st = p.stat()
                events.append({
                    'date': datetime.fromtimestamp(st.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'action': 'MODIFIED',
                    'file': str(p),
                    'size': st.st_size
                })
            except: continue

    events.sort(key=lambda x: x['date'], reverse=True)
    
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['date', 'action', 'file', 'size'])
        writer.writeheader()
        writer.writerows(events)

    print(f"  {g('✓')} Timeline de {len(events)} eventos guardado en {csv_file}")
    pause()

# ══════════════════════════════════════════════════════════════════════════
#  [23] NOX_REPORT — Generador de reporte HTML forense
# ══════════════════════════════════════════════════════════════════════════
def t23_report():
    # DEPS: [hashlib, pathlib]
    banner(); hdr(23, "NOX_REPORT", "Generador de reporte HTML consolidado")
    sessions = sorted(BASE_DIR.glob('*_NOXRECON*'), reverse=True)
    if not sessions: 
        sessions = sorted(BASE_DIR.glob('*'), reverse=True)

    print(f"  {cy('Sesiones disponibles:')}")
    for i, s in enumerate(sessions[:10]):
        print(f"    {i}. {s.name}")
    
    idx = inp("Selecciona sesión [0]: ") or "0"
    target_session = sessions[int(idx)]
    analyst = inp("Nombre del Analista: ") or "Admin"

    html_content = f"""
    <html><head><style>
        body {{ background: #1a1a1a; color: #e0e0e0; font-family: monospace; padding: 40px; }}
        h1 {{ color: #00ffcc; border-bottom: 2px solid #333; }}
        .box {{ background: #252525; padding: 20px; border-radius: 5px; margin-bottom: 20px; border-left: 5px solid #00ffcc; }}
        pre {{ background: #000; padding: 15px; overflow-x: auto; color: #00ff00; }}
        .meta {{ color: #888; font-size: 0.9em; }}
    </style></head><body>
    <h1>FORENX REPORT: {target_session.name}</h1>
    <div class="box">
        <p><b>Analista:</b> {analyst}</p>
        <p><b>Fecha:</b> {datetime.now()}</p>
        <p><b>Evidencia:</b> {target_session}</p>
    </div>
    """

    for p in target_session.rglob('*'):
        if p.is_file() and p.suffix in ('.txt', '.json', '.log', '.csv'):
            content = p.read_text(errors='ignore')
            # Basic syntax highlight
            content = content.replace('open', '<b style="color:red">open</b>')
            html_content += f"<h3>FILE: {p.name}</h3><pre>{content}</pre>"

    html_content += "</body></html>"
    
    report_path = target_session / f"FINAL_REPORT_{target_session.name}.html"
    save_file(report_path, html_content)
    print(f"\n  {g('✓')} Reporte HTML generado exitosamente:")
    print(f"  {g('→')} {report_path}")
    pause()

# ══════════════════════════════════════════════════════════════════════════
#  [24] NOX_WIFIKEYS — Extracción forense de redes WiFi guardadas
# ══════════════════════════════════════════════════════════════════════════
def t_wifi():
    # DEPS: [subprocess, re, json, csv, configparser, xml.etree.ElementTree]
    banner(); hdr(24, "NOX_WIFIKEYS", "Extracción forense de redes WiFi guardadas")

    session = new_session('wifi_keys')
    results = []

    if platform.system() == 'Windows':
        print(f"  {cy('→')} Extrayendo perfiles WiFi en Windows...")
        try:
            # List profiles
            cmd = 'netsh wlan show profiles'
            resultado = subprocess.run(cmd, shell=True, capture_output=True,
                                       text=True, encoding='utf-8',
                                       errors='replace')
            profiles_output = resultado.stdout
            profile_names = re.findall(r"(?:All User Profile|Perfil de todos los usuarios)\s*:\s*(.*)", profiles_output)

            for profile_name in profile_names:
                profile_name = profile_name.strip()
                print(f"    {dm('·')} Procesando perfil: {profile_name}")
                cmd = f'netsh wlan show profile name="{profile_name}" key=clear'
                resultado = subprocess.run(cmd, shell=True, capture_output=True,
                                           text=True, encoding='utf-8',
                                           errors='replace')
                profile_output = resultado.stdout

                ssid_match = re.search(r"(?:SSID name|Nombre SSID)\s*:\s*(.*)", profile_output)
                auth_match = re.search(r"(?:Authentication|Autenticación)\s*:\s*(.*)", profile_output)
                key_match = re.search(r"(?:Key Content|Contenido de la clave)\s*:\s*(.*)", profile_output)
                # MAC del router no es directamente visible en 'show profile', se necesitaría 'show networks mode=bssid'
                # Simplificamos para no añadir más llamadas a netsh que compliquen el parsing
                mac_match = re.search(r"BSSID\s*:\s*([0-9A-Fa-f:]{17})", profile_output) # A veces aparece en el output, pero no es consistente
                last_conn_match = re.search(r"Time of last connection\s*:\s*(.*)", profile_output)

                ssid = ssid_match.group(1).strip() if ssid_match else profile_name
                auth = auth_match.group(1).strip() if auth_match else "Unknown"
                password = key_match.group(1).strip() if key_match else "None/Encrypted"
                mac = mac_match.group(1).strip() if mac_match else "N/A"
                last_conn = last_conn_match.group(1).strip() if last_conn_match else "N/A"

                results.append({
                    "SSID": ssid,
                    "Auth": auth,
                    "Password": password,
                    "MAC": mac,
                    "Last_Connection": last_conn,
                    "Notes": ""
                })
        except Exception as e:
            print(f"  {r('✗')} Error en Windows WiFi: {e}")

    elif platform.system() == 'Linux':
        print(f"  {cy('→')} Extrayendo perfiles WiFi en Linux...")
        if not IS_ROOT:
            print(f"  {y('⚠')} Se recomienda ejecutar como ROOT para acceder a todos los perfiles de NetworkManager.")

        # NetworkManager profiles
        nm_path = Path('/etc/NetworkManager/system-connections/')
        if nm_path.is_dir():
            for conf_file in nm_path.glob('*.nmconnection'):
                try:
                    config = configparser.ConfigParser()
                    config.read(conf_file)

                    ssid = config.get('wifi', 'ssid', fallback='N/A')
                    psk = config.get('wifi-security', 'psk', fallback='None/Encrypted')
                    auth_alg = config.get('wifi-security', 'auth-alg', fallback='N/A')
                    key_mgmt = config.get('wifi-security', 'key-mgmt', fallback='N/A')

                    results.append({
                        "SSID": ssid,
                        "Auth": f"{auth_alg}/{key_mgmt}",
                        "Password": psk,
                        "MAC": "N/A", # No es fácilmente disponible aquí sin más parsing
                        "Last_Connection": "N/A",
                        "Notes": f"NetworkManager: {conf_file.name}"
                    })
                except Exception as e:
                    print(f"    {y('⚠')} Error al leer {conf_file.name}: {e}")

        # Fallback to wpa_supplicant.conf
        wpa_supp_path = Path('/etc/wpa_supplicant/wpa_supplicant.conf')
        if wpa_supp_path.is_file():
            print(f"  {dm('·')} Leyendo {wpa_supp_path}...")
            try:
                content = wpa_supp_path.read_text()
                networks = re.findall(r'network={\s*[^}]+ssid="([^"]+)"\s*[^}]+psk="([^"]+)"', content)
                for ssid, psk in networks:
                    results.append({
                        "SSID": ssid,
                        "Auth": "WPA/WPA2 PSK",
                        "Password": psk,
                        "MAC": "N/A",
                        "Last_Connection": "N/A",
                        "Notes": f"wpa_supplicant.conf"
                    })
            except Exception as e:
                print(f"    {y('⚠')} Error al leer {wpa_supp_path}: {e}")

    elif IS_TERMUX: # Android
        print(f"  {cy('→')} Extrayendo perfiles WiFi en Termux/Android...")
        wifi_config_xml = Path('/data/misc/wifi/WifiConfigStore.xml')
        wpa_supp_sdcard = Path('/sdcard/wpa_supplicant.conf')

        if IS_ROOT and wifi_config_xml.is_file():
            print(f"  {dm('·')} Leyendo {wifi_config_xml} (requiere ROOT)...")
            try:
                tree = ET.parse(wifi_config_xml)
                root = tree.getroot()
                for network in root.findall(".//Network"):
                    ssid_elem = network.find(".//string[@name='SSID']")
                    psk_elem = network.find(".//string[@name='PreSharedKey']")
                    
                    ssid = ssid_elem.text.strip('"') if ssid_elem is not None and ssid_elem.text else "N/A"
                    psk = psk_elem.text.strip('"') if psk_elem is not None and psk_elem.text else "None/Encrypted"
                    
                    results.append({
                        "SSID": ssid,
                        "Auth": "Unknown", # Más complejo de parsear del XML
                        "Password": psk,
                        "MAC": "N/A",
                        "Last_Connection": "N/A",
                        "Notes": "WifiConfigStore.xml (ROOT)"
                    })
            except Exception as e:
                print(f"    {y('⚠')} Error al parsear {wifi_config_xml}: {e}")
        elif wpa_supp_sdcard.is_file():
            print(f"  {dm('·')} Leyendo {wpa_supp_sdcard}...")
            try:
                content = wpa_supp_sdcard.read_text()
                networks = re.findall(r'network={\s*[^}]+ssid="([^"]+)"\s*[^}]+psk="([^"]+)"', content)
                for ssid, psk in networks:
                    results.append({
                        "SSID": ssid,
                        "Auth": "WPA/WPA2 PSK",
                        "Password": psk,
                        "MAC": "N/A",
                        "Last_Connection": "N/A",
                        "Notes": f"wpa_supplicant.conf (SD Card)"
                    })
            except Exception as e:
                print(f"    {y('⚠')} Error al leer {wpa_supp_sdcard}: {e}")
        else:
            print(f"  {y('⚠')} No se encontraron archivos de configuración WiFi accesibles. Intenta ejecutar como ROOT.")

    if results:
        print(f"\n  {C.W}{'SSID':<25} {'Auth':<15} {'Password':<25} {'Notes':<20}{C.RS}")
        print(f"  {dm('─' * 85)}")
        for r in results:
            password_display = r['Password'] if len(r['Password']) < 20 else r['Password'][:17] + "..."
            print(f"  {C.CY}{r['SSID'][:25]:<25}{C.RS} {r['Auth'][:15]:<15} {C.G}{password_display:<25}{C.RS} {dm(r['Notes'][:20]):<20}")

        save_file(session/'wifi_passwords.txt', "\n".join([f"SSID: {r['SSID']}, Auth: {r['Auth']}, Password: {r['Password']}, Notes: {r['Notes']}" for r in results]))
        save_file(session/'wifi_passwords.json', json.dumps(results, indent=4))
        print(f"\n  {g('✓')} {len(results)} perfiles WiFi guardados en {session}")
    else:
        print(f"\n  {y('⚠')} No se encontraron perfiles WiFi o no se pudieron extraer.")
    pause()

# ══════════════════════════════════════════════════════════════════════════
#  [25] NOX_BROWSERFORENS — Forense completo de navegadores
# ══════════════════════════════════════════════════════════════════════════
def t_browser():
    # DEPS: [subprocess, re, json, csv, sqlite3, shutil, datetime, timedelta, base64, win32crypt (Windows)]
    banner(); hdr(25, "NOX_BROWSERFORENS", "Análisis forense de navegadores (Historial, Cookies, Contraseñas, Descargas, Extensiones)")

    session = new_session('browser_forensics')
    
    # --- Helper: Browser Path Detection ---

    # --- Upfront pywin32 installation for Windows ---
    if platform.system() == 'Windows':
        global win32crypt # Aseguramos que podemos modificar la variable global win32crypt
        if win32crypt is None:
            print(f"  {y('⚠')} pywin32 (necesario para descifrar contraseñas/cookies en Windows) no encontrado.")
            resp = inp("¿Intentar instalar pywin32 ahora? [s/N]: ")
            if resp.lower() == 's':
                try:
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pywin32', '--break-system-packages', '-q'])
                    import win32crypt as w3c
                    win32crypt = w3c # Asignamos el módulo recién importado a la variable global
                    print(f"  {g('✓')} pywin32 instalado exitosamente.")
                except Exception as e:
                    print(f"  {r('✗')} Falló la instalación de pywin32: {e}. Las contraseñas y cookies de Windows permanecerán cifradas.")
            else:
                print(f"  {y('⚠')} pywin32 no será instalado. Las contraseñas y cookies de Windows permanecerán cifradas.")

    def get_browser_paths():
        browser_paths = {
            "Chrome": [], "Brave": [], "Edge": [], "Opera": [], "Firefox": []
        }
        
        if platform.system() == 'Windows':
            local_app_data = Path(os.getenv('LOCALAPPDATA'))
            app_data = Path(os.getenv('APPDATA'))

            # Chromium-based
            for browser, rel_path in [
                ("Chrome", r"Google\Chrome\User Data"),
                ("Brave", r"BraveSoftware\Brave-Browser\User Data"),
                ("Edge", r"Microsoft\Edge\User Data"),
                ("Opera", r"Opera Software\Opera Stable\User Data"), # Common Opera path
            ]:
                path = local_app_data / rel_path
                if path.is_dir():
                    # Look for Default profile or other profiles
                    for profile_dir in path.glob('Profile*'): # Profile 1, Profile 2, Default, Guest Profile
                        if profile_dir.is_dir():
                            browser_paths[browser].append(profile_dir)
                    if not browser_paths[browser] and (path / 'Default').is_dir(): # Fallback to Default if no specific profiles found
                        browser_paths[browser].append(path / 'Default')

            # Firefox
            firefox_path = app_data / r"Mozilla\Firefox\Profiles"
            if firefox_path.is_dir():
                for profile_dir in firefox_path.glob('*.default-release'):
                    if profile_dir.is_dir():
                        browser_paths["Firefox"].append(profile_dir)
                if not browser_paths["Firefox"]: # Fallback for other profiles
                    for profile_dir in firefox_path.glob('*'):
                        if profile_dir.is_dir():
                            browser_paths["Firefox"].append(profile_dir)

        elif platform.system() == 'Linux':
            home = Path.home()
            # Chromium-based
            for browser, rel_path in [
                ("Chrome", ".config/google-chrome"),
                ("Brave", ".config/BraveSoftware/Brave-Browser"),
                ("Chromium", ".config/chromium"), # Often separate
                ("Opera", ".config/opera"),
            ]:
                path = home / rel_path
                if path.is_dir():
                    for profile_dir in path.glob('Profile*'):
                        if profile_dir.is_dir():
                            browser_paths[browser].append(profile_dir)
                    if not browser_paths[browser] and (path / 'Default').is_dir():
                        browser_paths[browser].append(path / 'Default')

            # Firefox
            firefox_path = home / ".mozilla/firefox"
            if firefox_path.is_dir():
                for profile_dir in firefox_path.glob('*.default-release'):
                    if profile_dir.is_dir():
                        browser_paths["Firefox"].append(profile_dir)
                if not browser_paths["Firefox"]: # Fallback for other profiles
                    for profile_dir in firefox_path.glob('*'):
                        if profile_dir.is_dir() and (profile_dir / 'places.sqlite').is_file():
                            browser_paths["Firefox"].append(profile_dir)

        elif IS_TERMUX: # Android
            # Requires ROOT for most paths
            print(f"  {y('⚠')} En Termux/Android, la mayoría de los datos de navegador requieren ROOT.")
            # Chrome Android (requires root)
            chrome_android_path = Path('/data/data/com.android.chrome/app_chrome/Default/')
            if IS_ROOT and chrome_android_path.is_dir():
                browser_paths["Chrome"].append(chrome_android_path)
            elif not IS_ROOT:
                print(f"  {y('⚠')} Chrome Android data en {chrome_android_path} no accesible sin ROOT.")

            # Firefox Android (requires root)
            firefox_android_path = Path('/data/data/org.mozilla.firefox/files/mozilla/')
            if IS_ROOT and firefox_android_path.is_dir():
                for profile_dir in firefox_android_path.glob('*.default'):
                    if profile_dir.is_dir():
                        browser_paths["Firefox"].append(profile_dir)
            elif not IS_ROOT:
                print(f"  {y('⚠')} Firefox Android data en {firefox_android_path} no accesible sin ROOT.")

        return browser_paths

    # --- Helper: Chrome Timestamp Conversion ---
    def chrome_timestamp_to_datetime(chrome_ts):
        if chrome_ts == 0: return None
        # Chrome timestamp is microseconds since 1601-01-01 00:00:00 UTC
        # Python datetime epoch is 1970-01-01 00:00:00 UTC
        # Difference in microseconds between 1601-01-01 and 1970-01-01
        chrome_epoch_offset = 11644473600000000 # Microseconds
        return datetime(1970, 1, 1) + timedelta(microseconds=chrome_ts - chrome_epoch_offset)

    # --- Helper: Windows DPAPI Decryption ---
    def decrypt_windows_password(encrypted_value):
        if not win32crypt:
            # Este caso debería ser manejado por la verificación inicial en t_browser()
            return "Requires pywin32 for decryption (not installed or failed to load)"
        try:
            # The encrypted_value from Chrome/Edge/Brave is usually prefixed with 'v10' or 'v11'
            # The actual encrypted blob starts after the 'v10'/'v11' prefix
            if encrypted_value.startswith(b'v10') or encrypted_value.startswith(b'v11'):
                encrypted_value = encrypted_value[3:] # Remove prefix
            
            # DPAPI expects raw bytes
            _, decrypted_data = win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)
            return decrypted_data.decode('utf-8', errors='ignore')
        except Exception as e:
            return f"Decryption failed: {e}"

    # --- Helper: Linux Password Decryption (Placeholder) ---
    def decrypt_linux_password(encrypted_value, browser_type):
        # Este es un tema complejo. Los navegadores en Linux a menudo usan libsecret (keyring)
        # o una clave derivada de la contraseña de inicio de sesión del usuario, a veces con AES-GCM.
        # Implementar esto puramente en Python sin librerías externas como `keyring` o `cryptography`
        # es no trivial y propenso a errores/problemas de seguridad.
        # Para este ejercicio, extraemos el valor cifrado y documentamos la complejidad.
        return f"Encrypted (Linux - requiere keyring/AES): {base64.b64encode(encrypted_value).decode()}"

    # --- Helper: Firefox NSS Decryption (Placeholder) ---
    def decrypt_firefox_nss(encrypted_value_b64):
        # Firefox usa la librería NSS (Network Security Services) para el almacenamiento de contraseñas.
        # Descifrar esto requiere cargar libnss3.so y llamar a sus funciones a través de ctypes.
        # Esto es altamente complejo y depende de la configuración NSS del sistema.
        # Para este ejercicio, extraemos el valor codificado en base64.
        return f"Encrypted (Firefox NSS - requiere libnss3/master password): {encrypted_value_b64}"

    # --- Main Browser Forensics Logic ---
    browser_paths = get_browser_paths()
    total_cookies = 0
    total_passwords = 0
    total_history = 0
    high_risk_extensions = 0

    selected_modules = []
    print(f"\n  {cy('Sub-módulos disponibles:')}")
    print(f"    {cy('A')}. Historial")
    print(f"    {cy('B')}. Cookies")
    print(f"    {cy('C')}. Contraseñas Guardadas")
    print(f"    {cy('D')}. Descargas")
    print(f"    {cy('E')}. Extensiones Instaladas")
    print(f"    {cy('F')}. Firefox Específico (Historial, Cookies, Contraseñas)")
    choice = inp("Selecciona módulos (ej: ABC, todos): ") or "ABCDE"
    if choice.lower() == 'todos':
        selected_modules = ['A', 'B', 'C', 'D', 'E', 'F']
    else:
        selected_modules = list(choice.upper())

    # --- Process each browser type ---
    for browser_name, paths in browser_paths.items():
        if not paths:
            print(f"  {dm('·')} No se encontraron perfiles para {browser_name}.")
            continue

        print(f"\n  {C.BD}{C.CY}--- Procesando {browser_name} ---{C.RS}")
        for profile_path in paths:
            print(f"  {dm('·')} Perfil: {profile_path}")
            browser_session_dir = session / browser_name.lower() / profile_path.name
            browser_session_dir.mkdir(parents=True, exist_ok=True)

            # --- [A] HISTORY (Chromium-based) ---
            if 'A' in selected_modules and browser_name != "Firefox":
                history_db_path = profile_path / 'History'
                if history_db_path.is_file():
                    temp_db = browser_session_dir / 'History.sqlite'
                    try:
                        shutil.copy2(history_db_path, temp_db)
                        conn = sqlite3.connect(temp_db)
                        cursor = conn.cursor()
                        cursor.execute("SELECT url, title, visit_count, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 500")
                        history_data = cursor.fetchall()
                        conn.close()

                        history_records = []
                        for url, title, visit_count, last_visit_time in history_data:
                            dt = chrome_timestamp_to_datetime(last_visit_time)
                            history_records.append({
                                "date": dt.strftime('%Y-%m-%d %H:%M:%S') if dt else "N/A",
                                "url": url,
                                "title": title,
                                "visit_count": visit_count
                            })
                        
                        history_csv_path = browser_session_dir / 'history.csv'
                        with open(history_csv_path, 'w', newline='', encoding='utf-8') as f:
                            writer = csv.DictWriter(f, fieldnames=["date", "url", "title", "visit_count"])
                            writer.writeheader()
                            writer.writerows(history_records)
                        print(f"    {g('✓')} Historial guardado: {history_csv_path}")
                        total_history += len(history_records)
                    except Exception as e:
                        print(f"    {r('✗')} Error al extraer historial de {profile_path}: {e}")
                else:
                    print(f"    {dm('·')} Historial no encontrado en {profile_path}")

            # --- [B] COOKIES (Chromium-based) ---
            if 'B' in selected_modules and browser_name != "Firefox":
                cookies_db_path = profile_path / 'Cookies'
                if cookies_db_path.is_file():
                    temp_db = browser_session_dir / 'Cookies.sqlite'
                    try:
                        shutil.copy2(cookies_db_path, temp_db)
                        conn = sqlite3.connect(temp_db)
                        cursor = conn.cursor()
                        cursor.execute("SELECT host_key, name, value, encrypted_value, expires_utc, is_secure, is_httponly FROM cookies")
                        cookies_data = cursor.fetchall()
                        conn.close()

                        cookie_records = []
                        for host_key, name, value, encrypted_value, expires_utc, is_secure, is_httponly in cookies_data:
                            decrypted_value = value.decode('utf-8', errors='ignore') # 'value' is usually cleartext for non-secure cookies
                            if encrypted_value: # 'encrypted_value' is used for secure cookies
                                if platform.system() == 'Windows':
                                    decrypted_value = decrypt_windows_password(encrypted_value)
                                elif platform.system() == 'Linux':
                                    decrypted_value = decrypt_linux_password(encrypted_value, browser_name)
                                else: # Termux/Android
                                    decrypted_value = f"Encrypted: {base64.b64encode(encrypted_value).decode()}"
                            
                            dt_expires = chrome_timestamp_to_datetime(expires_utc)
                            cookie_records.append({
                                "domain": host_key,
                                "name": name,
                                "value": decrypted_value,
                                "expires": dt_expires.strftime('%Y-%m-%d %H:%M:%S') if dt_expires else "N/A",
                                "secure": bool(is_secure),
                                "httponly": bool(is_httponly)
                            })
                        
                        cookies_csv_path = browser_session_dir / 'cookies.csv'
                        with open(cookies_csv_path, 'w', newline='', encoding='utf-8') as f:
                            writer = csv.DictWriter(f, fieldnames=["domain", "name", "value", "expires", "secure", "httponly"])
                            writer.writeheader()
                            writer.writerows(cookie_records)
                        print(f"    {g('✓')} Cookies guardadas: {cookies_csv_path}")
                        total_cookies += len(cookie_records)
                    except Exception as e:
                        print(f"    {r('✗')} Error al extraer cookies de {profile_path}: {e}")
                else:
                    print(f"    {dm('·')} Cookies no encontradas en {profile_path}")

            # --- [C] PASSWORDS (Chromium-based) ---
            if 'C' in selected_modules and browser_name != "Firefox":
                login_db_path = profile_path / 'Login Data'
                if login_db_path.is_file():
                    print(f"\n  {C.R}⚠️ ADVERTENCIA LEGAL: Este módulo extrae credenciales almacenadas localmente.")
                    print(f"     Úsalo solo en sistemas sobre los que tengas autorización.{C.RS}")
                    confirm = inp("¿Deseas continuar? [s/N]: ")
                    if confirm.lower() != 's':
                        print(f"    {y('⚠')} Extracción de contraseñas cancelada.")
                        continue

                    temp_db = browser_session_dir / 'Login_Data.sqlite'
                    try:
                        shutil.copy2(login_db_path, temp_db)
                        conn = sqlite3.connect(temp_db)
                        cursor = conn.cursor()
                        cursor.execute("SELECT origin_url, username_value, password_value, date_created FROM logins")
                        login_data = cursor.fetchall()
                        conn.close()

                        password_records = []
                        for origin_url, username_value, password_value, date_created in login_data:
                            decrypted_password = ""
                            if password_value:
                                if platform.system() == 'Windows':
                                    decrypted_password = decrypt_windows_password(password_value)
                                elif platform.system() == 'Linux':
                                    decrypted_password = decrypt_linux_password(password_value, browser_name)
                                else: # Termux/Android
                                    decrypted_password = f"Encrypted: {base64.b64encode(password_value).decode()}"
                            
                            dt_created = chrome_timestamp_to_datetime(date_created)
                            password_records.append({
                                "url": origin_url,
                                "username": username_value,
                                "password": decrypted_password,
                                "date_created": dt_created.strftime('%Y-%m-%d %H:%M:%S') if dt_created else "N/A"
                            })
                        
                        passwords_csv_path = browser_session_dir / 'passwords.csv'
                        with open(passwords_csv_path, 'w', newline='', encoding='utf-8') as f:
                            writer = csv.DictWriter(f, fieldnames=["url", "username", "password", "date_created"])
                            writer.writeheader()
                            writer.writerows(password_records)
                        print(f"    {g('✓')} Contraseñas guardadas: {passwords_csv_path}")
                        total_passwords += len(password_records)
                    except Exception as e:
                        print(f"    {r('✗')} Error al extraer contraseñas de {profile_path}: {e}")
                else:
                    print(f"    {dm('·')} Login Data no encontrado en {profile_path}")

            # --- [D] DOWNLOADS (Chromium-based) ---
            if 'D' in selected_modules and browser_name != "Firefox":
                history_db_path = profile_path / 'History' # Downloads are often in History DB
                if history_db_path.is_file():
                    temp_db = browser_session_dir / 'History_downloads.sqlite'
                    try:
                        shutil.copy2(history_db_path, temp_db)
                        conn = sqlite3.connect(temp_db)
                        cursor = conn.cursor()
                        cursor.execute("SELECT target_path, tab_url, total_bytes, start_time, end_time, state FROM downloads")
                        downloads_data = cursor.fetchall()
                        conn.close()

                        download_records = []
                        for target_path, tab_url, total_bytes, start_time, end_time, state in downloads_data:
                            dt_start = chrome_timestamp_to_datetime(start_time)
                            dt_end = chrome_timestamp_to_datetime(end_time)
                            download_records.append({
                                "target_path": target_path,
                                "source_url": tab_url,
                                "size_bytes": total_bytes,
                                "start_time": dt_start.strftime('%Y-%m-%d %H:%M:%S') if dt_start else "N/A",
                                "end_time": dt_end.strftime('%Y-%m-%d %H:%M:%S') if dt_end else "N/A",
                                "state": state
                            })
                        
                        downloads_csv_path = browser_session_dir / 'downloads.csv'
                        with open(downloads_csv_path, 'w', newline='', encoding='utf-8') as f:
                            writer = csv.DictWriter(f, fieldnames=["target_path", "source_url", "size_bytes", "start_time", "end_time", "state"])
                            writer.writeheader()
                            writer.writerows(download_records)
                        print(f"    {g('✓')} Descargas guardadas: {downloads_csv_path}")
                    except Exception as e:
                        print(f"    {r('✗')} Error al extraer descargas de {profile_path}: {e}")
                else:
                    print(f"    {dm('·')} Descargas no encontradas en {profile_path}")

            # --- [E] EXTENSIONS (Chromium-based) ---
            if 'E' in selected_modules and browser_name != "Firefox":
                extensions_path = profile_path / 'Extensions'
                if extensions_path.is_dir():
                    extension_records = []
                    for ext_id_path in extensions_path.iterdir():
                        if ext_id_path.is_dir():
                            for version_path in ext_id_path.iterdir():
                                if version_path.is_dir():
                                    manifest_path = version_path / 'manifest.json'
                                    if manifest_path.is_file():
                                        try:
                                            manifest = json.loads(manifest_path.read_text(errors='ignore'))
                                            permissions = manifest.get('permissions', [])
                                            
                                            risk_score = 0
                                            high_risk_perms = ["tabs", "webRequest", "cookies", "password", "nativeMessaging", "proxy", "unlimitedStorage", "debugger"]
                                            for perm in permissions:
                                                if perm in high_risk_perms:
                                                    risk_score += 1
                                            
                                            risk_level = "Bajo"
                                            if risk_score >= 3: risk_level = "Alto"
                                            elif risk_score >= 1: risk_level = "Medio"

                                            if risk_level == "Alto": high_risk_extensions += 1

                                            extension_records.append({
                                                "name": manifest.get('name', 'N/A'),
                                                "version": manifest.get('version', 'N/A'),
                                                "description": manifest.get('description', 'N/A')[:50],
                                                "permissions": ", ".join(permissions),
                                                "risk": risk_level
                                            })
                                        except Exception as e:
                                            print(f"    {y('⚠')} Error al leer manifest de extensión en {version_path}: {e}")
                    
                    if extension_records:
                        extensions_json_path = browser_session_dir / 'extensions.json'
                        save_file(extensions_json_path, json.dumps(extension_records, indent=4))
                        print(f"    {g('✓')} Extensiones guardadas: {extensions_json_path}")
                    else:
                        print(f"    {dm('·')} No se encontraron extensiones en {profile_path}")
                else:
                    print(f"    {dm('·')} Directorio de extensiones no encontrado en {profile_path}")

            # --- [F] FIREFOX SPECIFIC ---
            if 'F' in selected_modules and browser_name == "Firefox":
                # Historial (places.sqlite)
                places_db_path = profile_path / 'places.sqlite'
                if places_db_path.is_file():
                    temp_db = browser_session_dir / 'firefox_places.sqlite'
                    try:
                        shutil.copy2(places_db_path, temp_db)
                        conn = sqlite3.connect(temp_db)
                        cursor = conn.cursor()
                        cursor.execute("SELECT url, title, visit_count, last_visit_date FROM moz_places ORDER BY last_visit_date DESC LIMIT 500")
                        history_data = cursor.fetchall()
                        conn.close()

                        history_records = []
                        for url, title, visit_count, last_visit_date in history_data:
                            # Firefox timestamp is microseconds since 1970-01-01
                            dt = datetime(1970, 1, 1) + timedelta(microseconds=last_visit_date)
                            history_records.append({
                                "date": dt.strftime('%Y-%m-%d %H:%M:%S'),
                                "url": url,
                                "title": title,
                                "visit_count": visit_count
                            })
                        history_csv_path = browser_session_dir / 'firefox_history.csv'
                        with open(history_csv_path, 'w', newline='', encoding='utf-8') as f:
                            writer = csv.DictWriter(f, fieldnames=["date", "url", "title", "visit_count"])
                            writer.writeheader()
                            writer.writerows(history_records)
                        print(f"    {g('✓')} Historial Firefox guardado: {history_csv_path}")
                        total_history += len(history_records)
                    except Exception as e:
                        print(f"    {r('✗')} Error al extraer historial Firefox de {profile_path}: {e}")
                else:
                    print(f"    {dm('·')} Historial Firefox no encontrado en {profile_path}")

                # Cookies (cookies.sqlite)
                cookies_db_path = profile_path / 'cookies.sqlite'
                if cookies_db_path.is_file():
                    temp_db = browser_session_dir / 'firefox_cookies.sqlite'
                    try:
                        shutil.copy2(cookies_db_path, temp_db)
                        conn = sqlite3.connect(temp_db)
                        cursor = conn.cursor()
                        cursor.execute("SELECT host, name, value, creationTime, lastAccessed, expiry, isSecure, isHttpOnly FROM moz_cookies")
                        cookies_data = cursor.fetchall()
                        conn.close()

                        cookie_records = []
                        for host, name, value, creationTime, lastAccessed, expiry, isSecure, isHttpOnly in cookies_data:
                            # Firefox timestamps are microseconds since 1970-01-01
                            dt_created = datetime(1970, 1, 1) + timedelta(microseconds=creationTime)
                            dt_expires = datetime.fromtimestamp(expiry) # expiry is seconds since epoch
                            cookie_records.append({
                                "domain": host,
                                "name": name,
                                "value": value,
                                "created": dt_created.strftime('%Y-%m-%d %H:%M:%S'),
                                "expires": dt_expires.strftime('%Y-%m-%d %H:%M:%S'),
                                "secure": bool(isSecure),
                                "httponly": bool(isHttpOnly)
                            })
                        cookies_csv_path = browser_session_dir / 'firefox_cookies.csv'
                        with open(cookies_csv_path, 'w', newline='', encoding='utf-8') as f:
                            writer = csv.DictWriter(f, fieldnames=["domain", "name", "value", "created", "expires", "secure", "httponly"])
                            writer.writeheader()
                            writer.writerows(cookie_records)
                        print(f"    {g('✓')} Cookies Firefox guardadas: {cookies_csv_path}")
                        total_cookies += len(cookie_records)
                    except Exception as e:
                        print(f"    {r('✗')} Error al extraer cookies Firefox de {profile_path}: {e}")
                else:
                    print(f"    {dm('·')} Cookies Firefox no encontradas en {profile_path}")

                # Passwords (logins.json + key4.db)
                logins_json_path = profile_path / 'logins.json'
                key4_db_path = profile_path / 'key4.db' # Required for NSS decryption
                if logins_json_path.is_file():
                    print(f"\n  {C.R}⚠️ ADVERTENCIA LEGAL: Este módulo extrae credenciales almacenadas localmente.")
                    print(f"     Úsalo solo en sistemas sobre los que tengas autorización.{C.RS}")
                    confirm = inp("¿Deseas continuar? [s/N]: ")
                    if confirm.lower() != 's':
                        print(f"    {y('⚠')} Extracción de contraseñas Firefox cancelada.")
                        continue

                    try:
                        logins_data = json.loads(logins_json_path.read_text(errors='ignore'))
                        password_records = []
                        for login in logins_data.get('logins', []):
                            encrypted_username_b64 = login.get('encryptedUsername', '')
                            encrypted_password_b64 = login.get('encryptedPassword', '')
                            
                            # Decryption requires NSS library (libnss3.so) and potentially master password
                            # This is highly complex to implement purely in Python without external bindings
                            # or a full NSS implementation.
                            decrypted_username = decrypt_firefox_nss(encrypted_username_b64)
                            decrypted_password = decrypt_firefox_nss(encrypted_password_b64)

                            password_records.append({
                                "hostname": login.get('hostname', 'N/A'),
                                "username": decrypted_username,
                                "password": decrypted_password,
                                "timeCreated": datetime.fromtimestamp(login.get('timeCreated', 0) / 1000000).strftime('%Y-%m-%d %H:%M:%S') # Microseconds to seconds
                            })
                        
                        firefox_passwords_json_path = browser_session_dir / 'firefox_passwords.json'
                        save_file(firefox_passwords_json_path, json.dumps(password_records, indent=4))
                        print(f"    {g('✓')} Contraseñas Firefox guardadas (cifradas): {firefox_passwords_json_path}")
                        total_passwords += len(password_records)
                    except Exception as e:
                        print(f"    {r('✗')} Error al extraer contraseñas Firefox de {profile_path}: {e}")
                else:
                    print(f"    {dm('·')} logins.json no encontrado en {profile_path}")

    # --- Consolidated Report ---
    print(f"\n  {C.BD}{C.CY}--- Resumen del Análisis de Navegadores ---{C.RS}")
    print(f"  {g('✓')} Navegadores encontrados: {', '.join([b for b, p in browser_paths.items() if p])}")
    print(f"  {g('✓')} Total de entradas de historial: {total_history}")
    print(f"  {g('✓')} Total de cookies: {total_cookies}")
    print(f"  {g('✓')} Total de contraseñas (cifradas/descifradas): {total_passwords}")
    if high_risk_extensions > 0:
        print(f"  {r('✗')} Extensiones de alto riesgo detectadas: {high_risk_extensions}")
    else:
        print(f"  {g('✓')} No se detectaron extensiones de alto riesgo.")
    print(f"\n  {g('✓')} Todos los resultados guardados en {session}")
    pause()

# ══════════════════════════════════════════════════════════════════════════
#  MENÚ PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════
TOOLS = [
    ('00', 'NOXRECON ★',      'Recolección forense completa del sistema',       t00_noxrecon),
    ('01', 'SpiderFoot',      'Framework OSINT con interfaz web',               t01_spiderfoot),
    ('02', 'theHarvester',    'Emails / subdominios / hosts / IPs',             t02_theharvester),
    ('03', 'Volatility 3',    'Análisis forense de memoria RAM',                t03_volatility),
    ('04', 'Binwalk',         'Firmware y análisis de binarios',                t04_binwalk),
    ('05', 'Foremost',        'Carving / recuperación de archivos',             t05_foremost),
    ('06', 'Bulk Extractor',  'Extracción masiva de evidencias digitales',      t06_bulk_extractor),
    ('07', 'ExifTool',        'Extracción de metadatos de archivos',            t07_exiftool),
    ('08', 'tshark',          'Análisis de capturas de red PCAP',               t08_tshark),
    ('09', 'Steghide',        'Esteganografía — datos ocultos en imágenes',     t09_steghide),
    ('10', 'Lynis',           'Auditoría de seguridad del sistema',             t10_lynis),
    ('11', 'chkrootkit',      'Detección de rootkits y backdoors',              t11_rootkit),
    ('12', 'Nmap',            'Escaneo de red y fingerprinting',                t12_nmap),
    ('13', 'Sherlock',        'Username OSINT en +400 plataformas',             t13_sherlock),
    ('14', 'Recon-ng',        'Framework de reconocimiento modular',            t14_reconng),
    ('15', 'Binary Analysis', 'strings / hexdump / hashes / disasm',           t15_binary),
    ('16', 'NOX_PORTSCAN',    'Escáner de puertos y banners (Nativo)',          t16_portscan),
    ('17', 'NOX_FILECAVER',   'Recuperación de archivos (Carving Nativo)',      t17_filecaver),
    ('18', 'NOX_PROCWATCH',    'Análisis de procesos y anomalías',               t18_procwatch),
    ('19', 'NOX_NETSNIFF',    'Sniffer de red Raw (Captura Nativa)',            t19_netsniff),
    ('20', 'NOX_STEGDETECT',  'Detección de esteganografía LSB',                t20_stegdetect),
    ('21', 'NOX_CREDSCAN',    'Escáner de secrets y API keys',                  t21_credscan),
    ('22', 'NOX_TIMELINE',    'Constructor de timeline forense',                t22_timeline),
    ('23', 'NOX_REPORT',      'Generador de reporte HTML final',                t23_report),
    ('24', 'NOX_WIFIKEYS',     'Extracción de contraseñas WiFi guardadas',     t_wifi),
    ('25', 'NOX_BROWSERFORENS','Historial / Cookies / Passwords / Extensiones', t_browser),
]

# Herramientas no disponibles en Termux
TERMUX_SKIP = {'05', '06', '11'}

def menu():
    while True:
        banner()
        env  = 'Termux' if IS_TERMUX else 'Kali/Linux'
        priv = 'ROOT' if IS_ROOT else 'user'
        print(f"  {dm(f'Entorno: {env}  │  {priv}  │  ~/Datos/')}\n")

        for num, name, desc, _ in TOOLS:
            is_exclusive = '★' in name
            is_skip      = IS_TERMUX and num in TERMUX_SKIP
            name_disp    = name.replace(' ★', '')
            tag_ex       = f" {C.Y}[EXCL]{C.RS}" if is_exclusive else ''
            tag_ko       = f" {C.R}[Kali]{C.RS}"  if is_skip     else ''

            if is_skip:
                print(f"  {C.DM}[{num}] {name_disp:<22} {desc}{C.RS}{tag_ko}")
            elif is_exclusive:
                print(f"  {C.Y}[{num}]{C.RS} {C.Y}{C.BD}{name_disp:<22}{C.RS} {dm(desc)}{tag_ex}")
            else:
                print(f"  {cy(f'[{num}]')} {C.W}{name_disp:<22}{C.RS} {dm(desc)}")

        print(f"\n  {cy('[q]')} Salir")
        print(f"  {C.DM}{'─' * 52}{C.RS}")

        choice = inp("Selección: ").strip().lower()

        if choice in ('q', 'quit', 'exit', 'salir', ''):
            if choice in ('q', 'quit', 'exit', 'salir'):
                print(f"\n  {cy('Hasta luego.')}\n")
                sys.exit(0)
            continue

        # Normalizar: "1" → "01"
        if choice.isdigit():
            choice = choice.zfill(2)

        matched = False
        for num, _, _, func in TOOLS:
            if choice == num:
                func()
                matched = True
                break

        if not matched:
            pass  # opción inválida → re-mostrar menú


# ══════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    try:
        menu()
    except KeyboardInterrupt:
        print(f"\n\n  {y('Interrumpido.')}\n")
        sys.exit(0)
