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
    {d}                                 github.com/nostraxiten/noxforens
    """
    print(banner)
    print(f"{r}[{w}I{r}]{w} Info                                                                 {w}Next {r}[{w}N{r}]")
    print(f"{r}[{w}S{r}]{w} Site")

def print_menu_columns(columns):
    r = Fore.RED + Style.BRIGHT
    w = Fore.WHITE + Style.BRIGHT

    headers = ("NOX / FORENSE", "OSINT / RED", "ANALISIS SISTEMA")
    gap = 8
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

def main():
    while True:
        clear_screen()
        print_banner()
        
        r = Fore.RED + Style.BRIGHT
        w = Fore.WHITE + Style.BRIGHT
        # 2. Error de variable 'd' no definida solucionado:
        d = Fore.LIGHTBLACK_EX
        
        col1 = [
            ("01", "NoxRecon (Full Scan)", "modules/nox/noxrecon.py"),
            ("02", "Browser Forensics", "modules/nox/browserforens.py"),
            ("03", "WiFi Keys Dump", "modules/nox/wifikeys.py"),
            ("04", "Credential Scanner", "modules/nox/credscan.py"),
            ("05", "Process Watcher", "modules/nox/procwatch.py"),
            ("06", "Network Sniffer", "modules/nox/netsniff.py"),
            ("07", "Port Scanner", "modules/nox/portscan.py"),
            ("08", "File Caver", "modules/nox/filecaver.py"),
            ("09", "Steg Detect", "modules/nox/stegdetect.py")
        ]
        
        col2 = [
            ("10", "Nmap Integration", "modules/classic/nmap.py"),
            ("11", "Tshark Dump", "modules/classic/tshark.py"),
            ("12", "TheHarvester", "modules/classic/theharvester.py"),
            ("13", "Sherlock", "modules/classic/sherlock.py"),
            ("14", "Recon-ng", "modules/classic/reconng.py"),
            ("15", "Spiderfoot", "modules/classic/spiderfoot.py"),
            ("16", "Steghide", "modules/classic/steghide.py"),
            ("17", "Binwalk", "modules/classic/binwalk.py"),
            ("18", "Exiftool", "modules/classic/exiftool.py")
        ]
        
        col3 = [
            ("19", "Timeline Gen", "modules/nox/timeline.py"),
            ("20", "Generate Report", "modules/nox/report.py"),
            ("21", "Binary Analyzer", "modules/nox/binary.py"),
            ("22", "Volatility", "modules/classic/volatility.py"),
            ("23", "Foremost", "modules/classic/foremost.py"),
            ("24", "Bulk Extractor", "modules/classic/bulk_extractor.py"),
            ("25", "Lynis Audit", "modules/classic/lynis.py"),
            ("26", "Chkrootkit", "modules/classic/chkrootkit.py")
        ]
        
        # Combinar todas las opciones para la búsqueda fácil
        all_options = {item[0]: item for item in col1 + col2 + col3}
        
        print_menu_columns((col1, col2, col3))
        footer = "[00] Exit"
        footer_indent = " " * max(4, ((shutil.get_terminal_size((100, 24)).columns - len(footer)) // 2) - 18)
        print(f"\n{footer_indent}{r}[{w}00{r}]{w} Exit")
        print()
        max_rows = 0
        for i in range(max_rows):
            # Obtener datos
            c1_num, c1_text, _ = col1[i] if i < len(col1) else ("", "", "")
            c2_num, c2_text, _ = col2[i] if i < len(col2) else ("", "", "")
            c3_num, c3_text, _ = col3[i] if i < len(col3) else ("", "", "")
            
            # Formatear la cadena de visualización (rojo los corchetes, blanco el texto)
            str_c1 = f"{r}[{w}{c1_num}{r}]{w} {c1_text}" if c1_num else ""
            str_c2 = f"{r}[{w}{c2_num}{r}]{w} {c2_text}" if c2_num else ""
            str_c3 = f"{r}[{w}{c3_num}{r}]{w} {c3_text}" if c3_num else ""
            
            # Calcular espacios. Usamos el texto plano para calcular longitudes.
            plain_c1 = f"[{c1_num}] {c1_text}" if c1_num else ""
            plain_c2 = f"[{c2_num}] {c2_text}" if c2_num else ""
            
            pad1 = " " * (34 - len(plain_c1)) if plain_c1 else " " * 34
            pad2 = " " * (32 - len(plain_c2)) if plain_c2 else " " * 32
            
            print(f"      {str_c1}{pad1}{str_c2}{pad2}{str_c3}")

        
        
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
        elif choice in ['I', 'i']:
            print(f"\n{w}[i] Nostraxiten Framework - Advanced Forensic & OSINT Suite")
            print(f"{w}[i] Version 1.6 - OSINT Pro Edition")
            input(f"\n{d}Press Enter to return...")
        elif choice in ['S', 's']:
            print(f"\n{w}[i] Github: https://github.com/nostraxiten/noxforens")
            input(f"\n{d}Press Enter to return...")
        elif choice in all_options:
            module_num, module_name, module_path = all_options[choice]
            print(f"\n{w}[*] Iniciando {r}{module_name}{w}...")
            time.sleep(1)
            
            # Comprobar si el módulo existe
            if os.path.exists(module_path):
                try:
                    # Ejecutar el módulo con la misma versión de python que ejecuta este script
                    subprocess.run([sys.executable, module_path])
                except Exception as e:
                    print(f"\n{r}[X] Error al ejecutar el módulo: {e}")
            else:
                print(f"\n{r}[X] Módulo '{module_path}' no encontrado.")
            
            input(f"\n{d}Presiona Enter para volver al menú...")
        elif choice != '':
            print(f"\n{r}[X] Opción inválida.")
            time.sleep(1)

if __name__ == '__main__':
    main()
