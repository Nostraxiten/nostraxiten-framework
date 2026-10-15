import re
import json
from pathlib import Path
from core.colors import cy, g, r, C
from core.utils import new_session, save_file, pause, inp, banner, hdr

def run():
    banner()
    hdr(21, "NOX_CREDSCAN", "Búsqueda de API Keys, Tokens y Passwords")
    path = inp("Directorio a escanear [.]: ") or "."
    
    scan_dir(path)

def scan_dir(path_to_scan, quiet=False, create_session=True):
    rules = {
        'AWS Key': r'AKIA[0-9A-Z]{16}',
        'GitHub Token': r'gh[pousr]_[A-Za-z0-9_]{36,255}',
        'Slack Token': r'xox[baprs]-[0-9a-zA-Z]{10,48}',
        'Discord Token': r'[MNO][a-zA-Z\d_-]{23,25}\.[a-zA-Z\d_-]{6}\.[a-zA-Z\d_-]{27}',
        'Generic API Key': r'(?i)(?:api_key|apikey|secret_key|app_secret)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{16,64})["\']',
        'Generic Password': r'(?i)password\s*[:=]\s*["\']([^"\']+)["\']',
        'JWT Token': r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*',
        'Private Key': r'-----BEGIN [A-Z ]+ PRIVATE KEY-----',
        'Google API': r'AIza[0-9A-Za-z-_]{35}'
    }

    found = []

    for p in Path(path_to_scan).rglob('*'):
        if p.is_file() and p.suffix.lower() not in ('.exe', '.png', '.jpg', '.jpeg', '.gif', '.zip', '.tar', '.gz', '.iso', '.bin', '.dll', '.so'):
            try:
                content = p.read_text(errors='ignore')
                for name, regex in rules.items():
                    matches = re.finditer(regex, content)
                    for m in matches:
                        val = m.group()
                        obs = val[:6] + "***"
                        if not quiet:
                            print(f"  {C.R}[!]{C.RS} {name:<17} | {p.name:<20} | {C.Y}{obs}{C.RS}")
                        found.append({"file": str(p), "type": name, "value": val})
            except: continue

    save_path = None
    if create_session:
        session = new_session('credscan')
        save_path = session / 'leaks.json'
        save_file(save_path, json.dumps(found, indent=4))
        
    if not quiet:
        print(f"\n  {g('✓')} Escaneo completado. {len(found)} secretos hallados.")
        pause()
    return found, save_path

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
