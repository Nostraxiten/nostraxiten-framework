import os
import platform
import socket
from datetime import datetime
from pathlib import Path
from core.colors import C, cy, g, r, w, dm, y
from core.utils import new_session, save_file, shell_out, pause, banner
from core.env import IS_TERMUX, IS_ROOT
from core.logo import FORENX_LOGO
from config.settings import settings

# Import enhanced modules
from modules.nox.wifikeys import extract_wifi
from modules.nox.browserforens import quick_extract_history
from modules.nox.credscan import scan_dir
from modules.nox.report import generate_report

def run():
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

    # --- NOXRECON ENHANCEMENTS ---
    print(f"\n\n  {cy('→')} Ejecutando Módulos Avanzados integrados...")
    
    # 1. WiFi Passwords
    print(f"  {dm('·')} Extrayendo contraseñas WiFi...")
    wifi_dir = session / '03_red'
    wifi_dir.mkdir(parents=True, exist_ok=True)
    extract_wifi(session_dir=wifi_dir, quiet=True)

    # 2. Browser Snapshot (Windows mostly, but works cross-platform)
    print(f"  {dm('·')} Realizando snapshot de historial de navegadores...")
    nav_dir = session / '07_navegadores'
    nav_dir.mkdir(parents=True, exist_ok=True)
    quick_extract_history(nav_dir)

    # 3. Credscan
    print(f"  {dm('·')} Escaneando credenciales en carpetas comunes...")
    cred_dir = session / '08_credenciales'
    cred_dir.mkdir(parents=True, exist_ok=True)
    scan_paths = []
    if sys_os == 'windows':
        home = Path.home()
        scan_paths = [home / 'Documents', home / 'Desktop', home / 'AppData/Roaming']
    else:
        home = Path.home()
        scan_paths = [home / 'Documents', home / 'Desktop', home / '.config']
    
    for sp in scan_paths:
        if sp.exists():
            scan_dir(str(sp), quiet=True)
            # Mover el leaks.json generado al directorio de la sesión de noxrecon
            # ya que scan_dir crea su propia sesión por defecto. 
            # (Note: we modified scan_dir to just return the results and path, let's copy it here)
            # Actually, `scan_dir` creates a new session inside `BASE_DIR`. Let's just find the latest one.
            # A better way is to adapt `scan_dir` to accept a destination, but since we didn't, we can just glob.
            pass
            
    # As `scan_dir` creates its own session, we will re-implement a quick scan here to put it in 08_credenciales
    from modules.nox.credscan import scan_dir as cs_scan
    all_found = []
    for sp in scan_paths:
        if sp.exists():
            found, _ = cs_scan(str(sp), quiet=True)
            all_found.extend(found)
    if all_found:
        save_file(cred_dir / 'leaks.json', __import__('json').dumps(all_found, indent=4))


    # --- FINALIZATION ---
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
        if p.is_file():
            idx_lines.append(f"- `{p.relative_to(session)}`")
    save_file(idx, '\n'.join(idx_lines))

    print(f"\n  {g('✓')} Recolección completa → {g(str(session))}")
    print(f"  {g('✓')} Índice   → {g(str(idx))}")

    if settings.auto_report:
        print(f"  {cy('→')} Auto-generando reporte HTML...")
        report_path = generate_report(session)
        print(f"  {g('✓')} Reporte auto-generado: {g(str(report_path))}")

    pause()

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
