import os
from pathlib import Path
from core.colors import r, cy, g, dm
from core.utils import exists, new_session, pause, inp, banner, hdr

def run():
    banner()
    hdr(3, "Volatility 3", "Análisis forense de memoria RAM (dumps de memoria)")
    vol_bin = next((b for b in ['vol', 'vol3', 'volatility3'] if exists(b)), 'vol3')

    mem_file = inp("Ruta al dump de memoria (ej: /mnt/evidence.raw): ")
    if not mem_file or not Path(mem_file).exists():
        print(f"  {r('✗')} Archivo no encontrado: {mem_file}")
        pause(); return

    plugins = {
        '1': 'windows.pslist.PsList',
        '2': 'windows.netscan.NetScan',
        '3': 'windows.cmdline.CmdLine',
        '4': 'windows.filescan.FileScan',
        '5': 'windows.malfind.Malfind',
        '6': 'linux.pslist.PsList',
        '7': 'linux.bash.Bash',
        '8': 'linux.netstat.Netstat',
    }
    descs = {
        '1': 'Procesos Windows',      '2': 'Conexiones de red (Win)',
        '3': 'Líneas de comando',      '4': 'Escaneo de archivos',
        '5': 'Detección de malware',   '6': 'Procesos Linux',
        '7': 'Historial bash (Linux)', '8': 'Netstat Linux',
    }
    for k in plugins:
        print(f"    {cy(k)}. {plugins[k]:<40} {dm(descs[k])}")

    choice  = inp("Plugin [1]: ") or '1'
    plugin  = plugins.get(choice, plugins['1'])
    session = new_session('volatility')
    out     = session / f"{plugin.replace('.', '-')}.txt"

    cmd = f'{vol_bin} -f {mem_file} {plugin}'
    print(f"\n  {cy('→')} {dm(cmd)}\n")
    os.system(f'{cmd} 2>&1 | tee {out}')
    print(f"\n  {g('✓')} Guardado: {out}")
    pause()

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
