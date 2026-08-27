import os
from core.colors import cy, g, dm
from core.utils import new_session, pause, inp, banner, hdr

def run():
    banner()
    hdr(5, "Foremost", "Recuperación y carving de archivos eliminados de imágenes de disco")

    target = inp("Dispositivo o imagen (ej: /dev/sda1, dump.img): ")
    if not target: pause(); return

    session = new_session('foremost')
    carv    = session / 'carving'
    cmd     = f'foremost -i {target} -o {carv} -v -T'
    print(f"\n  {cy('→')} {dm(cmd)}\n")
    os.system(cmd)
    print(f"\n  {g('✓')} Archivos recuperados en: {carv}")
    pause()

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
