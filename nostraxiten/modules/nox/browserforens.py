import os
import sys
import subprocess
import shutil
import platform
import csv
import json
import sqlite3
import base64
from datetime import datetime, timedelta
from pathlib import Path
from core.colors import C, cy, g, r, y, dm
from core.utils import new_session, save_file, pause, inp, banner, hdr
from core.env import IS_TERMUX, IS_ROOT

# Variable global para win32crypt
win32crypt = None

def run():
    banner()
    hdr(25, "NOX_BROWSERFORENS", "Análisis forense de navegadores (Historial, Cookies, Contraseñas, Descargas, Extensiones)")

    session = new_session('browser_forensics')
    
    # Instalación upfront de pywin32 para Windows
    if platform.system() == 'Windows':
        global win32crypt
        if win32crypt is None:
            try:
                import win32crypt as w3c
                win32crypt = w3c
            except ImportError:
                print(f"  {y('⚠')} pywin32 (necesario para descifrar contraseñas/cookies en Windows) no encontrado.")
                resp = inp("¿Intentar instalar pywin32 ahora? [s/N]: ")
                if resp.lower() == 's':
                    try:
                        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pywin32', '--break-system-packages', '-q'])
                        import win32crypt as w3c
                        win32crypt = w3c
                        print(f"  {g('✓')} pywin32 instalado exitosamente.")
                    except Exception as e:
                        print(f"  {r('✗')} Falló la instalación de pywin32: {e}. Las contraseñas y cookies de Windows permanecerán cifradas.")
                else:
                    print(f"  {y('⚠')} pywin32 no será instalado. Las contraseñas y cookies de Windows permanecerán cifradas.")

    browser_paths = get_browser_paths()
    total_cookies = 0
    total_passwords = 0
    total_history = 0
    high_risk_extensions = 0

    selected_modules = []
    print(f"\n  {cy('Sub-módulos disponibles:')}")
    print(f"    {cy('A')}. Historial")
    print(f"    {cy('B')}. Cookies")
    print(f"    {cy('C')}. Contraseñas Guardadas")
    print(f"    {cy('D')}. Descargas")
    print(f"    {cy('E')}. Extensiones Instaladas")
    print(f"    {cy('F')}. Firefox Específico (Historial, Cookies, Contraseñas)")
    choice = inp("Selecciona módulos (ej: ABC, todos): ") or "ABCDE"
    if choice.lower() == 'todos':
        selected_modules = ['A', 'B', 'C', 'D', 'E', 'F']
    else:
        selected_modules = list(choice.upper())

    for browser_name, paths in browser_paths.items():
        if not paths:
            print(f"  {dm('·')} No se encontraron perfiles para {browser_name}.")
            continue

        print(f"\n  {C.BD}{C.CY}--- Procesando {browser_name} ---{C.RS}")
        for profile_path in paths:
            print(f"  {dm('·')} Perfil: {profile_path}")
            browser_session_dir = session / browser_name.lower() / profile_path.name
            browser_session_dir.mkdir(parents=True, exist_ok=True)

            if 'A' in selected_modules and browser_name != "Firefox":
                recs = extract_chromium_history(profile_path, browser_session_dir)
                total_history += len(recs)

            if 'B' in selected_modules and browser_name != "Firefox":
                recs = extract_chromium_cookies(profile_path, browser_session_dir, browser_name)
                total_cookies += len(recs)

            if 'C' in selected_modules and browser_name != "Firefox":
                recs = extract_chromium_passwords(profile_path, browser_session_dir, browser_name)
                total_passwords += len(recs)

            if 'D' in selected_modules and browser_name != "Firefox":
                extract_chromium_downloads(profile_path, browser_session_dir)

            if 'E' in selected_modules and browser_name != "Firefox":
                risk = extract_chromium_extensions(profile_path, browser_session_dir)
                high_risk_extensions += risk

            if 'F' in selected_modules and browser_name == "Firefox":
                h, c, p = extract_firefox_data(profile_path, browser_session_dir)
                total_history += h
                total_cookies += c
                total_passwords += p

    print(f"\n  {C.BD}{C.CY}--- Resumen del Análisis de Navegadores ---{C.RS}")
    print(f"  {g('✓')} Navegadores encontrados: {', '.join([b for b, p in browser_paths.items() if p])}")
    print(f"  {g('✓')} Total de entradas de historial: {total_history}")
    print(f"  {g('✓')} Total de cookies: {total_cookies}")
    print(f"  {g('✓')} Total de contraseñas (cifradas/descifradas): {total_passwords}")
    if high_risk_extensions > 0:
        print(f"  {r('✗')} Extensiones de alto riesgo detectadas: {high_risk_extensions}")
    else:
        print(f"  {g('✓')} No se detectaron extensiones de alto riesgo.")
    print(f"\n  {g('✓')} Todos los resultados guardados en {session}")
    pause()


