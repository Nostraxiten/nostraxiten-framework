import os
import re
import sys
import json
import platform
import subprocess
from pathlib import Path
from core.colors import cy, g, r, y, dm, C
from core.utils import new_session, save_file, pause, banner, hdr
from core.env import IS_TERMUX, HOME

SUSPICIOUS_CMD_PATTERNS = [
    r'nc\s+-[el]',
    r'bash\s+-i',
    r'/dev/tcp/',
    r'curl\s+[^|\n]+?\|\s*(?:bash|sh)',
    r'wget\s+[^|\n]+?\|\s*(?:bash|sh)',
    r'(?:powershell|pwsh).*(?:-enc|-encodedcommand|bypass|downloadstring)',
    r'certutil.*-urlcache',
    r'base64\s+-d',
    r'mimikatz',
    r'chisel',
    r'ngrok'
]

def analyze_linux_procs():
    anomalies_found = []
    proc_root = Path('/proc')
    if not proc_root.exists():
        return anomalies_found

    for proc_path in proc_root.glob('[0-9]*'):
        pid = proc_path.name
        try:
            with open(proc_path / 'cmdline', 'r', errors='ignore') as f:
                cmd = f.read().replace('\0', ' ').strip()
            
            exe_path = "N/A"
            try:
                exe_path = str((proc_path / 'exe').readlink())
            except Exception:
                pass
            
            anomalies = []
            if (exe_path == "N/A" or not exe_path) and cmd:
                anomalies.append("Hollow/NoExe")
            
            try:
                environ = (proc_path / 'environ').read_text(errors='ignore')
                if "LD_PRELOAD" in environ:
                    anomalies.append("LD_PRELOAD")
            except Exception:
                pass

            if exe_path and any(temp_dir in exe_path.lower() for temp_dir in ['/tmp', '/dev/shm', '/var/tmp']):
                anomalies.append("ExecInTemp")

            for pat in SUSPICIOUS_CMD_PATTERNS:
                if re.search(pat, cmd, re.IGNORECASE):
                    anomalies.append("SuspiciousCMD")
                    break

            if anomalies:
                anomalies_found.append({
                    "pid": pid,
                    "cmd": cmd,
                    "exe": exe_path,
                    "anomalies": anomalies
                })
        except Exception:
            continue

    return anomalies_found

def analyze_windows_procs():
    anomalies_found = []
    try:
        # Use tasklist or powershell
        cmd = ["powershell", "-NoProfile", "-Command", 
               "Get-CimInstance Win32_Process | Select-Object ProcessId, Name, Path, CommandLine | ConvertTo-Json -Compress"]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if res.returncode == 0 and res.stdout.strip():
            raw_data = json.loads(res.stdout)
            if isinstance(raw_data, dict):
                raw_data = [raw_data]
            
            for item in raw_data:
                pid = str(item.get("ProcessId", ""))
                name = item.get("Name", "") or ""
                path = item.get("Path", "") or ""
                cmdline = item.get("CommandLine", "") or ""
                
                anomalies = []
                if path and any(td in path.lower() for td in ['appdata\\local\\temp', 'windows\\temp', 'public']):
                    anomalies.append("ExecInTemp")
                
                for pat in SUSPICIOUS_CMD_PATTERNS:
                    if re.search(pat, cmdline, re.IGNORECASE):
                        anomalies.append("SuspiciousCMD")
                        break

                if anomalies:
                    anomalies_found.append({
                        "pid": pid,
                        "cmd": cmdline or name,
                        "exe": path,
                        "anomalies": anomalies
                    })
    except Exception:
        pass
    return anomalies_found

