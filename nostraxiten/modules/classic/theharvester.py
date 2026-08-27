import os
from core.colors import cy, g, dm
from core.utils import new_session, pause, inp, banner, hdr

def run():
    banner()
    hdr(2, "theHarvester", "Emails, subdominios, hosts, IPs, names desde fuentes OSINT")

    domain = inp("Dominio objetivo: ")
    if not domain: pause(); return
    limit  = inp("Límite resultados [500]: ") or '500'
    source = inp("Fuentes [baidu,bing,crtsh,yahoo]: ") or 'baidu,bing,crtsh,yahoo'

    session  = new_session(f'theHarvester_{domain}')
    out_file = session / 'results'
    cmd = f'theHarvester -d {domain} -l {limit} -b {source} -f {out_file}'
    print(f"\n  {cy('→')} {dm(cmd)}\n")
    os.system(cmd)
    print(f"\n  {g('✓')} Resultados en: {session}")
    pause()

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
