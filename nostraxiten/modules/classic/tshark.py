import os
from pathlib import Path
from core.colors import r, cy, g, y, dm
from core.utils import new_session, pause, inp, banner, hdr, run_and_save

def run():
    banner()
    hdr(8, "tshark", "Análisis de capturas PCAP/PCAPNG y captura en vivo")

    print(f"  {cy('Modos:')}")
    print(f"    {cy('1')}. Analizar archivo PCAP/PCAPNG")
    print(f"    {cy('2')}. Captura en vivo")
    mode = inp("Modo [1]: ") or '1'
    session = new_session('tshark')

    if mode == '2':
        iface = inp("Interfaz (ej: eth0, wlan0): ")
        count = inp("Paquetes [200]: ") or '200'
        out   = session / 'captura.pcap'
        print(f"\n  {y('!')} Capturando... Ctrl+C para detener\n")
        run_cmd = f'tshark -i "{iface}" -c {count} -w "{out}"' if iface else f'tshark -c {count} -w "{out}"'
        import subprocess
        subprocess.run(run_cmd, shell=True)
        print(f"\n  {g('✓')} PCAP guardado: {out}")
    else:
        pcap = inp("Ruta al archivo PCAP: ")
        if not pcap or not Path(pcap).exists():
            print(f"  {r('✗')} Archivo no encontrado"); pause(); return

        analyses = {
            '1': (f'tshark -r "{pcap}" -q -z io,stat,0',                          'estadisticas.txt',   'Estadísticas generales'),
            '2': (f'tshark -r "{pcap}" -T fields -e ip.src -e ip.dst',            'top_ips.txt',        'Top IPs src/dst'),
            '3': (f'tshark -r "{pcap}" -Y http.request -T fields -e http.host -e http.request.uri', 'http_requests.txt',  'HTTP requests'),
            '4': (f'tshark -r "{pcap}" -Y dns -T fields -e dns.qry.name',         'dns_queries.txt',    'DNS queries'),
            '5': (f'tshark -r "{pcap}" -q -z io,phs',                             'protocols.txt',      'Distribución protocolos'),
            '6': (f'tshark -r "{pcap}" -Y "tcp.flags.syn==1 && tcp.flags.ack==0" -T fields -e ip.src -e tcp.dstport', 'syn_scan.txt', 'Posible port-scan (SYN)'),
        }
        for k, (_, fn, desc) in analyses.items():
            print(f"    {cy(k)}. {desc}")
        sub = inp("Análisis [1]: ") or '1'
        cmd, fname, _ = analyses.get(sub, analyses['1'])
        out_f = session / fname
        print(f"\n  {cy('→')} {dm(cmd)}\n")
        run_and_save(cmd, out_f)
        print(f"\n  {g('✓')} Guardado: {out_f}")
    pause()

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
