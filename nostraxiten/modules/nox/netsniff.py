import socket
import struct
import time
from core.colors import cy, g, r, y, C
from core.utils import new_session, pause, banner, hdr
from core.env import IS_ROOT

def run():
    banner()
    hdr(19, "NOX_NETSNIFF", "Sniffer de red por Raw Sockets (Solo Linux/Root)")
    if not IS_ROOT: print(f"  {r('✗')} Requiere ROOT."); pause(); return

    try:
        sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
    except Exception as e:
        print(f"  {r('✗')} Error al crear raw socket: {e}"); pause(); return

    session = new_session('netsniff')
    pcap_file = session / 'capture.pcap'
    
    with open(pcap_file, 'wb') as f:
        f.write(struct.pack('!IHHiIII', 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1))

    print(f"  {y('!')} Capturando... Ctrl+C para detener y guardar.\n")
    print(f"  {'PROTO':<8} {'ORIGEN':<20} {'DESTINO':<20}")
    
    try:
        count = 0
        while count < 100:
            raw_data, _ = sock.recvfrom(65535)
            count += 1
            
            eth = struct.unpack('!6s6sH', raw_data[:14])
            proto = socket.htons(eth[2])
            
            if proto == 8: # IPv4
                ip_hdr = struct.unpack('!BBHHHBBH4s4s', raw_data[14:34])
                src_ip = socket.inet_ntoa(ip_hdr[8])
                dst_ip = socket.inet_ntoa(ip_hdr[9])
                l4_proto = ip_hdr[6]
                
                p_name = "TCP" if l4_proto == 6 else "UDP" if l4_proto == 17 else "ICMP"
                print(f"  {C.CY}{p_name:<8}{C.RS} {src_ip:<20} -> {dst_ip:<20}")
                
                t = str(time.time()).split('.')
                ts_sec = int(t[0])
                ts_usec = int(t[1][:6]) if len(t) > 1 else 0
                pkt_hdr = struct.pack('!IIII', ts_sec, ts_usec, len(raw_data), len(raw_data))
                with open(pcap_file, 'ab') as f: f.write(pkt_hdr + raw_data)

    except KeyboardInterrupt: pass
    print(f"\n  {g('✓')} Captura guardada en formato PCAP: {pcap_file}")
    pause()

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
