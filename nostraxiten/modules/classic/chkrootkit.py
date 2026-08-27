import os
from core.colors import r, cy, g
from core.utils import exists, pkg_install, new_session, pause, inp, warn_termux, banner, hdr

def run():
    banner()
    hdr(11, "chkrootkit / rkhunter", "Detección de rootkits, backdoors y malware en el sistema")
    if warn_termux(skip=True): return

    tool = next((t for t in ['chkrootkit', 'rkhunter'] if exists(t)), None)
    if not tool:
        print(f"  {r('✗')} Herramienta no encontrada. Instálala usando los comandos mostrados anteriormente."); pause(); return

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

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
