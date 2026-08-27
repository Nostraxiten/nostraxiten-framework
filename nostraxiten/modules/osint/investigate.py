"""
Investigación Completa — orquesta domain_recon, username_recon, email_recon y
metadata_recon sobre un mismo caso, correlacionando todo en un EntityGraph y
generando un reporte HTML consolidado. Esto es lo que diferencia a Nostraxiten
de un simple menú de herramientas sueltas.
"""
import json
from datetime import datetime

from core.colors import cy, g, y, r, dm, w, C
from core.utils import new_session as new_case, save_file, pause, inp, banner, hdr
from modules.osint import domain_recon, username_recon, email_recon, metadata_recon
from modules.osint.graph import EntityGraph


def run():
    banner()
    hdr(31, "Investigación Completa", "Correlación multi-módulo: dominio + username + email + grafo de entidades")

    print(f"  {cy('Introduce los datos que tengas (deja vacío lo que no aplique):')}\n")
    domain = inp("Dominio (ej: example.com): ")
    username = inp("Username: ")
    email = inp("Email: ")
    image_path = inp("Ruta a imagen para analizar EXIF (opcional): ")

    if not any([domain, username, email, image_path]):
        print(f"\n  {r('✗')} No se proporcionó ningún objetivo.")
        pause()
        return

    case_label = domain or username or email or 'investigacion'
    graph = EntityGraph(case_name=case_label)
    case = new_case(f'INVESTIGACION_{case_label.replace("@", "_at_").replace(".", "_")}')

    results = {'case': case_label, 'timestamp': str(datetime.now())}

    if domain:
        print(f"\n  {C.BD}{C.CY}[1/4] Domain Recon: {domain}{C.RS}")
        results['domain_recon'] = domain_recon.run(domain=domain, silent=True, graph=graph)
        print(f"  {g('✓')} completado")

    if username:
        print(f"\n  {C.BD}{C.CY}[2/4] Username Recon: {username}{C.RS}")
        results['username_recon'] = username_recon.run(username=username, silent=True, graph=graph)
        found_n = len(results['username_recon']['found']) if results['username_recon'] else 0
        print(f"  {g('✓')} completado — {found_n} perfiles encontrados")

    if email:
        print(f"\n  {C.BD}{C.CY}[3/4] Email Recon: {email}{C.RS}")
        results['email_recon'] = email_recon.run(email=email, silent=True, graph=graph)
        print(f"  {g('✓')} completado")

    if image_path:
        print(f"\n  {C.BD}{C.CY}[4/4] Metadata Recon: {image_path}{C.RS}")
        results['metadata_recon'] = metadata_recon.run(path=image_path, silent=True, graph=graph)
        print(f"  {g('✓')} completado")

    # Correlación cruzada básica: si el email pertenece al mismo dominio investigado, enlazar.
    if domain and email and email.endswith('@' + domain):
        graph.add_relation(email, domain, 'owned_by_investigated_domain')
    if domain and username:
        graph.add_relation(username, domain, 'associated_investigation')

    save_file(case / 'raw_results.json', json.dumps(results, indent=2, default=str))
    graph.save_json(case / 'graph.json')
    graph.export_dot(case / 'graph.dot')
    html_graph_path = case / 'graph.html'
    graph.export_html(html_graph_path)

    report_path = _generate_consolidated_report(case, results, graph)

    stats = graph.stats()
    print(f"\n  {C.BD}{C.CY}── INVESTIGACIÓN COMPLETA ──{C.RS}")
    print(f"  {w('Entidades correlacionadas')}: {g(str(stats['nodes']))}    {w('Relaciones')}: {g(str(stats['edges']))}")
    for etype, count in stats['by_type'].items():
        print(f"    {dm('•')} {etype}: {count}")
    print(f"\n  {g('✓')} Caso guardado en: {case}")
    print(f"  {g('✓')} Grafo interactivo: {cy(str(html_graph_path))}")
    print(f"  {g('✓')} Reporte consolidado: {cy(str(report_path))}")
    pause()


