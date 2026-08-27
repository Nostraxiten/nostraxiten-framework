import os
from pathlib import Path
from core.colors import cy, g, dm
from core.utils import new_session, pause, inp, banner, hdr

def run():
    banner()
    hdr(7, "ExifTool", "Extracción de metadatos — imágenes, PDFs, documentos, audio/video")

    target = inp("Archivo o directorio: ")
    if not target: pause(); return

    session = new_session('exiftool')
    out     = session / 'metadata.txt'
    rec_flag = '-r' if Path(target).is_dir() else ''
    cmd = f'exiftool {rec_flag} -a -u -g1 "{target}"'
    print(f"\n  {cy('→')} {dm(cmd)}\n")
    os.system(f'{cmd} 2>&1 | tee {out}')
    print(f"\n  {g('✓')} Metadatos en: {out}")
    pause()

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
