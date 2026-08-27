import os
import shutil
from core.colors import cy, g, y, dm
from core.utils import new_session, pause, inp, banner, hdr
from core.env import IS_ROOT

def run():
    banner()
    hdr(12, "Nmap", "Escaneo de red, fingerprinting y detección de vulnerabilidades")

    target = inp("Target (IP / rango CIDR / dominio): ")
    if not target: pause(); return

    modes = {
        '1': ('-sV -sC -O',                      'Completo (versiones + scripts + OS)'),
        '2': ('-sn',                              'Ping sweep — descubrimiento de hosts'),
        '3': ('-p- --open -T4',                   'Todos los puertos TCP abiertos'),
        '4': ('-sU --top-ports 200',              'Top 200 puertos UDP'),
        '5': ('-sV --script=vuln',               'Scan de vulnerabilidades'),
        '6': ('-sV --script=smb-vuln*,http-vuln*', 'Vulns SMB + HTTP específicas'),
        '7': ('-A --script=default,auth,discovery', 'Agresivo + auth + discovery'),
    }
    for k, (_, d) in modes.items():
        print(f"    {cy(k)}. {d}")

    mode    = inp("Modo [1]: ") or '1'
    flags   = modes.get(mode, modes['1'])[0]
    session = new_session(f'nmap_{target.replace("/", "_")}')
    xml_f   = session / 'nmap.xml'
    txt_f   = session / 'nmap.txt'
    gnmap_f = session / 'nmap.gnmap'

    if not IS_ROOT and ('-sS' in flags or '-O' in flags):
        print(f"  {y('⚠')} Este scan requiere root. Saltando flags que lo necesitan o ejecuta con sudo.")

    cmd = f'nmap {flags} {target} -oX {xml_f} -oG {gnmap_f} -oN {txt_f}'
    print(f"\n  {cy('→')} {dm(cmd)}\n")
    os.system(cmd)
    print(f"\n  {g('✓')} Resultados en: {session}")
    pause()

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