# --- Quick extractor for NOXRECON ---
def quick_extract_history(session_dir):
    browser_paths = get_browser_paths()
    total_history = 0
    for browser_name, paths in browser_paths.items():
        if not paths: continue
        for profile_path in paths:
            browser_session_dir = session_dir / browser_name.lower() / profile_path.name
            browser_session_dir.mkdir(parents=True, exist_ok=True)
            if browser_name != "Firefox":
                total_history += len(extract_chromium_history(profile_path, browser_session_dir, quiet=True))
            else:
                h, _, _ = extract_firefox_data(profile_path, browser_session_dir, only_history=True, quiet=True)
                total_history += h
    return total_history


# --- Helpers ---

def get_browser_paths():
    browser_paths = {
        "Chrome": [], "Brave": [], "Edge": [], "Opera": [], "Firefox": []
    }
    
    if platform.system() == 'Windows':
        local_app_data = Path(os.getenv('LOCALAPPDATA'))
        app_data = Path(os.getenv('APPDATA'))

        for browser, rel_path in [
            ("Chrome", r"Google\Chrome\User Data"),
            ("Brave", r"BraveSoftware\Brave-Browser\User Data"),
            ("Edge", r"Microsoft\Edge\User Data"),
            ("Opera", r"Opera Software\Opera Stable\User Data"), 
        ]:
            path = local_app_data / rel_path
            if path.is_dir():
                for profile_dir in path.glob('Profile*'):
                    if profile_dir.is_dir(): browser_paths[browser].append(profile_dir)
                if not browser_paths[browser] and (path / 'Default').is_dir():
                    browser_paths[browser].append(path / 'Default')

        firefox_path = app_data / r"Mozilla\Firefox\Profiles"
        if firefox_path.is_dir():
            for profile_dir in firefox_path.glob('*.default-release'):
                if profile_dir.is_dir(): browser_paths["Firefox"].append(profile_dir)
            if not browser_paths["Firefox"]:
                for profile_dir in firefox_path.glob('*'):
                    if profile_dir.is_dir(): browser_paths["Firefox"].append(profile_dir)

    elif platform.system() == 'Linux':
        home = Path.home()
        for browser, rel_path in [
            ("Chrome", ".config/google-chrome"),
            ("Brave", ".config/BraveSoftware/Brave-Browser"),
            ("Chromium", ".config/chromium"),
            ("Opera", ".config/opera"),
        ]:
            path = home / rel_path
            if path.is_dir():
                for profile_dir in path.glob('Profile*'):
                    if profile_dir.is_dir(): browser_paths[browser].append(profile_dir)
                if not browser_paths[browser] and (path / 'Default').is_dir():
                    browser_paths[browser].append(path / 'Default')

        firefox_path = home / ".mozilla/firefox"
        if firefox_path.is_dir():
            for profile_dir in firefox_path.glob('*.default-release'):
                if profile_dir.is_dir(): browser_paths["Firefox"].append(profile_dir)
            if not browser_paths["Firefox"]:
                for profile_dir in firefox_path.glob('*'):
                    if profile_dir.is_dir() and (profile_dir / 'places.sqlite').is_file():
                        browser_paths["Firefox"].append(profile_dir)

    elif IS_TERMUX:
        chrome_android_path = Path('/data/data/com.android.chrome/app_chrome/Default/')
        if IS_ROOT and chrome_android_path.is_dir():
            browser_paths["Chrome"].append(chrome_android_path)

        firefox_android_path = Path('/data/data/org.mozilla.firefox/files/mozilla/')
        if IS_ROOT and firefox_android_path.is_dir():
            for profile_dir in firefox_android_path.glob('*.default'):
                if profile_dir.is_dir(): browser_paths["Firefox"].append(profile_dir)
    return browser_paths

