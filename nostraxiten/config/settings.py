import json
import os
from pathlib import Path

CONFIG_FILE = Path.home() / '.noxforens.json'

class Config:
    def __init__(self):
        self.vt_api_key = ''
        self.onyphe_api_key = ''
        self.hunter_api_key = ''
        self.hibp_api_key = ''
        self.shodan_api_key = ''
        self.wordlist_path = '/usr/share/wordlists/rockyou.txt'
        self.last_session = ''
        self.analyst_name = 'Admin'
        self.base_dir = str(Path.home() / 'Datos')
        self.auto_report = False
        self.load()

    def load(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    for k, v in data.items():
                        if hasattr(self, k):
                            setattr(self, k, v)
            except Exception:
                pass

    def save(self):
        data = {
            'vt_api_key': self.vt_api_key,
            'onyphe_api_key': self.onyphe_api_key,
            'hunter_api_key': self.hunter_api_key,
            'hibp_api_key': self.hibp_api_key,
            'shodan_api_key': self.shodan_api_key,
            'wordlist_path': self.wordlist_path,
            'last_session': self.last_session,
            'analyst_name': self.analyst_name,
            'base_dir': self.base_dir,
            'auto_report': self.auto_report
        }
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception:
            pass

    def edit(self):
        # We will import these here to avoid circular imports since config might be used widely
        from core.colors import cy, g, r, dm, C
        from core.utils import inp
        import os
        
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"\n  {C.BD}{C.CY}=== CONFIGURACIÓN NOXFORENS ==={C.RS}\n")
            print(f"  [1] VirusTotal API Key: {dm(self.vt_api_key[:5] + '...' if self.vt_api_key else 'Vacío')}")
            print(f"  [2] Onyphe API Key:     {dm(self.onyphe_api_key[:5] + '...' if self.onyphe_api_key else 'Vacío')}")
            print(f"  [3] Hunter.io API Key:  {dm(self.hunter_api_key[:5] + '...' if self.hunter_api_key else 'Vacío')}")
            print(f"  [4] HIBP API Key:       {dm(self.hibp_api_key[:5] + '...' if self.hibp_api_key else 'Vacío')}")
            print(f"  [5] Shodan API Key:     {dm(self.shodan_api_key[:5] + '...' if self.shodan_api_key else 'Vacío')}")
            print(f"  [6] Wordlist Path:      {dm(self.wordlist_path)}")
            print(f"  [7] Analyst Name:       {dm(self.analyst_name)}")
            print(f"  [8] Base Dir:           {dm(self.base_dir)}")
            print(f"  [9] Auto Report:        {g('ON') if self.auto_report else r('OFF')}")
            print(f"\n  [s] Guardar y Salir")

            choice = inp("Selecciona opción a editar: ").strip().lower()
            if choice == 's':
                self.save()
                break
            elif choice == '1':
                self.vt_api_key = inp("Nuevo VT API Key: ")
            elif choice == '2':
                self.onyphe_api_key = inp("Nuevo Onyphe API Key: ")
            elif choice == '3':
                self.hunter_api_key = inp("Nuevo Hunter.io API Key: ")
            elif choice == '4':
                self.hibp_api_key = inp("Nuevo HIBP API Key (haveibeenpwned.com/API/Key): ")
            elif choice == '5':
                self.shodan_api_key = inp("Nuevo Shodan API Key: ")
            elif choice == '6':
                self.wordlist_path = inp("Nuevo Wordlist Path: ")
            elif choice == '7':
                self.analyst_name = inp("Nuevo Analyst Name: ")
            elif choice == '8':
                self.base_dir = inp("Nuevo Base Dir: ")
            elif choice == '9':
                self.auto_report = not self.auto_report

settings = Config()
