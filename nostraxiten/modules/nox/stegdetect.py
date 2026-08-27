import math
from pathlib import Path
from core.colors import cy, g, r, y, C
from core.utils import pause, inp, banner, hdr

def run():
    banner()
    hdr(20, "NOX_STEGDETECT", "Análisis de Entropía y LSB (Pure Python)")
    path = inp("Imagen a analizar: ")
    if not path or not Path(path).exists(): return

    def calc_entropy(data):
        if not data: return 0
        entropy = 0
        for i in range(256):
            p_i = data.count(i) / len(data)
            if p_i > 0: entropy -= p_i * math.log2(p_i)
        return entropy

    with open(path, 'rb') as f:
        data = f.read()
        ent = calc_entropy(data)
        
    print(f"\n  {cy('→')} Resultados del análisis:")
    print(f"    - Entropía Global: {C.Y}{ent:.4f}{C.RS} (Máx 8.0)")
    
    score = 0
    if ent > 7.9: score += 50
    
    lsb_bits = ""
    for byte in data[100:1100]:
        lsb_bits += str(byte & 1)
    
    print(f"    - Sospecha Esteganográfica: {C.R if score > 40 else C.G}{score}/100{C.RS}")
    if score > 40: print(f"    - {y('⚠')} Entropía extremadamente alta. Posible contenedor cifrado.")
    
    pause()

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
