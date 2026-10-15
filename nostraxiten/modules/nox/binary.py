import os
import re
import struct
import hashlib
import platform
import shutil
import urllib.request
import urllib.parse
import json
from pathlib import Path
from core.colors import cy, g, dm, r, y, C
from core.utils import new_session, save_file, pause, inp, banner, hdr
from config.settings import settings

def calculate_hashes(file_path):
    file_path = Path(file_path)
    h_md5 = hashlib.md5()
    h_sha1 = hashlib.sha1()
    h_sha256 = hashlib.sha256()
    
    with open(file_path, 'rb') as f:
        while chunk := f.read(65536):
            h_md5.update(chunk)
            h_sha1.update(chunk)
            h_sha256.update(chunk)
            
    return {
        "MD5": h_md5.hexdigest(),
        "SHA1": h_sha1.hexdigest(),
        "SHA256": h_sha256.hexdigest()
    }

def detect_file_type(data: bytes, file_path) -> str:
    file_path = Path(file_path)
    if len(data) >= 2 and data[:2] == b'MZ':
        arch = "Unknown PE"
        try:
            pe_offset = struct.unpack('<I', data[0x3c:0x40])[0]
            if data[pe_offset:pe_offset+4] == b'PE\x00\x00':
                machine = struct.unpack('<H', data[pe_offset+4:pe_offset+6])[0]
                if machine == 0x014c: arch = "PE32 (x86)"
                elif machine == 0x8664: arch = "PE32+ (x64 AMD64)"
                elif machine == 0xaa64: arch = "PE32+ (ARM64)"
                else: arch = f"PE (Machine 0x{machine:04x})"
        except Exception:
            arch = "PE Executable (MZ)"
        return f"Windows Executable: {arch}"
    
    if len(data) >= 4 and data[:4] == b'\x7fELF':
        bitness = "64-bit" if len(data) > 4 and data[4] == 2 else "32-bit"
        endian = "LSB" if len(data) > 5 and data[5] == 1 else "MSB"
        return f"Linux/Unix ELF Binary: {bitness} {endian}"
    
    if len(data) >= 4 and data[:4] in (b'\xfe\xed\xfa\xce', b'\xce\xfa\xed\xfe', b'\xfe\xed\xfa\xcf', b'\xcf\xfa\xed\xfe', b'\xca\xfe\xba\xbe'):
        return "macOS Mach-O Binary / Universal Fat"
    
    if len(data) >= 4 and data[:4] == b'PK\x03\x04':
        return "ZIP Archive / JAR / Office Document (OpenXML)"
    if len(data) >= 4 and data[:4] == b'%PDF':
        return "PDF Document"
    if len(data) >= 8 and data[:8] == b'\x89PNG\r\n\x1a\n':
        return "PNG Image"
    if len(data) >= 3 and data[:3] == b'\xff\xd8\xff':
        return "JPEG Image"
    if len(data) >= 6 and data[:6] in (b'GIF87a', b'GIF89a'):
        return "GIF Image"
    if len(data) >= 2 and data[:2] == b'\x1f\x8b':
        return "Gzip Compressed Archive"
    if len(data) >= 6 and data[:6] == b'7z\xbc\xaf\x27\x1c':
        return "7-Zip Archive"
    if len(data) >= 4 and data[:4] == b'Rar!\x1a\x07':
        return "RAR Archive"

    # Fallback to extension or file command if available
    if shutil.which("file"):
        try:
            import subprocess
            res = subprocess.run(["file", str(file_path)], capture_output=True, text=True, timeout=5)
            if res.returncode == 0:
                return res.stdout.strip()
        except Exception:
            pass

    return f"Generic Data / Extension {file_path.suffix or 'unknown'}"

def extract_strings(data: bytes, min_len: int = 6, limit: int = 2000):
    ascii_regex = re.compile(rb'[\x20-\x7e]{' + str(min_len).encode() + rb',}')
    matches = [m.decode('latin1') for m in ascii_regex.findall(data)]
    return matches[:limit]

def format_hexdump(data: bytes, max_bytes: int = 4096):
    lines = []
    chunk = data[:max_bytes]
    for i in range(0, len(chunk), 16):
        line_bytes = chunk[i:i+16]
        hex_part = " ".join(f"{b:02x}" for b in line_bytes)
        hex_part = f"{hex_part:<48}"
        ascii_part = "".join(chr(b) if 32 <= b <= 126 else "." for b in line_bytes)
        lines.append(f"{i:08x}  {hex_part}  |{ascii_part}|")
    if len(data) > max_bytes:
        lines.append(f"... [Truncado a {max_bytes} bytes de {len(data)} totales]")
    return "\n".join(lines)