def check_persistence():
    sys_os = platform.system().lower()
    persist_records = []
    
    suspicious_persist_regex = re.compile(
        r'(curl|wget|bash|sh|powershell|cmd\.exe|nc|socat|python|perl|eval|base64|certutil|\.vbs|\.ps1)',
        re.IGNORECASE
    )

    if sys_os == 'windows':
        # Check Startup folder
        startup_dir = Path.home() / 'AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup'
        if startup_dir.exists():
            for f in startup_dir.iterdir():
                if f.is_file():
                    persist_records.append({
                        "location": "Startup Folder",
                        "path": str(f),
                        "suspicious": True,
                        "detail": f"Archivo en inicio automático: {f.name}"
                    })

        # Check Registry Run keys
        reg_keys = [
            r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run",
            r"HKLM\Software\Microsoft\Windows\CurrentVersion\Run"
        ]
        for rk in reg_keys:
            try:
                res = subprocess.run(["reg", "query", rk], capture_output=True, text=True, timeout=5)
                if res.returncode == 0:
                    for line in res.stdout.splitlines():
                        line = line.strip()
                        if line and not line.startswith("HKEY_"):
                            is_susp = bool(suspicious_persist_regex.search(line))
                            persist_records.append({
                                "location": rk,
                                "entry": line,
                                "suspicious": is_susp,
                                "detail": line
                            })
            except Exception:
                pass
    else:
        # Linux / Unix / macOS persistence paths
        paths_to_check = [
            Path('/etc/crontab'),
            Path('/etc/rc.local'),
            HOME / '.bashrc',
            HOME / '.zshrc',
            HOME / '.profile',
            Path('/etc/cron.d')
        ]

        for p in paths_to_check:
            if not p.exists():
                continue
            if p.is_dir():
                file_list = [f for f in p.iterdir() if f.is_file()]
            else:
                file_list = [p]

            for target_file in file_list:
                try:
                    content = target_file.read_text(errors='ignore')
                    susp_lines = []
                    for line in content.splitlines():
                        line_s = line.strip()
                        if line_s and not line_s.startswith('#'):
                            if suspicious_persist_regex.search(line_s):
                                susp_lines.append(line_s)
                    
                    if susp_lines:
                        persist_records.append({
                            "location": str(target_file),
                            "suspicious": True,
                            "suspicious_lines": susp_lines[:5],
                            "detail": f"{len(susp_lines)} línea(s) sospechosa(s)"
                        })
                    else:
                        persist_records.append({
                            "location": str(target_file),
                            "suspicious": False,
                            "detail": "Verificado (sin patrones de riesgo detectados)"
                        })
                except Exception as e:
                    persist_records.append({
                        "location": str(target_file),
                        "suspicious": False,
                        "detail": f"No accesible: {e}"
                    })

    return persist_records

def run():
    banner()
    hdr(18, "NOX_PROCWATCH", "Análisis profundo de procesos y anomalías")
    if IS_TERMUX: 
        print(f"  {y('⚠')} En Termux el acceso a /proc está muy limitado.")
    
    session = new_session('procwatch')
    sys_os = platform.system().lower()

    print(f"\n  {C.W}{'PID':<8} {'PROCESO':<28} {'ANOMALÍA':<20}{C.RS}")
    print(f"  {dm('─' * 60)}")

    if sys_os == 'windows':
        report = analyze_windows_procs()
    else:
        report = analyze_linux_procs()

    if not report:
        print(f"  {g('✓')} No se detectaron anomalías críticas en los procesos activos.")
    else:
        for item in report:
            pid = item['pid']
            cmd_preview = item['cmd'][:26]
            anoms = ",".join(item['anomalies'])
            color = C.R if any(x in anoms for x in ["Hollow", "LD_PRELOAD", "SuspiciousCMD"]) else C.Y
            print(f"  {color}{pid:<8} {cmd_preview:<28} {anoms:<20}{C.RS}")

    save_file(session / 'proc_anomalies.json', json.dumps(report, indent=4))

    print(f"\n  {g('✓')} Análisis de persistencia del sistema ({sys_os})...")
    persist_results = check_persistence()
    for item in persist_results:
        loc = item.get("location", "")
        is_susp = item.get("suspicious", False)
        detail = item.get("detail", "")
        if is_susp:
            print(f"  {r('!')} {loc} → {y(detail)}")
        else:
            print(f"  {dm('·')} {loc} → {dm(detail)}")

    save_file(session / 'persistence_audit.json', json.dumps(persist_results, indent=4))
    print(f"\n  {g('✓')} Auditoría guardada en: {g(str(session))}")
    pause()

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
