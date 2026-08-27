"""
Ver Grafo de Entidades — lista investigaciones previas guardadas por Investigate
y muestra un resumen + la ruta al grafo interactivo HTML.
"""
from core.colors import cy, g, y, dm, w, C
from core.utils import pause, inp, banner, hdr
from core.env import BASE_DIR
from modules.osint.graph import EntityGraph


def run():
    banner()
    hdr(32, "Ver Grafo de Entidades", "Investigaciones previas guardadas (Investigación Completa)")

    cases = sorted(BASE_DIR.glob('*_INVESTIGACION_*'), reverse=True)
    if not cases:
        print(f"\n  {y('⚠')} No hay investigaciones guardadas todavía. Usa la opción [31] primero.")
        pause()
        return

    for i, c in enumerate(cases[:15]):
        graph_json = c / 'graph.json'
        summary = ''
        if graph_json.exists():
            try:
                gr = EntityGraph.load_json(graph_json)
                stats = gr.stats()
                summary = f" — {stats['nodes']} entidades, {stats['edges']} relaciones"
            except Exception:
                pass
        print(f"    {cy(str(i))}. {c.name}{dm(summary)}")

    idx = inp("\nSelecciona caso [0]: ") or "0"
    try:
        case = cases[int(idx)]
    except (ValueError, IndexError):
        print(f"\n  {y('⚠')} Selección inválida.")
        pause()
        return

    graph_html = case / 'graph.html'
    report_html = next(case.glob('REPORTE_*.html'), None)

    print(f"\n  {C.BD}{C.CY}── {case.name} ──{C.RS}")
    if (case / 'graph.json').exists():
        gr = EntityGraph.load_json(case / 'graph.json')
        stats = gr.stats()
        print(f"  {w('Entidades')}: {stats['nodes']}   {w('Relaciones')}: {stats['edges']}")
        for etype, count in stats['by_type'].items():
            print(f"    {dm('•')} {etype}: {count}")
    if graph_html.exists():
        print(f"\n  {g('✓')} Grafo interactivo: {cy(str(graph_html))}")
    if report_html:
        print(f"  {g('✓')} Reporte consolidado: {cy(str(report_html))}")
    print(f"\n  {dm('Abre estos archivos .html en un navegador para visualizarlos.')}")
    pause()


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
