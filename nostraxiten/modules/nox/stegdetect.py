import math
import string
from pathlib import Path
from core.colors import cy, g, r, y, dm, C
from core.utils import pause, inp, banner, hdr

def calc_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    entropy = 0.0
    length = len(data)
    # Using bytearray counting for speed
    byte_counts = [0] * 256
    for b in data:
        byte_counts[b] += 1
    for count in byte_counts:
        if count > 0:
            p_i = count / length
            entropy -= p_i * math.log2(p_i)
    return entropy

def check_trailing_data(data: bytes, ext: str):
    """Detects data hidden after official image EOF markers (Overlay/Appended stego)."""
    trailing = b""
    ext = ext.lower()
    if ext in ('.jpg', '.jpeg'):
        eof_index = data.rfind(b'\xff\xd9')
        if eof_index != -1 and eof_index + 2 < len(data):
            trailing = data[eof_index + 2:]
    elif ext == '.png':
        iend = b'IEND\xae\x42\x60\x82'
        eof_index = data.rfind(iend)
        if eof_index != -1 and eof_index + len(iend) < len(data):
            trailing = data[eof_index + len(iend):]
    elif ext == '.gif':
        eof_index = data.rfind(b'\x00\x3b')
        if eof_index != -1 and eof_index + 2 < len(data):
            trailing = data[eof_index + 2:]
    return trailing

def analyze_lsb(data: bytes, sample_size: int = 4000):
    """Analyzes Least Significant Bits for hidden data and uniformity."""
    sample = data[100:100 + sample_size] if len(data) > 100 + sample_size else data
    if not sample:
        return 0.5, ""

    bits = [b & 1 for b in sample]
    ones = sum(bits)
    zeros = len(bits) - ones
    ratio = ones / len(bits) if bits else 0.5

    # Try extracting ASCII bytes from LSB
    extracted_chars = []
    for i in range(0, len(bits) - 7, 8):
        byte_val = 0
        for bit in bits[i:i+8]:
            byte_val = (byte_val << 1) | bit
        if 32 <= byte_val <= 126:
            extracted_chars.append(chr(byte_val))
        elif byte_val == 0:
            if len(extracted_chars) >= 4:
                break
            extracted_chars = []
        else:
            if len(extracted_chars) < 6:
                extracted_chars = []

    extracted_text = "".join(extracted_chars)
    return ratio, extracted_text

def run():
    banner()
    hdr(20, "NOX_STEGDETECT", "Análisis Forense de Entropía, EOF y LSB")
    img_path = inp("Ruta de imagen a analizar: ")
    if not img_path:
        return
    p = Path(img_path)
    if not p.exists() or not p.is_file():
        print(f"  {r('✘')} El archivo no existe.")
        pause()
        return

    with open(p, 'rb') as f:
        data = f.read()

    file_size = len(data)
    ent = calc_entropy(data)
    score = 0
    findings = []

    print(f"\n  {cy('→')} Archivo: {p.name} ({file_size:,} bytes)")
    print(f"  {cy('→')} Resultados del análisis:")
    print(f"    - Entropía Shannon Global: {C.Y}{ent:.4f}{C.RS} / 8.0000")

    if ent > 7.92:
        score += 45
        findings.append("Entropía global extremadamente alta (> 7.92, típico de payloads cifrados o comprimidos)")
    elif ent > 7.75:
        score += 25
        findings.append("Entropía elevada (> 7.75)")

    # 1. Check Trailing Overlay
    trailing = check_trailing_data(data, p.suffix)
    if trailing:
        score += 45
        trail_ent = calc_entropy(trailing)
        has_zip = b'PK\x03\x04' in trailing
        has_rar = b'Rar!' in trailing
        archive_type = " (Contiene archivo ZIP)" if has_zip else (" (Contiene archivo RAR)" if has_rar else "")
        findings.append(f"Overlay detectado: {len(trailing)} bytes después del marcador EOF{archive_type} [Entropía: {trail_ent:.3f}]")

    # 2. Check Embedded Archive Signature anywhere
    if b'PK\x03\x04' in data and not trailing:
        score += 35
        findings.append("Firma PK (ZIP/Office) encontrada dentro de los bytes del archivo.")

    # 3. LSB Analysis
    ratio, extracted_text = analyze_lsb(data)
    lsb_bias = abs(ratio - 0.5)
    print(f"    - Distribución LSB (1s ratio): {ratio:.3f} (Desviación: {lsb_bias:.3f})")
    
    # In encrypted LSB stego, ratio is extremely close to 0.5 (bias < 0.015 in non-compressed structures)
    if lsb_bias < 0.01 and len(data) > 5000:
        score += 20
        findings.append("Distribución LSB perfectamente uniforme (entropía binaria plana, sospechoso de esteganografía LSB)")

    if len(extracted_text) >= 6:
        score += 35
        findings.append(f"Texto ASCII reconstruido en primeros LSB: \"{extracted_text[:40]}\"")

    score = min(100, score)
    color = C.R if score >= 60 else (C.Y if score >= 30 else C.G)
    print(f"\n  {C.W}Puntuación de Sospecha Esteganográfica:{C.RS} {color}{score}/100{C.RS}")

    if findings:
        print(f"\n  {cy('Indicadores detectados:')}")
        for f in findings:
            print(f"    {r('!')} {f}")
    else:
        print(f"\n  {g('✓')} No se encontraron anomalías evidentes ni datos residuales.")

    pause()

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
