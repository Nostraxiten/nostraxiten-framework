"""
Username Recon — búsqueda nativa multiplataforma (sin depender de sherlock-project).
Lee la base de datos de plataformas en data/osint_sites.json y comprueba en paralelo
si el username existe en cada una.
"""
import json
import concurrent.futures
from pathlib import Path
from datetime import datetime

from core.colors import cy, g, y, r, dm, w, C
from core.utils import new_session as new_case, save_file, pause, inp, banner, hdr
from core.env import BASE_DIR
from core.http import new_session, safe_get, ensure_requests

SITES_FILE = Path(__file__).resolve().parents[2] / 'data' / 'osint_sites.json'


def load_sites():
    try:
        with open(SITES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        data.pop('_meta', None)
        return data
    except Exception:
        return {}


def _check_site(session, name, spec, username):
    url = spec['url'].format(username)
    resp = safe_get(session, url, timeout=8)
    if resp is None:
        return name, url, 'error', None

    notfound_code = spec.get('notfound_code', 404)

    # Un status >=400 distinto del código "no existe" suele ser un bloqueo
    # anti-bot (403/429/503), no una confirmación de que el usuario no existe.
    if resp.status_code >= 400 and resp.status_code != notfound_code:
        return name, url, 'error', resp.status_code

    if spec['type'] == 'status_code':
        exists = resp.status_code != notfound_code
    else:
        notfound_text = spec.get('notfound_text', '').lower()
        body = (resp.text or '').lower()
        exists = notfound_text not in body

    return name, url, ('found' if exists else 'not_found'), resp.status_code


def search_username(username, max_workers=25, progress_cb=None):
    """Busca un username en todas las plataformas registradas. Devuelve dict de resultados."""
    if not ensure_requests():
        return {}

    sites = load_sites()
    results = {}
    session = new_session()

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {
            ex.submit(_check_site, session, name, spec, username): name
            for name, spec in sites.items()
        }
        done = 0
        total = len(futures)
        for fut in concurrent.futures.as_completed(futures):
            name = futures[fut]
            try:
                site_name, url, status, code = fut.result()
            except Exception:
                site_name, url, status, code = name, '', 'error', None
            results[site_name] = {'url': url, 'status': status, 'http_code': code}
            done += 1
            if progress_cb:
                progress_cb(done, total, site_name, status)

    return results


def run(username=None, session_dir=None, silent=False, graph=None):
    if not silent:
        banner()
        hdr(28, "Username Recon", f"Búsqueda nativa en {len(load_sites())} plataformas — sin binarios externos")
        username = username or inp("Username a buscar: ")
        if not username:
            pause()
            return None

    if not silent:
        total = len(load_sites())
        print(f"\n  {cy('→')} Consultando {total} plataformas en paralelo...\n")

        def progress(done, total, name, status):
            mark = g('✓') if status == 'found' else (dm('·') if status == 'not_found' else y('!'))
            print(f"  {mark} {dm(f'[{done}/{total}]')} {name}")

        results = search_username(username, progress_cb=progress)
    else:
        results = search_username(username)

    found = {k: v for k, v in results.items() if v['status'] == 'found'}
    not_found = {k: v for k, v in results.items() if v['status'] == 'not_found'}
    errors = {k: v for k, v in results.items() if v['status'] == 'error'}

    if graph is not None:
        graph.add_entity('username', username, {'source': 'username_recon'})
        for site, info in found.items():
            graph.add_entity('profile', info['url'], {'platform': site})
            graph.add_relation(username, info['url'], f'profile_on_{site}')

    if not silent:
        print(f"\n  {C.BD}{C.CY}── RESULTADOS: {username} ──{C.RS}\n")
        print(f"  {g(f'✓ {len(found)} encontrados')}   {dm(f'· {len(not_found)} no encontrados')}   "
              f"{y(f'! {len(errors)} errores/timeout')}\n")
        for name, info in sorted(found.items()):
            print(f"    {g('✓')} {w(name):<20} {cy(info['url'])}")

        case = new_case(f'username_{username}')
        save_file(case / 'found.json', json.dumps(found, indent=2))
        save_file(case / 'full_results.json', json.dumps(results, indent=2))
        lines = [f"# Username Recon: {username}", f"Fecha: {datetime.now()}", "",
                 f"Encontrados: {len(found)} / {len(results)}", ""]
        for name, info in sorted(found.items()):
            lines.append(f"- **{name}**: {info['url']}")
        save_file(case / 'report.md', '\n'.join(lines))
        print(f"\n  {g('✓')} Resultados guardados en: {case}")
        pause()

    return {'username': username, 'found': found, 'not_found': not_found, 'errors': errors}


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