def chrome_timestamp_to_datetime(chrome_ts):
    if chrome_ts == 0: return None
    chrome_epoch_offset = 11644473600000000 
    return datetime(1970, 1, 1) + timedelta(microseconds=chrome_ts - chrome_epoch_offset)

def decrypt_windows_password(encrypted_value):
    if not win32crypt:
        return "Requires pywin32 for decryption"
    try:
        if encrypted_value.startswith(b'v10') or encrypted_value.startswith(b'v11'):
            encrypted_value = encrypted_value[3:]
        _, decrypted_data = win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)
        return decrypted_data.decode('utf-8', errors='ignore')
    except Exception as e:
        return f"Decryption failed: {e}"

def decrypt_linux_password(encrypted_value, browser_type):
    return f"Encrypted (Linux - requiere keyring/AES): {base64.b64encode(encrypted_value).decode()}"

def decrypt_firefox_nss(encrypted_value_b64):
    return f"Encrypted (Firefox NSS - requiere libnss3/master password): {encrypted_value_b64}"

def extract_chromium_history(profile_path, session_dir, quiet=False):
    records = []
    history_db_path = profile_path / 'History'
    if history_db_path.is_file():
        temp_db = session_dir / 'History.sqlite'
        try:
            shutil.copy2(history_db_path, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT url, title, visit_count, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 500")
            for url, title, visit_count, last_visit_time in cursor.fetchall():
                dt = chrome_timestamp_to_datetime(last_visit_time)
                records.append({
                    "date": dt.strftime('%Y-%m-%d %H:%M:%S') if dt else "N/A",
                    "url": url,
                    "title": title,
                    "visit_count": visit_count
                })
            conn.close()
            csv_path = session_dir / 'history.csv'
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=["date", "url", "title", "visit_count"])
                writer.writeheader()
                writer.writerows(records)
            if not quiet: print(f"    {g('✓')} Historial guardado: {csv_path}")
        except Exception as e:
            if not quiet: print(f"    {r('✗')} Error historial: {e}")
    else:
        if not quiet: print(f"    {dm('·')} Historial no encontrado")
    return records

def extract_chromium_cookies(profile_path, session_dir, browser_name, quiet=False):
    records = []
    cookies_db_path = profile_path / 'Cookies'
    if cookies_db_path.is_file():
        temp_db = session_dir / 'Cookies.sqlite'
        try:
            shutil.copy2(cookies_db_path, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT host_key, name, value, encrypted_value, expires_utc, is_secure, is_httponly FROM cookies")
            for host_key, name, value, encrypted_value, expires_utc, is_secure, is_httponly in cursor.fetchall():
                decrypted_value = value.decode('utf-8', errors='ignore')
                if encrypted_value:
                    if platform.system() == 'Windows':
                        decrypted_value = decrypt_windows_password(encrypted_value)
                    elif platform.system() == 'Linux':
                        decrypted_value = decrypt_linux_password(encrypted_value, browser_name)
                    else:
                        decrypted_value = f"Encrypted: {base64.b64encode(encrypted_value).decode()}"
                
                dt_expires = chrome_timestamp_to_datetime(expires_utc)
                records.append({
                    "domain": host_key,
                    "name": name,
                    "value": decrypted_value,
                    "expires": dt_expires.strftime('%Y-%m-%d %H:%M:%S') if dt_expires else "N/A",
                    "secure": bool(is_secure),
                    "httponly": bool(is_httponly)
                })
            conn.close()
            csv_path = session_dir / 'cookies.csv'
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=["domain", "name", "value", "expires", "secure", "httponly"])
                writer.writeheader()
                writer.writerows(records)
            if not quiet: print(f"    {g('✓')} Cookies guardadas: {csv_path}")
        except Exception as e:
            if not quiet: print(f"    {r('✗')} Error cookies: {e}")
    else:
        if not quiet: print(f"    {dm('·')} Cookies no encontradas")
    return records

