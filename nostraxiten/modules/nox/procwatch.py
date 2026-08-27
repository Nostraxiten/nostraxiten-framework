import json
from pathlib import Path
from core.colors import cy, g, y, dm, C
from core.utils import new_session, save_file, pause, banner, hdr
from core.env import IS_TERMUX, HOME

def run():
    banner()
    hdr(18, "NOX_PROCWATCH", "Análisis profundo de procesos y anomalías")
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
    
    persist_paths = ['/etc/crontab', '/etc/rc.local', str(HOME / '.bashrc')]
    for p in persist_paths:
        if Path(p).exists():
            print(f"  {cy('→')} Verificando {p}...")

    pause()

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
