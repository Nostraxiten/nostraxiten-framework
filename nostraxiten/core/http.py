"""Cliente HTTP compartido para los módulos OSINT nativos."""
import random

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
]


def ensure_requests():
    """Comprueba que 'requests' está disponible; si no, intenta instalarlo."""
    global HAS_REQUESTS
    if HAS_REQUESTS:
        return True
    from core.utils import pip_install
    from core.colors import y
    print(f"  {y('⚠')} La librería 'requests' no está instalada, instalando...")
    pip_install('requests')
    try:
        import requests  # noqa: F401
        HAS_REQUESTS = True
        return True
    except ImportError:
        return False


def new_session(extra_headers=None):
    """Crea una sesión de requests con UA aleatorio y timeouts razonables."""
    if not ensure_requests():
        return None
    import requests
    s = requests.Session()
    s.headers.update({
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
    })
    if extra_headers:
        s.headers.update(extra_headers)
    return s


def safe_get(session, url, timeout=8, allow_redirects=True, **kwargs):
    """GET tolerante a fallos: nunca lanza excepción, devuelve None si falla."""
    try:
        return session.get(url, timeout=timeout, allow_redirects=allow_redirects, **kwargs)
    except Exception:
        return None


def safe_head(session, url, timeout=6, allow_redirects=True, **kwargs):
    try:
        return session.head(url, timeout=timeout, allow_redirects=allow_redirects, **kwargs)
    except Exception:
        return None