def extract_chromium_passwords(profile_path, session_dir, browser_name, quiet=False):
    records = []
    login_db_path = profile_path / 'Login Data'
    if login_db_path.is_file():
        if not quiet:
            print(f"\n  {C.R}⚠️ ADVERTENCIA LEGAL: Extracción de credenciales locales.{C.RS}")
            if inp("¿Continuar? [s/N]: ").lower() != 's':
                return []

        temp_db = session_dir / 'Login_Data.sqlite'
        try:
            shutil.copy2(login_db_path, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value, date_created FROM logins")
            for origin_url, username_value, password_value, date_created in cursor.fetchall():
                decrypted_password = ""
                if password_value:
                    if platform.system() == 'Windows':
                        decrypted_password = decrypt_windows_password(password_value)
                    elif platform.system() == 'Linux':
                        decrypted_password = decrypt_linux_password(password_value, browser_name)
                    else:
                        decrypted_password = f"Encrypted: {base64.b64encode(password_value).decode()}"
                
                dt_created = chrome_timestamp_to_datetime(date_created)
                records.append({
                    "url": origin_url,
                    "username": username_value,
                    "password": decrypted_password,
                    "date_created": dt_created.strftime('%Y-%m-%d %H:%M:%S') if dt_created else "N/A"
                })
            conn.close()
            csv_path = session_dir / 'passwords.csv'
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=["url", "username", "password", "date_created"])
                writer.writeheader()
                writer.writerows(records)
            if not quiet: print(f"    {g('✓')} Contraseñas guardadas: {csv_path}")
        except Exception as e:
            if not quiet: print(f"    {r('✗')} Error contraseñas: {e}")
    else:
        if not quiet: print(f"    {dm('·')} Login Data no encontrado")
    return records

def extract_chromium_downloads(profile_path, session_dir, quiet=False):
    history_db_path = profile_path / 'History'
    if history_db_path.is_file():
        temp_db = session_dir / 'History_downloads.sqlite'
        try:
            shutil.copy2(history_db_path, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT target_path, tab_url, total_bytes, start_time, end_time, state FROM downloads")
            records = []
            for target_path, tab_url, total_bytes, start_time, end_time, state in cursor.fetchall():
                dt_start = chrome_timestamp_to_datetime(start_time)
                dt_end = chrome_timestamp_to_datetime(end_time)
                records.append({
                    "target_path": target_path,
                    "source_url": tab_url,
                    "size_bytes": total_bytes,
                    "start_time": dt_start.strftime('%Y-%m-%d %H:%M:%S') if dt_start else "N/A",
                    "end_time": dt_end.strftime('%Y-%m-%d %H:%M:%S') if dt_end else "N/A",
                    "state": state
                })
            conn.close()
            csv_path = session_dir / 'downloads.csv'
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=["target_path", "source_url", "size_bytes", "start_time", "end_time", "state"])
                writer.writeheader()
                writer.writerows(records)
            if not quiet: print(f"    {g('✓')} Descargas guardadas: {csv_path}")
        except Exception as e:
            if not quiet: print(f"    {r('✗')} Error descargas: {e}")

def extract_chromium_extensions(profile_path, session_dir, quiet=False):
    high_risk_count = 0
    extensions_path = profile_path / 'Extensions'
    if extensions_path.is_dir():
        records = []
        for ext_id_path in extensions_path.iterdir():
            if ext_id_path.is_dir():
                for version_path in ext_id_path.iterdir():
                    if version_path.is_dir():
                        manifest_path = version_path / 'manifest.json'
                        if manifest_path.is_file():
                            try:
                                manifest = json.loads(manifest_path.read_text(errors='ignore'))
                                permissions = manifest.get('permissions', [])
                                
                                risk_score = sum(1 for p in permissions if p in ["tabs", "webRequest", "cookies", "password", "nativeMessaging", "proxy", "unlimitedStorage", "debugger"])
                                
                                risk_level = "Bajo"
                                if risk_score >= 3: 
                                    risk_level = "Alto"
                                    high_risk_count += 1
                                elif risk_score >= 1: 
                                    risk_level = "Medio"

                                records.append({
                                    "name": manifest.get('name', 'N/A'),
                                    "version": manifest.get('version', 'N/A'),
                                    "description": str(manifest.get('description', 'N/A'))[:50],
                                    "permissions": ", ".join(permissions),
                                    "risk": risk_level
                                })
                            except: pass
        if records:
            save_file(session_dir / 'extensions.json', json.dumps(records, indent=4))
            if not quiet: print(f"    {g('✓')} Extensiones guardadas")
    return high_risk_count

