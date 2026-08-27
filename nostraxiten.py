import os
import sys
import time
import subprocess
import shutil

# 1. Error de Unicode en Windows solucionado:
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class DummyColor:
        def __getattr__(self, name): return ""
    Fore = DummyColor()
    Style = DummyColor()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    r = Fore.RED + Style.BRIGHT
    w = Fore.WHITE + Style.BRIGHT
    d = Fore.LIGHTBLACK_EX
    
    # Red Tiger style banner
    banner = f"""{r}
      ::::    :::  ::::::::   :::::::: ::::::::::: :::::::::      :::     :::    ::: ::::::::::: ::::::::::: :::::::::: ::::    ::: 
     :+:+:   :+: :+:    :+: :+:    :+:    :+:     :+:    :+:   :+: :+:   :+:    :+:     :+:         :+:     :+:        :+:+:   :+:  
    :+:+:+  +:+ +:+    +:+ +:+           +:+     +:+    +:+  +:+   +:+   +:+  +:+      +:+         +:+     +:+        :+:+:+  +:+   
   +#+ +:+ +#+ +#+    +:+ +#++:++#++    +#+     +#++:++#:  +#++:++#++:   +#++:+       +#+         +#+     +#++:++#   +#+ +:+ +#+    
  +#+  +#+#+# +#+    +#+        +#+    +#+     +#+    +#+ +#+     +#+  +#+  +#+      +#+         +#+     +#+        +#+  +#+#+#     
 #+#   #+#+# #+#    #+# #+#    #+#    #+#     #+#    #+# #+#     #+# #+#    #+#     #+#         #+#     #+#        #+#   #+#+#      
###    ####  ########   ########     ###     ###    ### ###     ### ###    ### ###########     ###     ########## ###    ####       
    {d}
    """
    print(banner)
    print(f"{r}[{w}I{r}]{w} Info                                                                 {w}Next {r}[{w}N{r}]")
    print(f"{r}[{w}S{r}]{w} Site")

