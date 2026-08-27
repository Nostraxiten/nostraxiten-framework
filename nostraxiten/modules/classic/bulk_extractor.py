import os
from core.colors import cy, g, dm
from core.utils import new_session, pause, inp, banner, hdr

def run():
    banner()
    hdr(6, "Bulk Extractor", "Extracción masiva: emails, URLs, IPs, tarjetas de crédito")

    target = inp("Imagen/dispositivo/archivo a analizar: ")
    if not target: pause(); return

    session = new_session('bulk_extractor')
    threads = inp("Threads [4]: ") or '4'
    cmd     = f'bulk_extractor -o {session} -j {threads} -R {target}'
    print(f"\n  {cy('→')} {dm(cmd)}\n")
    os.system(cmd)
    print(f"\n  {g('✓')} Resultados en: {session}")
    pause()

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
