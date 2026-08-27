import socket
import re
import json
from concurrent.futures import ThreadPoolExecutor
from core.colors import cy, g, dm, C
from core.utils import new_session, save_file, pause, inp, banner, hdr

def run():
    banner()
    hdr(16, "NOX_PORTSCAN", "Motor de escaneo y banner grabbing (Pure Python)")
    target = inp("IP Objetivo: ")
    if not target: return
    ports_str = inp("Puertos (ej: 21-80,443,3306) [1-1024]: ") or "1-1024"
    
    ports = []
    for part in ports_str.split(','):
        if '-' in part:
            start, end = map(int, part.split('-'))
            ports.extend(range(start, end + 1))
        else:
            ports.append(int(part))

    results = []
    print(f"\n  {cy('→')} Escaneando {len(ports)} puertos en {target}...\n")

    def scan_port(port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.5)
        try:
            res = s.connect_ex((target, port))
            if res == 0:
                banner_txt = "Desconocido"
                try:
                    s.send(b"HEAD / HTTP/1.0\r\n\r\n")
                    banner_txt = s.recv(512).decode('utf-8', 'ignore').strip().replace('\n', ' ')
                except: pass
                
                service = "Unknown"
                if re.search(r'SSH', banner_txt, re.I): service = "SSH"
                elif re.search(r'HTTP|Apache|nginx', banner_txt, re.I): service = "HTTP"
                elif re.search(r'FTP', banner_txt, re.I): service = "FTP"
                elif re.search(r'MySQL', banner_txt, re.I): service = "MySQL"
                
                print(f"  {g('[+]')} Puerto {C.W}{port:<5}{C.RS} | {C.G}ABIERTO{C.RS} | {C.CY}{service:<8}{C.RS} | {dm(banner_txt[:40])}")
                return {"port": port, "status": "open", "service": service, "banner": banner_txt}
        except: pass
        finally: s.close()
        return None

    with ThreadPoolExecutor(max_workers=50) as executor:
        found = list(executor.map(scan_port, ports))
        results = [r for r in found if r]

    session = new_session('portscan')
    save_file(session/'results.json', json.dumps(results, indent=4))
    print(f"\n  {g('✓')} Escaneo finalizado. {len(results)} puertos abiertos. Datos en {session}")
    pause()

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