def extract_firefox_data(profile_path, session_dir, only_history=False, quiet=False):
    h, c, p = 0, 0, 0
    places_db_path = profile_path / 'places.sqlite'
    if places_db_path.is_file():
        temp_db = session_dir / 'firefox_places.sqlite'
        try:
            shutil.copy2(places_db_path, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT url, title, visit_count, last_visit_date FROM moz_places ORDER BY last_visit_date DESC LIMIT 500")
            records = []
            for url, title, visit_count, last_visit_date in cursor.fetchall():
                if last_visit_date:
                    dt = datetime(1970, 1, 1) + timedelta(microseconds=last_visit_date)
                    dts = dt.strftime('%Y-%m-%d %H:%M:%S')
                else: dts = "N/A"
                records.append({"date": dts, "url": url, "title": title, "visit_count": visit_count})
            conn.close()
            with open(session_dir / 'firefox_history.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=["date", "url", "title", "visit_count"])
                writer.writeheader()
                writer.writerows(records)
            h = len(records)
            if not quiet: print(f"    {g('✓')} Historial Firefox guardado")
        except Exception as e:
            if not quiet: print(f"    {r('✗')} Error Firefox historial: {e}")

    if only_history: return h, c, p

    cookies_db_path = profile_path / 'cookies.sqlite'
    if cookies_db_path.is_file():
        temp_db = session_dir / 'firefox_cookies.sqlite'
        try:
            shutil.copy2(cookies_db_path, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT host, name, value, creationTime, lastAccessed, expiry, isSecure, isHttpOnly FROM moz_cookies")
            records = []
            for host, name, value, creationTime, lastAccessed, expiry, isSecure, isHttpOnly in cursor.fetchall():
                dt_created = datetime(1970, 1, 1) + timedelta(microseconds=creationTime)
                dt_expires = datetime.fromtimestamp(expiry)
                records.append({
                    "domain": host, "name": name, "value": value,
                    "created": dt_created.strftime('%Y-%m-%d %H:%M:%S'),
                    "expires": dt_expires.strftime('%Y-%m-%d %H:%M:%S'),
                    "secure": bool(isSecure), "httponly": bool(isHttpOnly)
                })
            conn.close()
            with open(session_dir / 'firefox_cookies.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=["domain", "name", "value", "created", "expires", "secure", "httponly"])
                writer.writeheader()
                writer.writerows(records)
            c = len(records)
            if not quiet: print(f"    {g('✓')} Cookies Firefox guardadas")
        except Exception as e:
            if not quiet: print(f"    {r('✗')} Error Firefox cookies: {e}")

    logins_json_path = profile_path / 'logins.json'
    if logins_json_path.is_file():
        if not quiet:
            print(f"\n  {C.R}⚠️ ADVERTENCIA LEGAL: Extracción de credenciales.{C.RS}")
            if inp("¿Continuar? [s/N]: ").lower() != 's':
                return h, c, p
        try:
            logins_data = json.loads(logins_json_path.read_text(errors='ignore'))
            records = []
            for login in logins_data.get('logins', []):
                e_u = login.get('encryptedUsername', '')
                e_p = login.get('encryptedPassword', '')
                records.append({
                    "hostname": login.get('hostname', 'N/A'),
                    "username": decrypt_firefox_nss(e_u),
                    "password": decrypt_firefox_nss(e_p),
                    "timeCreated": datetime.fromtimestamp(login.get('timeCreated', 0) / 1000000).strftime('%Y-%m-%d %H:%M:%S')
                })
            save_file(session_dir / 'firefox_passwords.json', json.dumps(records, indent=4))
            p = len(records)
            if not quiet: print(f"    {g('✓')} Contraseñas Firefox guardadas")
        except Exception as e:
            if not quiet: print(f"    {r('✗')} Error Firefox contraseñas: {e}")

    return h, c, p

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
