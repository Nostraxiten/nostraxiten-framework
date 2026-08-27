import os
from pathlib import Path
from core.colors import r, cy, g, dm
from core.utils import new_session, pause, inp, banner, hdr

def run():
    banner()
    hdr(4, "Binwalk", "Análisis de firmware, archivos binarios y extracción")

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

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
