import html
from datetime import datetime
from pathlib import Path
from core.colors import cy, g, r, dm, y
from core.utils import save_file, pause, inp, banner, hdr
from core.env import BASE_DIR
from config.settings import settings

def run():
    banner()
    hdr(23, "NOX_REPORT", "Generador de reporte HTML consolidado")
    sessions = sorted(BASE_DIR.glob('*_NOXRECON*'), reverse=True)
    if not sessions: 
        sessions = sorted(BASE_DIR.glob('*'), reverse=True)

    if not sessions:
        print(f"  {r('✘')} No se encontraron sesiones forenses en {BASE_DIR}")
        pause()
        return

    print(f"  {cy('Sesiones disponibles:')}")
    for i, s in enumerate(sessions[:10]):
        print(f"    {i}. {s.name}")
    
    idx_str = inp("Selecciona sesión [0]: ") or "0"
    try:
        idx = int(idx_str)
        if 0 <= idx < len(sessions):
            target_session = sessions[idx]
        else:
            print(f"  {y('!')} Índice fuera de rango. Usando sesión 0.")
            target_session = sessions[0]
    except ValueError:
        print(f"  {y('!')} Entrada inválida. Usando sesión 0.")
        target_session = sessions[0]

    analyst = inp(f"Nombre del Analista [{settings.analyst_name}]: ") or settings.analyst_name

    report_path = generate_report(target_session, analyst)
    print(f"\n  {g('✓')} Reporte HTML generado exitosamente:")
    print(f"  {g('→')} {report_path}")
    pause()

def generate_report(target_session, analyst=None):
    if analyst is None:
        analyst = settings.analyst_name

    target_session = Path(target_session)
    analyst_escaped = html.escape(str(analyst))
    session_escaped = html.escape(str(target_session.name))
    
    files_to_render = []
    for p in sorted(target_session.rglob('*')):
        if p.is_file() and p.suffix.lower() in ('.txt', '.json', '.log', '.csv', '.md'):
            if p.name.startswith("FINAL_REPORT_"):
                continue
            files_to_render.append(p)

    nav_links = "".join(
        f'<a href="#file-{i}">{html.escape(p.name)}</a>'
        for i, p in enumerate(files_to_render)
    )

    rendered_files = []
    for i, p in enumerate(files_to_render):
        try:
            content = p.read_text(errors='ignore')
            safe_content = html.escape(content)
            rel_path = html.escape(str(p.relative_to(target_session)))
            rendered_files.append(
                f'<div class="file-card" id="file-{i}">'
                f'<div class="file-header">'
                f'<span class="file-title">{rel_path}</span>'
                f'<span class="file-size">{p.stat().st_size:,} bytes</span>'
                f'</div>'
                f'<pre><code>{safe_content}</code></pre>'
                f'</div>'
            )
        except Exception as e:
            rendered_files.append(f'<div class="file-card"><p>Error leyendo {html.escape(p.name)}: {html.escape(str(e))}</p></div>')

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte Forense - {session_escaped}</title>
    <style>
        :root {{
            --bg: #0d1117;
            --card-bg: #161b22;
            --border: #30363d;
            --accent: #58a6ff;
            --accent-cyan: #39c5bb;
            --text: #c9d1d9;
            --text-dim: #8b949e;
            --code-bg: #030407;
            --code-text: #7ee787;
        }}
        * {{ box-sizing: border-box; }}
        body {{
            background: var(--bg);
            color: var(--text);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 30px;
        }}
        header {{
            border-bottom: 2px solid var(--border);
            padding-bottom: 20px;
            margin-bottom: 25px;
        }}
        h1 {{
            color: var(--accent-cyan);
            margin: 0 0 10px 0;
            font-size: 1.8rem;
            letter-spacing: 0.5px;
        }}
        .meta-box {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-left: 4px solid var(--accent-cyan);
            padding: 16px 20px;
            border-radius: 6px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 12px;
            margin-bottom: 25px;
        }}
        .meta-item {{ font-size: 0.92rem; }}
        .meta-label {{ color: var(--text-dim); display: block; font-size: 0.8rem; text-transform: uppercase; }}
        .meta-val {{ font-weight: 600; color: #fff; }}
        .nav-bar {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            padding: 12px 16px;
            border-radius: 6px;
            margin-bottom: 25px;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            font-size: 0.85rem;
        }}
        .nav-bar a {{
            color: var(--accent);
            text-decoration: none;
            background: #21262d;
            padding: 4px 10px;
            border-radius: 4px;
            border: 1px solid var(--border);
        }}
        .nav-bar a:hover {{ background: #30363d; text-decoration: underline; }}
        .file-card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 6px;
            margin-bottom: 20px;
            overflow: hidden;
        }}
        .file-header {{
            background: #1c2128;
            padding: 10px 16px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-family: monospace;
            font-size: 0.95rem;
        }}
        .file-title {{ color: var(--accent-cyan); font-weight: bold; }}
        .file-size {{ color: var(--text-dim); font-size: 0.8rem; }}
        pre {{
            margin: 0;
            padding: 16px;
            background: var(--code-bg);
            color: var(--code-text);
            overflow-x: auto;
            font-family: Consolas, "Courier New", monospace;
            font-size: 0.88rem;
            line-height: 1.45;
        }}
        footer {{
            margin-top: 40px;
            text-align: center;
            color: var(--text-dim);
            font-size: 0.85rem;
            border-top: 1px solid var(--border);
            padding-top: 20px;
        }}
    </style>
</head>
<body>
    <header>
        <h1>⚡ NOXFORENS // REPORTE FORENSE CONSOLIDADO</h1>
        <div style="color: var(--text-dim);">NOSTRAXITEN FRAMEWORK — ANALYTICS ENGINE</div>
    </header>

    <div class="meta-box">
        <div class="meta-item"><span class="meta-label">Sesión</span><span class="meta-val">{session_escaped}</span></div>
        <div class="meta-item"><span class="meta-label">Analista</span><span class="meta-val">{analyst_escaped}</span></div>
        <div class="meta-item"><span class="meta-label">Fecha de Generación</span><span class="meta-val">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span></div>
        <div class="meta-item"><span class="meta-label">Archivos Analizados</span><span class="meta-val">{len(files_to_render)}</span></div>
    </div>

    <div class="nav-bar">
        <strong style="display:flex; align-items:center; margin-right:8px; color:var(--text-dim);">Índice:</strong>
        {nav_links}
    </div>

    {"".join(rendered_files)}

    <footer>
        Generado automáticamente por Nostraxiten Framework | {datetime.now().year}
    </footer>
</body>
</html>"""

    report_path = target_session / f"FINAL_REPORT_{target_session.name}.html"
    save_file(report_path, html_content)
    return report_path

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
