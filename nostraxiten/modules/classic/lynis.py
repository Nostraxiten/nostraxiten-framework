import os
import shutil
from core.colors import cy, g, y, dm
from core.utils import new_session, pause, banner, hdr
from core.env import IS_ROOT, HOME

def run():
    banner()
    hdr(10, "Lynis", "Auditoría de seguridad y hardening del sistema Linux")
    lynis_bin = shutil.which('lynis') or 'lynis'

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

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
