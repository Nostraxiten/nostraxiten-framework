import os
from core.colors import y, g, dm, cy
from core.utils import pause, inp, banner, hdr

def run():
    banner()
    hdr(1, "SpiderFoot", "Framework OSINT automático con interfaz web")
    port = inp("Puerto web [4444]: ") or '4444'
    print(f"\n  {g('✓')} Iniciando en http://127.0.0.1:{port}")
    print(f"  {y('!')} Abre el navegador en http://127.0.0.1:{port}")
    print(f"  {dm('Ctrl+C para detener')}\n")
    os.system(f'spiderfoot -l 127.0.0.1:{port}')
    pause()

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
