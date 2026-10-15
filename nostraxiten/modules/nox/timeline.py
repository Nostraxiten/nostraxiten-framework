import os
import csv
from datetime import datetime
from pathlib import Path
from core.colors import cy, g, r, dm, C
from core.utils import new_session, pause, inp, banner, hdr

def run():
    banner()
    hdr(22, "NOX_TIMELINE", "Generador de Línea de Tiempo Forense (MACB: Modified, Accessed, Created)")
    target = inp("Directorio objetivo: ")
    if not target or not Path(target).exists():
        print(f"  {r('✗')} Ruta inválida o no encontrada.")
        pause()
        return

    session = new_session('timeline')
    csv_file = session / 'timeline.csv'
    
    print(f"\n  {cy('→')} Escaneando archivos y recolectando marcas de tiempo MACB...")
    events = []
    total_files = 0

    for root, _, files in os.walk(target):
        for f in files:
            p = Path(root) / f
            total_files += 1
            try:
                st = p.stat()
                file_size = st.st_size
                path_str = str(p)

                # M - Modified
                mtime_str = datetime.fromtimestamp(st.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                events.append({
                    'timestamp': mtime_str,
                    'type': 'MODIFIED (M)',
                    'file': path_str,
                    'size_bytes': file_size,
                    'extension': p.suffix.lower()
                })

                # A - Accessed
                atime_str = datetime.fromtimestamp(st.st_atime).strftime('%Y-%m-%d %H:%M:%S')
                events.append({
                    'timestamp': atime_str,
                    'type': 'ACCESSED (A)',
                    'file': path_str,
                    'size_bytes': file_size,
                    'extension': p.suffix.lower()
                })

                # B/C - Created / Metadata Changed (st_ctime on Windows is creation time, on Unix is metadata change)
                ctime_str = datetime.fromtimestamp(st.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
                ctime_label = 'CREATED/METACHG (C)'
                events.append({
                    'timestamp': ctime_str,
                    'type': ctime_label,
                    'file': path_str,
                    'size_bytes': file_size,
                    'extension': p.suffix.lower()
                })

            except Exception:
                continue

    events.sort(key=lambda x: x['timestamp'], reverse=True)
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['timestamp', 'type', 'file', 'size_bytes', 'extension'])
        writer.writeheader()
        writer.writerows(events)

    print(f"\n  {g('✓')} Análisis completado:")
    print(f"    - Archivos analizados: {C.W}{total_files:,}{C.RS}")
    print(f"    - Eventos temporales generados: {C.Y}{len(events):,}{C.RS}")
    print(f"    - Archivo CSV forense: {g(str(csv_file))}")

    # Preview latest 5 events
    if events:
        print(f"\n  {cy('Eventos más recientes:')}")
        for ev in events[:5]:
            print(f"    {dm(ev['timestamp'])} | {C.CY}{ev['type']:<20}{C.RS} | {Path(ev['file']).name}")

    pause()

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
