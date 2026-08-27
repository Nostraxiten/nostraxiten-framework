from datetime import datetime
from pathlib import Path
from core.colors import cy, g, dm
from core.utils import save_file, pause, inp, banner, hdr
from core.env import BASE_DIR
from config.settings import settings

def run():
    banner()
    hdr(23, "NOX_REPORT", "Generador de reporte HTML consolidado")
    sessions = sorted(BASE_DIR.glob('*_NOXRECON*'), reverse=True)
    if not sessions: 
        sessions = sorted(BASE_DIR.glob('*'), reverse=True)

    print(f"  {cy('Sesiones disponibles:')}")
    for i, s in enumerate(sessions[:10]):
        print(f"    {i}. {s.name}")
    
    idx = inp("Selecciona sesión [0]: ") or "0"
    target_session = sessions[int(idx)]
    analyst = inp(f"Nombre del Analista [{settings.analyst_name}]: ") or settings.analyst_name

    report_path = generate_report(target_session, analyst)
    print(f"\n  {g('✓')} Reporte HTML generado exitosamente:")
    print(f"  {g('→')} {report_path}")
    pause()

def generate_report(target_session, analyst=None):
    if analyst is None:
        analyst = settings.analyst_name

    html_content = f"""
    <html><head><style>
        body {{ background: #1a1a1a; color: #e0e0e0; font-family: monospace; padding: 40px; }}
        h1 {{ color: #00ffcc; border-bottom: 2px solid #333; }}
        .box {{ background: #252525; padding: 20px; border-radius: 5px; margin-bottom: 20px; border-left: 5px solid #00ffcc; }}
        pre {{ background: #000; padding: 15px; overflow-x: auto; color: #00ff00; }}
        .meta {{ color: #888; font-size: 0.9em; }}
    </style></head><body>
    <h1>FORENX REPORT: {target_session.name}</h1>
    <div class="box">
        <p><b>Analista:</b> {analyst}</p>
        <p><b>Fecha:</b> {datetime.now()}</p>
        <p><b>Evidencia:</b> {target_session}</p>
    </div>
    """

    for p in target_session.rglob('*'):
        if p.is_file() and p.suffix in ('.txt', '.json', '.log', '.csv', '.md'):
            try:
                content = p.read_text(errors='ignore')
                # Basic syntax highlight
                content = content.replace('open', '<b style="color:red">open</b>')
                html_content += f"<h3>FILE: {p.relative_to(target_session)}</h3><pre>{content}</pre>"
            except:
                pass

    html_content += "</body></html>"
    
    report_path = target_session / f"FINAL_REPORT_{target_session.name}.html"
    save_file(report_path, html_content)
    return report_path

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
