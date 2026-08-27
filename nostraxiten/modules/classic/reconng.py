import os
from core.colors import dm
from core.utils import pause, banner, hdr

def run():
    banner()
    hdr(14, "Recon-ng", "Framework de reconocimiento web modular y automatizable")

    print(f"  {dm('Comandos útiles dentro de recon-ng:')}")
    print(f"  {dm('  workspaces create <nombre>')}")
    print(f"  {dm('  marketplace install all')}")
    print(f"  {dm('  modules search <keyword>')}")
    print(f"  {dm('  db insert domains  →  set domain  →  run')}\n")
    os.system('recon-ng')
    pause()

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
