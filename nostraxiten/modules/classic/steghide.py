import os
from pathlib import Path
from core.colors import r, cy, g, dm
from core.utils import exists, pkg_install, new_session, pause, inp, banner, hdr

def run():
    banner()
    hdr(9, "Steghide / StegSeek", "Detección y extracción de datos ocultos en imágenes")

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

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
