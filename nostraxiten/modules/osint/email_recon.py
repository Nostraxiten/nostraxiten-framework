"""
Email Recon — validación, MX, Gravatar, Hunter.io y HaveIBeenPwned (breach check).
"""
import hashlib
import json
import re
import socket
from datetime import datetime

from core.colors import cy, g, y, r, dm, w, C
from core.utils import new_session as new_case, save_file, pause, inp, banner, hdr
from core.http import new_session, safe_get, ensure_requests
from config.settings import settings

EMAIL_RE = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')


def validate_syntax(email):
    return bool(EMAIL_RE.match(email.strip()))


def check_mx(domain):
    try:
        import dns.resolver
        resolver = dns.resolver.Resolver()
        resolver.timeout = 5
        resolver.lifetime = 5
        answers = resolver.resolve(domain, 'MX')
        return sorted(str(a.exchange).rstrip('.') for a in answers)
    except ImportError:
        try:
            socket.gethostbyname(domain)
            return ['(dnspython no instalado — solo se confirmó que el dominio resuelve)']
        except Exception:
            return []
    except Exception:
        return []


def gravatar_check(email):
    if not ensure_requests():
        return {'exists': False, 'note': 'requests no disponible'}
    h = hashlib.md5(email.strip().lower().encode()).hexdigest()
    session = new_session()
    avatar_resp = safe_get(session, f'https://www.gravatar.com/avatar/{h}?d=404', timeout=8)
    exists = avatar_resp is not None and avatar_resp.status_code == 200
    profile = None
    if exists:
        prof_resp = safe_get(session, f'https://www.gravatar.com/{h}.json', timeout=8)
        if prof_resp is not None and prof_resp.status_code == 200:
            try:
                profile = prof_resp.json()
            except Exception:
                profile = None
    return {'exists': exists, 'hash': h, 'avatar_url': f'https://www.gravatar.com/avatar/{h}', 'profile': profile}


def hunter_verify(email):
    if not settings.hunter_api_key:
        return {'available': False, 'note': 'Configura hunter_api_key en el menú de configuración'}
    if not ensure_requests():
        return {'available': False, 'note': 'requests no disponible'}
    session = new_session()
    resp = safe_get(session, 'https://api.hunter.io/v2/email-verifier',
                     params={'email': email, 'api_key': settings.hunter_api_key}, timeout=10)
    if resp is None:
        return {'available': True, 'error': 'sin respuesta de Hunter.io'}
    try:
        data = resp.json()
    except Exception:
        return {'available': True, 'error': f'HTTP {resp.status_code}'}
    return {'available': True, 'data': data.get('data', data)}


def hunter_domain_search(domain):
    if not settings.hunter_api_key:
        return {'available': False}
    if not ensure_requests():
        return {'available': False}
    session = new_session()
    resp = safe_get(session, 'https://api.hunter.io/v2/domain-search',
                     params={'domain': domain, 'api_key': settings.hunter_api_key}, timeout=10)
    if resp is None:
        return {'available': True, 'error': 'sin respuesta'}
    try:
        data = resp.json()
    except Exception:
        return {'available': True, 'error': f'HTTP {resp.status_code}'}
    return {'available': True, 'data': data.get('data', data)}


def hibp_breach_check(email):
    hibp_key = getattr(settings, 'hibp_api_key', '')
    if not hibp_key:
        return {'available': False, 'note': 'Configura hibp_api_key (HaveIBeenPwned) en el menú de configuración'}
    if not ensure_requests():
        return {'available': False, 'note': 'requests no disponible'}
    session = new_session({'hibp-api-key': hibp_key})
    resp = safe_get(session, f'https://haveibeenpwned.com/api/v3/breachedaccount/{email}',
                     params={'truncateResponse': 'false'}, timeout=10)
    if resp is None:
        return {'available': True, 'error': 'sin respuesta de HIBP'}
    if resp.status_code == 404:
        return {'available': True, 'breached': False, 'breaches': []}
    if resp.status_code == 200:
        try:
            return {'available': True, 'breached': True, 'breaches': resp.json()}
        except Exception:
            return {'available': True, 'error': 'respuesta inválida'}
    return {'available': True, 'error': f'HTTP {resp.status_code}'}


