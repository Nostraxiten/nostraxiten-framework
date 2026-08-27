from pathlib import Path
from core.colors import cy, g, dm, r
from core.utils import run as run_cmd, new_session, save_file, pause, inp, banner, hdr

def run():
    banner()
    hdr(15, "Binary Analysis", "strings + hexdump + xxd + file + hashes MD5/SHA256")

    target = inp("Archivo a analizar: ")
    if not target or not Path(target).exists():
        print(f"  {r('✗')} Archivo no encontrado"); pause(); return

    session = new_session('binary_analysis')

    analyses = {
        '1': (f'file "{target}"',                              'file_type.txt',   'Tipo de archivo'),
        '2': (f'strings -n 6 "{target}"',                     'strings.txt',     'Cadenas ASCII (min 6 chars)'),
        '3': (f'hexdump -C "{target}" | head -300',           'hexdump.txt',     'Hexdump (300 líneas)'),
        '4': (f'xxd "{target}" | head -300',                  'xxd.txt',         'xxd hex+ascii'),
        '5': (f'md5sum "{target}" && sha1sum "{target}" && sha256sum "{target}"', 'hashes.txt', 'MD5 / SHA1 / SHA256'),
        '6': (f'readelf -a "{target}" 2>/dev/null',           'readelf.txt',     'ELF headers (si aplica)'),
        '7': (f'objdump -d "{target}" 2>/dev/null | head -200', 'disasm.txt',    'Desensamblado (200 líneas)'),
    }

    print(f"\n  {cy('Análisis disponibles:')}")
    for k, (_, _, desc) in analyses.items():
        print(f"    {cy(k)}. {desc}")
    print(f"    {cy('0')}. TODOS")

    opt = inp("Opción [0]: ") or '0'
    run_on = analyses if opt == '0' else {opt: analyses.get(opt, analyses['1'])}

    for k, (cmd, fname, desc) in run_on.items():
        out_f = session / fname
        print(f"\n  {cy('→')} {dm(desc)}: {dm(cmd[:60])}")
        o, e, _ = run_cmd(cmd)
        content = f"# {desc}\n# CMD: {cmd}\n# {'─'*50}\n\n{o or e}"
        save_file(out_f, content)
        preview = (o or e)[:400]
        if preview:
            print(preview)

    print(f"\n  {g('✓')} Todo en: {session}")
    pause()

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