def _generate_consolidated_report(case, results, graph):
    stats = graph.stats()
    sections = []

    if results.get('domain_recon'):
        d = results['domain_recon']
        sections.append(f"""
        <div class="box"><h2>🌐 Domain Recon: {d['domain']}</h2>
        <p><b>Subdominios:</b> {len(d.get('subdomains_found', []))} encontrados, {len(d.get('subdomains_alive', {}))} activos</p>
        <p><b>Tecnologías:</b> {', '.join(d.get('http', {}).get('tech', [])) or 'N/D'}</p>
        <p><b>Puertos abiertos:</b> {', '.join(f"{{p}}/{{s}}" for p, s in d.get('open_ports', {}).items()) or 'ninguno'}</p>
        </div>""")

    if results.get('username_recon'):
        u = results['username_recon']
        found_list = ''.join(f"<li>{name}: <a href='{info['url']}' style='color:#58a6ff'>{info['url']}</a></li>"
                              for name, info in sorted(u.get('found', {}).items()))
        sections.append(f"""
        <div class="box"><h2>👤 Username Recon: {u['username']}</h2>
        <p><b>{len(u.get('found', {}))}</b> perfiles encontrados de {len(u.get('found', {})) + len(u.get('not_found', {}))} plataformas comprobadas.</p>
        <ul>{found_list}</ul></div>""")

    if results.get('email_recon'):
        e = results['email_recon']
        hibp = e.get('hibp', {})
        breach_html = ''
        if hibp.get('breached'):
            names = [b.get('Name', '?') if isinstance(b, dict) else str(b) for b in hibp.get('breaches', [])]
            breach_html = f"<p style='color:#f85149'><b>⚠ COMPROMETIDO en {len(names)} brechas:</b> {', '.join(names)}</p>"
        elif 'breached' in hibp:
            breach_html = "<p style='color:#3fb950'>Sin brechas conocidas.</p>"
        sections.append(f"""
        <div class="box"><h2>📧 Email Recon: {e['email']}</h2>
        <p><b>MX:</b> {', '.join(e.get('mx', [])) or 'N/D'}</p>
        <p><b>Gravatar:</b> {'existe' if e.get('gravatar', {}).get('exists') else 'sin cuenta'}</p>
        {breach_html}
        </div>""")

    if results.get('metadata_recon'):
        m = results['metadata_recon']
        gps = m.get('image', {}).get('gps')
        gps_html = f"<p style='color:#f85149'><b>📍 GPS:</b> <a href='{gps['maps_url']}' style='color:#58a6ff'>{gps['lat']}, {gps['lon']}</a></p>" if gps else "<p>Sin GPS.</p>"
        sections.append(f"""
        <div class="box"><h2>🖼 Metadata: {m['file']['name']}</h2>{gps_html}</div>""")

    by_type_html = ''.join(f"<span class='chip'>{etype}: {count}</span>" for etype, count in stats['by_type'].items())

    html_content = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><title>Nostraxiten — Reporte: {results['case']}</title>
<style>
  body {{ background:#0d1117; color:#e6edf3; font-family: -apple-system, Segoe UI, sans-serif; padding:32px; max-width:1000px; margin:auto; }}
  h1 {{ color:#58a6ff; border-bottom:2px solid #30363d; padding-bottom:12px; }}
  .box {{ background:#161b22; border:1px solid #30363d; border-radius:8px; padding:20px; margin-bottom:18px; }}
  .box h2 {{ margin-top:0; color:#79c0ff; }}
  .meta {{ color:#8b949e; font-size:0.9em; }}
  .chip {{ display:inline-block; background:#21262d; border:1px solid #30363d; border-radius:14px;
           padding:4px 12px; margin:4px 6px 4px 0; font-size:12px; }}
  a {{ color:#58a6ff; }}
</style></head><body>
  <h1>🕵 Nostraxiten — Investigación: {results['case']}</h1>
  <p class="meta">Fecha: {results['timestamp']} · Caso: {case.name}</p>
  <div class="box"><h2>📊 Resumen del Grafo de Entidades</h2>
    <p>{stats['nodes']} entidades · {stats['edges']} relaciones correlacionadas</p>
    {by_type_html}
    <p class="meta">Ver visualización interactiva en <a href="graph.html">graph.html</a></p>
  </div>
  {''.join(sections)}
</body></html>"""

    report_path = case / f"REPORTE_{case.name}.html"
    save_file(report_path, html_content)
    return report_path


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