def print_menu_columns(columns, headers):
    r = Fore.RED + Style.BRIGHT
    w = Fore.WHITE + Style.BRIGHT

    gap = 6
    min_col_width = 26
    left_shift = 18
    col_widths = [
        max(min_col_width, len(headers[i]), *(len(f"[{num}] {name}") for num, name, _ in col))
        for i, col in enumerate(columns)
    ]
    block_width = sum(col_widths) + gap * (len(columns) - 1)
    term_width = shutil.get_terminal_size((100, 24)).columns
    indent = " " * max(4, ((term_width - block_width) // 2) - left_shift)

    def color_header(text, width):
        return f"{r}{text.center(width)}{w}"

    def color_rule(width):
        return f"{r}{('-' * min(width, 16)).center(width)}{w}"

    def color_option(item, width):
        if not item:
            return " " * width
        num, text, _ = item
        plain = f"[{num}] {text}"
        padding = " " * max(0, width - len(plain))
        return f"{r}[{w}{num}{r}]{w} {text}{padding}"

    print()
    print(indent + (" " * gap).join(color_header(headers[i], col_widths[i]) for i in range(len(columns))))
    print(indent + (" " * gap).join(color_rule(col_widths[i]) for i in range(len(columns))))

    max_rows = max(len(col) for col in columns)
    for row in range(max_rows):
        cells = [
            color_option(columns[i][row] if row < len(columns[i]) else None, col_widths[i])
            for i in range(len(columns))
        ]
        print(indent + (" " * gap).join(cells))

def show_install_info(num, name):
    r = Fore.RED + Style.BRIGHT
    w = Fore.WHITE + Style.BRIGHT
    d = Fore.LIGHTBLACK_EX
    cy = Fore.CYAN + Style.BRIGHT

    # Base de datos de instalación por herramienta externa.
    tools_data = {
        "10": {"lin": "sudo apt install nmap", "win": "https://nmap.org/download.html", "tmx": "pkg install nmap"},
        "11": {"lin": "sudo apt install tshark", "win": "https://www.wireshark.org/", "tmx": "pkg install tshark"},
        "12": {"lin": "sudo apt install theharvester", "win": "https://github.com/laramies/theHarvester", "tmx": "pkg install theharvester"},
        "13": {"lin": "pip install sherlock-project", "win": "pip install sherlock-project", "tmx": "pip install sherlock-project"},
        "14": {"lin": "pip install recon-ng", "win": "pip install recon-ng", "tmx": "pip install recon-ng"},
        "15": {"lin": "pip install spiderfoot", "win": "pip install spiderfoot", "tmx": "pip install spiderfoot"},
        "16": {"lin": "sudo apt install steghide", "win": "https://github.com/StefanoDeVuono/steghide", "tmx": "pkg install steghide"},
        "17": {"lin": "sudo apt install binwalk", "win": "https://github.com/ReFirmLabs/binwalk", "tmx": "pkg install binwalk"},
        "18": {"lin": "sudo apt install libimage-exiftool-perl", "win": "https://exiftool.org/", "tmx": "pkg install exiftool"},
        "22": {"lin": "pip install volatility3", "win": "pip install volatility3", "tmx": "https://github.com/volatilityfoundation/volatility3"},
        "23": {"lin": "sudo apt install foremost", "win": "https://github.com/jonstewart/foremost", "tmx": "pkg install foremost"},
        "24": {"lin": "sudo apt install bulk-extractor", "win": "https://github.com/simsong/bulk_extractor", "tmx": "https://github.com/simsong/bulk_extractor"},
        "25": {"lin": "sudo apt install lynis", "win": "https://github.com/CISOfy/lynis", "tmx": "https://github.com/CISOfy/lynis"},
        "26": {"lin": "sudo apt install chkrootkit", "win": "https://github.com/chkrootkit/chkrootkit", "tmx": "https://github.com/chkrootkit/chkrootkit"},
    }

    info = tools_data.get(num, {"lin": "Instalación manual", "win": "GitHub", "tmx": "GitHub"})
    
    clear_screen()
    print_banner()
    print(f"\n      {r}--- GUÍA DE INSTALACIÓN: {w}{name} {r}---")
    print(f"      {d}Asegúrate de tener instalada la herramienta antes de continuar.{w}\n")

    # Linux
    if info["lin"].startswith("http"):
        print(f"      {r}[Linux]{w}   Soporte via: {cy}{info['lin']}")
    else:
        print(f"      {r}[Linux]{w}   Comando: {r}{info['lin']}")

    # Windows
    if info["win"].startswith("http"):
        print(f"      {r}[Windows]{w} Soporte via: {cy}{info['win']}")
    else:
        print(f"      {r}[Windows]{w} Comando: {r}{info['win']}")

    # Termux
    if info["tmx"].startswith("http"):
        print(f"      {r}[Termux]{w}  Soporte via: {cy}{info['tmx']}")
    else:
        print(f"      {r}[Termux]{w}  Comando: {r}{info['tmx']}")

    print(f"\n      {d}Presiona ENTER para intentar ejecutar la herramienta...")
    input()


def install_dependencies():
    r = Fore.RED + Style.BRIGHT
    w = Fore.WHITE + Style.BRIGHT
    d = Fore.LIGHTBLACK_EX
    
    clear_screen()
    print_banner()
    print(f"\n      {r}[{w}*{r}]{w} INICIANDO INSTALADOR CROSS-PLATFORM...")
    time.sleep(1)

    is_termux = 'com.termux' in os.environ.get('PREFIX', '')
    platform_name = "Android (Termux)" if is_termux else sys.platform
    
    print(f"      {r}[{w}i{r}]{w} Sistema detectado: {r}{platform_name}{w}")
    
    # --- 1. Dependencias de Sistema ---
    if is_termux:
        print(f"      {r}[{w}+{r}]{w} Instalando paquetes de sistema (pkg)...")
        packages = "python git nmap curl wget binwalk exiftool steghide foremost"
        subprocess.run(f"pkg install -y {packages}", shell=True)
    elif sys.platform.startswith('linux'):
        print(f"      {r}[{w}+{r}]{w} Instalando paquetes de sistema (apt) - Puede requerir sudo...")
        packages = "python3 python3-pip git nmap curl wget tshark binwalk exiftool steghide foremost bulk-extractor chkrootkit lynis"
        subprocess.run(f"sudo apt update && sudo apt install -y {packages}", shell=True)
    elif sys.platform == 'win32':
        print(f"      {r}[{w}i{r}]{w} En Windows, instala Nmap y herramientas externas manualmente.")
        print(f"      {r}[{w}i{r}]{w} Continuando con dependencias de Python...")

    # --- 2. Dependencias de Python ---
    print(f"\n      {r}[{w}+{r}]{w} Instalando librerías de Python...")
    py_deps = ["requests", "colorama", "cryptography", "pycryptodome", "scapy", "dnspython", "Pillow"]
    if sys.platform == 'win32':
        py_deps.append("pywin32")
    
    pip_cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "pip"]
    subprocess.run(pip_cmd)
    
    pip_cmd = [sys.executable, "-m", "pip", "install"] + py_deps
    if not sys.platform == 'win32':
        pip_cmd.append("--break-system-packages") # Para distros modernas de Linux
        
    subprocess.run(pip_cmd)
    
    print(f"\n      {r}[{w}✓{r}]{w} INSTALACIÓN FINALIZADA.")
    input(f"\n      {d}Presiona Enter para volver...")

def main():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(BASE_DIR, "nostraxiten")
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    while True:
        clear_screen()
        print_banner()
        
        r = Fore.RED + Style.BRIGHT
        w = Fore.WHITE + Style.BRIGHT
        d = Fore.LIGHTBLACK_EX
        
        col1 = [
            ("01", "NoxRecon (Full Scan)", "nostraxiten/modules/nox/noxrecon.py"),
            ("02", "Browser Forensics", "nostraxiten/modules/nox/browserforens.py"),
            ("03", "WiFi Keys Dump", "nostraxiten/modules/nox/wifikeys.py"),
            ("04", "Credential Scanner", "nostraxiten/modules/nox/credscan.py"),
            ("05", "Process Watcher", "nostraxiten/modules/nox/procwatch.py"),
            ("06", "Network Sniffer", "nostraxiten/modules/nox/netsniff.py"),
            ("07", "Port Scanner", "nostraxiten/modules/nox/portscan.py"),
            ("08", "File Caver", "nostraxiten/modules/nox/filecaver.py"),
            ("09", "Steg Detect", "nostraxiten/modules/nox/stegdetect.py"),
        ]
        
        col2 = [
            ("10", "Nmap Integration", "nostraxiten/modules/classic/nmap.py"),
            ("11", "Tshark Dump", "nostraxiten/modules/classic/tshark.py"),
            ("12", "TheHarvester", "nostraxiten/modules/classic/theharvester.py"),
            ("13", "Sherlock", "nostraxiten/modules/classic/sherlock.py"),
            ("14", "Recon-ng", "nostraxiten/modules/classic/reconng.py"),
            ("15", "Spiderfoot", "nostraxiten/modules/classic/spiderfoot.py"),
            ("16", "Steghide", "nostraxiten/modules/classic/steghide.py"),
            ("17", "Binwalk", "nostraxiten/modules/classic/binwalk.py"),
            ("18", "Exiftool", "nostraxiten/modules/classic/exiftool.py"),
        ]
        
        col3 = [
            ("19", "Timeline Gen", "nostraxiten/modules/nox/timeline.py"),
            ("20", "Generate Report", "nostraxiten/modules/nox/report.py"),
            ("21", "Binary Analyzer", "nostraxiten/modules/nox/binary.py"),
            ("22", "Volatility", "nostraxiten/modules/classic/volatility.py"),
            ("23", "Foremost", "nostraxiten/modules/classic/foremost.py"),
            ("24", "Bulk Extractor", "nostraxiten/modules/classic/bulk_extractor.py"),
            ("25", "Lynis Audit", "nostraxiten/modules/classic/lynis.py"),
            ("26", "Chkrootkit", "nostraxiten/modules/classic/chkrootkit.py")
        ]
        
        col4 = [
            ("27", "Domain Recon (WHOIS/DNS/Subs)", "nostraxiten/modules/osint/domain_recon.py"),
            ("28", "Username Recon (Multi-Plataf.)", "nostraxiten/modules/osint/username_recon.py"),
            ("29", "Email Recon (Breach/Hunter)", "nostraxiten/modules/osint/email_recon.py"),
            ("30", "Metadata / EXIF Analyzer", "nostraxiten/modules/osint/metadata_recon.py"),
            ("31", "Investigacion Completa", "nostraxiten/modules/osint/investigate.py"),
            ("32", "Ver Grafo de Entidades", "nostraxiten/modules/osint/view_cases.py"),
        ]

        all_options = {item[0]: item for item in col1 + col2 + col3 + col4}

        headers = ("NOX / FORENSE", "OSINT / RED", "ANALISIS SISTEMA", "OSINT PRO (NATIVO)")
        print_menu_columns((col1, col2, col3, col4), headers)

        footer = f"[99] Install Dependencies (Win/Lin/Android)  [98] Config API Keys  [00] Exit"
        footer_indent = " " * max(4, ((shutil.get_terminal_size((100, 24)).columns - len(footer)) // 2) - 18)
        print(f"\n{footer_indent}{r}[{w}99{r}]{w} Install Dependencies      {r}[{w}98{r}]{w} Config API Keys      {r}[{w}00{r}]{w} Exit")
        print()
        
        try:
            choice = input(f"{r}nostraxiten{w}@{r}root{w}:~# ").strip()
            # Normalizar entrada: si es un solo dígito (1-9), añadir 0 al inicio
            if choice.isdigit() and len(choice) == 1:
                choice = choice.zfill(2)
        except KeyboardInterrupt:
            break
            
        if choice == '00':
            print(f"\n{w}[+] Exiting Nostraxiten Framework...")
            break
        elif choice == '99':
            install_dependencies()
        elif choice == '98':
            from config.settings import settings
            settings.edit()
        elif choice in ['I', 'i']:
            print(f"\n{w}[i] Nostraxiten Framework - Advanced Forensic & OSINT Suite")
            print(f"{w}[i] Version 1.6 - OSINT Pro Edition")
            input(f"\n{d}Press Enter to return...")
        elif choice in ['S', 's']:
            print(f"\n{w}[i] Github: https://github.com/nostraxiten/noxforens")
            input(f"\n{d}Press Enter to return...")
        elif choice in all_options:
            module_num, module_name, module_path = all_options[choice]
            
            # Mostrar guía solo para herramientas externas.
            if choice in ["10", "11", "12", "13", "14", "15", "16", "17", "18", "22", "23", "24", "25", "26"]:
                show_install_info(choice, module_name)
                
            print(f"\n{w}[*] Iniciando {r}{module_name}{w}...")
            time.sleep(1)
            
            # Resolver ruta absoluta
            module_full_path = os.path.join(BASE_DIR, module_path)
            
            if os.path.exists(module_full_path):
                try:
                    # Configurar entorno para que los módulos encuentren los paquetes 'core', 'config', etc.
                    env = os.environ.copy()
                    # La carpeta 'nostraxiten' contiene los paquetes core, modules, etc.
                    project_root = os.path.join(BASE_DIR, "nostraxiten")
                    env["PYTHONPATH"] = project_root + (os.pathsep + env.get("PYTHONPATH", "") if env.get("PYTHONPATH") else "")
                    
                    subprocess.run([sys.executable, module_full_path], env=env)
                except Exception as e:
                    print(f"\n{r}[X] Error al ejecutar el módulo: {e}")
            else:
                print(f"\n{r}[X] Módulo no encontrado en: {module_full_path}")
            
            input(f"\n{d}Presiona Enter para volver al menú...")
        elif choice != '':
            print(f"\n{r}[X] Opción inválida.")
            time.sleep(1)

if __name__ == '__main__':
    main()
