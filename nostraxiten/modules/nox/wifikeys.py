import subprocess
import re
import json
import configparser
import platform
import xml.etree.ElementTree as ET
from pathlib import Path
from core.colors import cy, g, r, y, dm, C
from core.utils import new_session, save_file, pause, banner, hdr
from core.env import IS_TERMUX, IS_ROOT

def run():
    banner()
    hdr(24, "NOX_WIFIKEYS", "Extracción forense de redes WiFi guardadas")

    session = new_session('wifi_keys')
    results = extract_wifi(session)
    
    if results:
        print(f"\n  {C.W}{'SSID':<25} {'Auth':<15} {'Password':<25} {'Notes':<20}{C.RS}")
        print(f"  {dm('─' * 85)}")
        for r in results:
            password_display = r['Password'] if len(r['Password']) < 20 else r['Password'][:17] + "..."
            print(f"  {C.CY}{r['SSID'][:25]:<25}{C.RS} {r['Auth'][:15]:<15} {C.G}{password_display:<25}{C.RS} {dm(r['Notes'][:20]):<20}")

        print(f"\n  {g('✓')} {len(results)} perfiles WiFi guardados en {session}")
    else:
        print(f"\n  {y('⚠')} No se encontraron perfiles WiFi o no se pudieron extraer.")
    pause()

