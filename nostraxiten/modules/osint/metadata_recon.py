"""
Metadata Recon — extracción de EXIF/GPS de imágenes y metadata general de archivos.
"""
import json
import os
from datetime import datetime
from pathlib import Path

from core.colors import cy, g, y, r, dm, w, C
from core.utils import new_session as new_case, save_file, pause, inp, banner, hdr


def ensure_pillow():
    try:
        import PIL  # noqa: F401
        return True
    except ImportError:
        from core.utils import pip_install
        print(f"  {y('⚠')} Pillow no está instalado, instalando...")
        pip_install('Pillow')
        try:
            import PIL  # noqa: F401
            return True
        except ImportError:
            return False


def _dms_to_decimal(dms, ref):
    try:
        degrees, minutes, seconds = dms
        decimal = float(degrees) + float(minutes) / 60 + float(seconds) / 3600
        if ref in ('S', 'W'):
            decimal = -decimal
        return round(decimal, 6)
    except Exception:
        return None


def extract_exif(path):
    """Extrae EXIF completo + GPS de una imagen. Devuelve dict con 'exif', 'gps', 'error'."""
    if not ensure_pillow():
        return {'error': "Pillow no disponible ('pip install Pillow')"}

    from PIL import Image
    from PIL import ExifTags

    result = {'exif': {}, 'gps': None, 'error': None}
    try:
        img = Image.open(path)
        result['format'] = img.format
        result['size'] = img.size
        result['mode'] = img.mode

        raw_exif = img.getexif()
        if not raw_exif:
            return result

        tag_map = {v: k for k, v in ExifTags.TAGS.items()}
        exif_data = {}
        for tag_id, value in raw_exif.items():
            tag_name = ExifTags.TAGS.get(tag_id, tag_id)
            if isinstance(value, bytes):
                try:
                    value = value.decode(errors='replace')
                except Exception:
                    value = str(value)
            exif_data[str(tag_name)] = value
        result['exif'] = exif_data

        gps_info = raw_exif.get_ifd(ExifTags.IFD.GPSInfo) if hasattr(ExifTags, 'IFD') else None
        if gps_info:
            gps_tags = {ExifTags.GPSTAGS.get(k, k): v for k, v in gps_info.items()}
            lat = gps_tags.get('GPSLatitude')
            lat_ref = gps_tags.get('GPSLatitudeRef')
            lon = gps_tags.get('GPSLongitude')
            lon_ref = gps_tags.get('GPSLongitudeRef')
            if lat and lon:
                lat_dec = _dms_to_decimal(lat, lat_ref)
                lon_dec = _dms_to_decimal(lon, lon_ref)
                if lat_dec is not None and lon_dec is not None:
                    result['gps'] = {
                        'lat': lat_dec, 'lon': lon_dec,
                        'maps_url': f'https://www.google.com/maps?q={lat_dec},{lon_dec}',
                        'raw': {str(k): str(v) for k, v in gps_tags.items()},
                    }
    except Exception as e:
        result['error'] = str(e)
    return result


def file_metadata(path):
    p = Path(path)
    stat = p.stat()
    return {
        'name': p.name,
        'size_bytes': stat.st_size,
        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
        'created': datetime.fromtimestamp(getattr(stat, 'st_birthtime', stat.st_ctime)).isoformat(),
        'extension': p.suffix.lower(),
    }


def run(path=None, session_dir=None, silent=False, graph=None):
    if not silent:
        banner()
        hdr(30, "Metadata / EXIF Analyzer", "Extracción de metadatos y geolocalización GPS de imágenes")
        path = path or inp("Ruta al archivo de imagen: ")
        if not path or not os.path.exists(path):
            print(f"\n  {r('✗')} Archivo no encontrado.")
            pause()
            return None

    results = {'path': str(path), 'timestamp': str(datetime.now())}
    results['file'] = file_metadata(path)

    ext = Path(path).suffix.lower()
    if ext in ('.jpg', '.jpeg', '.tiff', '.tif', '.png', '.heic', '.webp'):
        results['image'] = extract_exif(path)
    else:
        results['image'] = {'note': 'Extensión no soportada para EXIF (solo imágenes).'}

    if graph is not None and results.get('image', {}).get('gps'):
        gps = results['image']['gps']
        loc_name = f"{gps['lat']},{gps['lon']}"
        graph.add_entity('gps_location', loc_name, {'maps_url': gps['maps_url']})
        graph.add_entity('file', str(path), {})
        graph.add_relation(str(path), loc_name, 'geotagged_at')

    if not silent:
        _print_summary(results)
        case = new_case(f'metadata_{Path(path).stem}')
        save_file(case / 'metadata.json', json.dumps(results, indent=2, default=str))
        print(f"\n  {g('✓')} Resultados guardados en: {case}")
        pause()

    return results


def _print_summary(results):
    print(f"\n  {C.BD}{C.CY}── METADATA: {results['file']['name']} ──{C.RS}\n")
    f = results['file']
    print(f"  {w('Tamaño')}: {f['size_bytes']} bytes    {w('Modificado')}: {f['modified']}")

    img = results.get('image', {})
    if img.get('error'):
        print(f"\n  {y('⚠')} {img['error']}")
        return
    if img.get('note'):
        print(f"\n  {dm(img['note'])}")
        return

    print(f"\n  {w('Formato')}: {img.get('format')}   {w('Dimensiones')}: {img.get('size')}")
    exif = img.get('exif', {})
    interesting = ['Make', 'Model', 'DateTime', 'Software', 'Artist', 'Copyright']
    for key in interesting:
        if key in exif:
            print(f"  {cy(key)}: {exif[key]}")

    gps = img.get('gps')
    if gps:
        print(f"\n  {r('📍 GPS ENCONTRADO')}: {gps['lat']}, {gps['lon']}")
        print(f"  {cy('→')} {gps['maps_url']}")
    else:
        print(f"\n  {dm('Sin datos GPS en la imagen.')}")


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