def virustotal_lookup(sha256_hash: str):
    api_key = settings.virustotal_key
    if not api_key:
        return None, "API Key de VirusTotal no configurada (usa opción [98] en el menú principal)"
    try:
        url = f"https://www.virustotal.com/api/v3/files/{sha256_hash}"
        req = urllib.request.Request(url, headers={"x-apikey": api_key, "User-Agent": "Nostraxiten/1.7"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            attrs = data.get('data', {}).get('attributes', {})
            stats = attrs.get('last_analysis_stats', {})
            malicious = stats.get('malicious', 0)
            suspicious = stats.get('suspicious', 0)
            harmless = stats.get('harmless', 0)
            undetected = stats.get('undetected', 0)
            name = attrs.get('meaningful_name', '') or attrs.get('type_description', '')
            return {
                "name": name,
                "malicious": malicious,
                "suspicious": suspicious,
                "harmless": harmless,
                "undetected": undetected,
                "total": malicious + suspicious + harmless + undetected
            }, None
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None, "Hash no encontrado en VirusTotal (archivo desconocido / no reportado)"
        return None, f"HTTP Error {e.code}: {e.reason}"
    except Exception as e:
        return None, f"Error consultando VirusTotal: {e}"

def run():
    banner()
    hdr(15, "Binary Analysis", "Hashes + Magic Type + Hexdump + Strings + VirusTotal (Cross-Platform)")

    target = inp("Archivo a analizar: ")
    if not target or not Path(target).exists():
        print(f"  {r('✗')} Archivo no encontrado")
        pause()
        return

    file_path = Path(target)
    session = new_session('binary_analysis')

    print(f"\n  {cy('→')} Leyendo archivo...")
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
    except Exception as e:
        print(f"  {r('✗')} Error al abrir archivo: {e}")
        pause()
        return

    file_size = len(data)
    print(f"  {dm('·')} Tamaño: {file_size:,} bytes ({file_size / (1024*1024):.2f} MB)")

    # 1. Hashes
    print(f"\n  {cy('[1/5]')} Calculando Hashes Criptográficos...")
    hashes = calculate_hashes(file_path)
    hash_txt = "\n".join(f"{k:<8}: {v}" for k, v in hashes.items())
    for k, v in hashes.items():
        print(f"    {C.W}{k:<8}{C.RS}: {C.Y}{v}{C.RS}")
    save_file(session / 'hashes.txt', hash_txt)

    # 2. File Type / Magic
    print(f"\n  {cy('[2/5]')} Identificando formato y cabecera binaria...")
    file_type = detect_file_type(data, file_path)
    print(f"    {g('✓')} Tipo: {C.W}{file_type}{C.RS}")
    save_file(session / 'file_type.txt', file_type)

    # 3. Hexdump
    print(f"\n  {cy('[3/5]')} Generando Hexdump canónico...")
    hexdump_content = format_hexdump(data, max_bytes=4096)
    save_file(session / 'hexdump.txt', hexdump_content)
    # Preview first 10 lines
    preview_lines = "\n".join(hexdump_content.splitlines()[:10])
    print(f"{dm(preview_lines)}\n    {dm('... [Hexdump completo guardado en hexdump.txt]')}")

    # 4. Strings
    print(f"\n  {cy('[4/5]')} Extrayendo cadenas ASCII legibles (min 6 caracteres)...")
    strings_list = extract_strings(data, min_len=6, limit=5000)
    print(f"    {g('✓')} Extraídas {len(strings_list)} cadenas de texto.")
    save_file(session / 'strings.txt', "\n".join(strings_list))
    if strings_list:
        print(f"    {dm('Muestra inicial:')} {C.W}{', '.join(strings_list[:8])}{C.RS}")

    # 5. VirusTotal Lookup (Optional / Automatic if configured)
    print(f"\n  {cy('[5/5]')} Consulta a Inteligencia de Amenazas (VirusTotal)...")
    vt_res, vt_err = virustotal_lookup(hashes['SHA256'])
    if vt_res:
        m = vt_res['malicious']
        tot = vt_res['total']
        color = C.R if m > 0 else C.G
        print(f"    {color}[VT Detecciones: {m}/{tot}]{C.RS} {vt_res.get('name', '')}")
        save_file(session / 'virustotal.json', json.dumps(vt_res, indent=4))
    else:
        print(f"    {dm('·')} {vt_err}")

    print(f"\n  {g('✓')} Resultados guardados en: {g(str(session))}")
    pause()

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