def extract_wifi(session_dir=None, quiet=False):
    results = []
    
    if platform.system() == 'Windows':
        if not quiet: print(f"  {cy('→')} Extrayendo perfiles WiFi en Windows...")
        try:
            cmd = 'netsh wlan show profiles'
            resultado = subprocess.run(cmd, shell=True, capture_output=True,
                                       text=True, encoding='utf-8',
                                       errors='replace')
            profiles_output = resultado.stdout
            profile_names = re.findall(r"(?:All User Profile|Perfil de todos los usuarios)\s*:\s*(.*)", profiles_output)

            for profile_name in profile_names:
                profile_name = profile_name.strip()
                if not quiet: print(f"    {dm('·')} Procesando perfil: {profile_name}")
                cmd = f'netsh wlan show profile name="{profile_name}" key=clear'
                resultado = subprocess.run(cmd, shell=True, capture_output=True,
                                           text=True, encoding='utf-8',
                                           errors='replace')
                profile_output = resultado.stdout

                ssid_match = re.search(r"(?:SSID name|Nombre SSID)\s*:\s*(.*)", profile_output)
                auth_match = re.search(r"(?:Authentication|Autenticación)\s*:\s*(.*)", profile_output)
                key_match = re.search(r"(?:Key Content|Contenido de la clave)\s*:\s*(.*)", profile_output)
                mac_match = re.search(r"BSSID\s*:\s*([0-9A-Fa-f:]{17})", profile_output)
                last_conn_match = re.search(r"Time of last connection\s*:\s*(.*)", profile_output)

                ssid = ssid_match.group(1).strip() if ssid_match else profile_name
                auth = auth_match.group(1).strip() if auth_match else "Unknown"
                password = key_match.group(1).strip() if key_match else "None/Encrypted"
                mac = mac_match.group(1).strip() if mac_match else "N/A"
                last_conn = last_conn_match.group(1).strip() if last_conn_match else "N/A"

                results.append({
                    "SSID": ssid,
                    "Auth": auth,
                    "Password": password,
                    "MAC": mac,
                    "Last_Connection": last_conn,
                    "Notes": ""
                })
        except Exception as e:
            if not quiet: print(f"  {r('✗')} Error en Windows WiFi: {e}")

    elif platform.system() == 'Linux':
        if not quiet: print(f"  {cy('→')} Extrayendo perfiles WiFi en Linux...")
        if not IS_ROOT and not quiet:
            print(f"  {y('⚠')} Se recomienda ejecutar como ROOT para acceder a todos los perfiles de NetworkManager.")

        nm_path = Path('/etc/NetworkManager/system-connections/')
        if nm_path.is_dir():
            for conf_file in nm_path.glob('*.nmconnection'):
                try:
                    config = configparser.ConfigParser()
                    config.read(conf_file)

                    ssid = config.get('wifi', 'ssid', fallback='N/A')
                    psk = config.get('wifi-security', 'psk', fallback='None/Encrypted')
                    auth_alg = config.get('wifi-security', 'auth-alg', fallback='N/A')
                    key_mgmt = config.get('wifi-security', 'key-mgmt', fallback='N/A')

                    results.append({
                        "SSID": ssid,
                        "Auth": f"{auth_alg}/{key_mgmt}",
                        "Password": psk,
                        "MAC": "N/A",
                        "Last_Connection": "N/A",
                        "Notes": f"NetworkManager: {conf_file.name}"
                    })
                except Exception as e:
                    if not quiet: print(f"    {y('⚠')} Error al leer {conf_file.name}: {e}")

        wpa_supp_path = Path('/etc/wpa_supplicant/wpa_supplicant.conf')
        if wpa_supp_path.is_file():
            if not quiet: print(f"  {dm('·')} Leyendo {wpa_supp_path}...")
            try:
                content = wpa_supp_path.read_text()
                networks = re.findall(r'network={\s*[^}]+ssid="([^"]+)"\s*[^}]+psk="([^"]+)"', content)
                for ssid, psk in networks:
                    results.append({
                        "SSID": ssid,
                        "Auth": "WPA/WPA2 PSK",
                        "Password": psk,
                        "MAC": "N/A",
                        "Last_Connection": "N/A",
                        "Notes": f"wpa_supplicant.conf"
                    })
            except Exception as e:
                if not quiet: print(f"    {y('⚠')} Error al leer {wpa_supp_path}: {e}")

    elif IS_TERMUX:
        if not quiet: print(f"  {cy('→')} Extrayendo perfiles WiFi en Termux/Android...")
        wifi_config_xml = Path('/data/misc/wifi/WifiConfigStore.xml')
        wpa_supp_sdcard = Path('/sdcard/wpa_supplicant.conf')

        if IS_ROOT and wifi_config_xml.is_file():
            if not quiet: print(f"  {dm('·')} Leyendo {wifi_config_xml} (requiere ROOT)...")
            try:
                tree = ET.parse(wifi_config_xml)
                root = tree.getroot()
                for network in root.findall(".//Network"):
                    ssid_elem = network.find(".//string[@name='SSID']")
                    psk_elem = network.find(".//string[@name='PreSharedKey']")
                    
                    ssid = ssid_elem.text.strip('"') if ssid_elem is not None and ssid_elem.text else "N/A"
                    psk = psk_elem.text.strip('"') if psk_elem is not None and psk_elem.text else "None/Encrypted"
                    
                    results.append({
                        "SSID": ssid,
                        "Auth": "Unknown",
                        "Password": psk,
                        "MAC": "N/A",
                        "Last_Connection": "N/A",
                        "Notes": "WifiConfigStore.xml (ROOT)"
                    })
            except Exception as e:
                if not quiet: print(f"    {y('⚠')} Error al parsear {wifi_config_xml}: {e}")
        elif wpa_supp_sdcard.is_file():
            if not quiet: print(f"  {dm('·')} Leyendo {wpa_supp_sdcard}...")
            try:
                content = wpa_supp_sdcard.read_text()
                networks = re.findall(r'network={\s*[^}]+ssid="([^"]+)"\s*[^}]+psk="([^"]+)"', content)
                for ssid, psk in networks:
                    results.append({
                        "SSID": ssid,
                        "Auth": "WPA/WPA2 PSK",
                        "Password": psk,
                        "MAC": "N/A",
                        "Last_Connection": "N/A",
                        "Notes": f"wpa_supplicant.conf (SD Card)"
                    })
            except Exception as e:
                if not quiet: print(f"    {y('⚠')} Error al leer {wpa_supp_sdcard}: {e}")
        else:
            if not quiet: print(f"  {y('⚠')} No se encontraron archivos de configuración WiFi accesibles. Intenta ejecutar como ROOT.")

    if results and session_dir:
        save_file(session_dir/'wifi_passwords.txt', "\n".join([f"SSID: {r['SSID']}, Auth: {r['Auth']}, Password: {r['Password']}, Notes: {r['Notes']}" for r in results]))
        save_file(session_dir/'wifi_passwords.json', json.dumps(results, indent=4))
        
    return results

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
