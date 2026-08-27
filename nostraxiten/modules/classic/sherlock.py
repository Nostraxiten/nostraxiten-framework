import os
from core.colors import cy
from core.utils import exists, new_session, pause, inp, banner, hdr
from core.env import HOME

def run():
    banner()
    hdr(13, "Sherlock", "Username OSINT — búsqueda en +400 redes sociales y plataformas")
    sherlock_dir = HOME / 'sherlock'

    username = inp("Username a buscar: ")
    if not username: pause(); return

    session  = new_session(f'sherlock_{username}')
    out_file = session / f'{username}.txt'

    if exists('sherlock'):
        cmd = f'sherlock "{username}" --output {out_file} --print-found'
    else:
        cmd = f'cd {sherlock_dir} && python3 sherlock/sherlock.py "{username}" --output {out_file} --print-found'

    print(f"\n  {cy('→')} Buscando {cy(username)}...\n")
    os.system(cmd)
    print(f"\n  {cy('✓')} Resultados: {out_file}")
    pause()

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
