import os
import csv
from datetime import datetime
from pathlib import Path
from core.colors import cy, g
from core.utils import new_session, pause, inp, banner, hdr

def run():
    banner()
    hdr(22, "NOX_TIMELINE", "Generador de línea de tiempo de archivos")
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

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
