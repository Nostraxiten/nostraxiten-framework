import json
import binascii
from pathlib import Path
from core.colors import cy, g, r, dm
from core.utils import new_session, pause, inp, banner, hdr

def run():
    banner()
    hdr(17, "NOX_FILECAVER", "Recuperación de archivos por Magic Bytes (Pure Python)")
    path = inp("Archivo/Imagen de disco: ")
    if not path or not Path(path).exists(): return

    json_path = Path(__file__).parent.parent.parent / 'data' / 'magic_bytes.json'
    if not json_path.exists():
        print(f"  {r('✗')} No se encontró el archivo de firmas en {json_path}")
        pause(); return

    try:
        with open(json_path, 'r') as f:
            sigs_data = json.load(f)
    except Exception as e:
        print(f"  {r('✗')} Error al leer magic_bytes.json: {e}")
        pause(); return

    sigs = {}
    for name, data in sigs_data.items():
        try:
            head = binascii.unhexlify(data['header'])
            foot = binascii.unhexlify(data['footer']) if data.get('footer') else None
            sigs[name] = {
                'head': head,
                'foot': foot,
                'ext': data['ext'],
                'size': data.get('max_size', 1024*100)
            }
        except Exception as e:
            print(f"  {r('✗')} Error al procesar firma {name}: {e}")

    session = new_session('filecarver')
    carv_dir = session / 'recovered'
    carv_dir.mkdir(exist_ok=True)
    
    print(f"\n  {cy('→')} Analizando binario... esto puede tardar.\n")
    count = 0
    with open(path, 'rb') as f:
        data = f.read()
        for name, sig in sigs.items():
            offset = 0
            while True:
                offset = data.find(sig['head'], offset)
                if offset == -1: break
                
                end = -1
                if sig['foot']:
                    end = data.find(sig['foot'], offset + len(sig['head']))
                    if end != -1: end += len(sig['foot'])
                
                if end == -1: end = offset + sig.get('size', 1024*100)
                
                extracted = data[offset:end]
                out_name = carv_dir / f"carved_0x{offset:X}_{name}{sig['ext']}"
                with open(out_name, 'wb') as out_f: out_f.write(extracted)
                
                print(f"  {g('✓')} {name.upper():<6} hallado en {hex(offset)} | {len(extracted)} bytes")
                count += 1
                offset += len(sig['head'])

    print(f"\n  {g('✓')} {count} archivos recuperados en {carv_dir}")
    pause()

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