def run(email=None, session_dir=None, silent=False, graph=None):
    if not silent:
        banner()
        hdr(29, "Email Recon", "Validación, MX, Gravatar, Hunter.io y HaveIBeenPwned breach-check")
        email = email or inp("Email objetivo: ")
        if not email:
            pause()
            return None

    email = email.strip()
    results = {'email': email, 'timestamp': str(datetime.now())}
    results['valid_syntax'] = validate_syntax(email)
    domain = email.split('@')[-1] if '@' in email else ''

    if not silent:
        print(f"\n  {cy('→')} Validando sintaxis y MX...")
    results['mx'] = check_mx(domain) if domain else []

    if not silent:
        print(f"  {cy('→')} Consultando Gravatar...")
    results['gravatar'] = gravatar_check(email)

    if not silent:
        print(f"  {cy('→')} Consultando Hunter.io...")
    results['hunter'] = hunter_verify(email)

    if not silent:
        print(f"  {cy('→')} Consultando HaveIBeenPwned (breaches)...")
    results['hibp'] = hibp_breach_check(email)

    if graph is not None:
        graph.add_entity('email', email, {'source': 'email_recon', 'valid_syntax': results['valid_syntax']})
        if domain:
            graph.add_entity('domain', domain, {})
            graph.add_relation(email, domain, 'belongs_to_domain')
        if results['gravatar'].get('exists'):
            graph.add_entity('gravatar_profile', results['gravatar']['avatar_url'], {})
            graph.add_relation(email, results['gravatar']['avatar_url'], 'has_gravatar')
        if results['hibp'].get('breached'):
            for b in results['hibp'].get('breaches', []):
                bname = b.get('Name', 'unknown') if isinstance(b, dict) else str(b)
                graph.add_entity('breach', bname, {})
                graph.add_relation(email, bname, 'found_in_breach')

    if not silent:
        _print_summary(results)
        case = new_case(f'email_recon_{email.replace("@", "_at_")}')
        save_file(case / 'full_results.json', json.dumps(results, indent=2, default=str))
        print(f"\n  {g('✓')} Resultados guardados en: {case}")
        pause()

    return results


def _print_summary(results):
    print(f"\n  {C.BD}{C.CY}── RESUMEN: {results['email']} ──{C.RS}\n")
    print(f"  {w('Sintaxis válida')}: {g('Sí') if results['valid_syntax'] else r('No')}")
    print(f"  {w('MX records')}: {', '.join(results['mx']) if results['mx'] else dm('ninguno')}")

    grav = results['gravatar']
    print(f"\n  {w('Gravatar')}: {g('existe') if grav.get('exists') else dm('sin cuenta')}")
    if grav.get('profile'):
        entry = grav['profile'].get('entry', [{}])[0]
        print(f"    {dm('Display name:')} {entry.get('displayName', '?')}")

    hunter = results['hunter']
    print(f"\n  {w('Hunter.io')}: ", end='')
    if not hunter.get('available'):
        print(dm(hunter.get('note', 'no configurado')))
    elif hunter.get('data'):
        d = hunter['data']
        print(f"score={d.get('score', '?')} status={d.get('status', '?')} disposable={d.get('disposable', '?')}")
    else:
        print(y(hunter.get('error', 'sin datos')))

    hibp = results['hibp']
    print(f"\n  {w('HaveIBeenPwned')}: ", end='')
    if not hibp.get('available'):
        print(dm(hibp.get('note', 'no configurado')))
    elif hibp.get('breached'):
        names = [b.get('Name', '?') if isinstance(b, dict) else str(b) for b in hibp.get('breaches', [])]
        print(r(f'¡COMPROMETIDO! en {len(names)} brechas: ') + ', '.join(names[:8]))
    elif 'breached' in hibp:
        print(g('sin brechas conocidas'))
    else:
        print(y(hibp.get('error', 'sin datos')))


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
