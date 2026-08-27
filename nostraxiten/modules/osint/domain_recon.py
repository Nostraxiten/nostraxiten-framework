"""
Domain Recon — WHOIS, DNS, subdominios (crt.sh) y fingerprint HTTP, 100% nativo.
"""
import json
import socket
import ssl
import concurrent.futures
from datetime import datetime

from core.colors import cy, g, y, r, dm, w, C
from core.utils import new_session as new_case, save_file, pause, inp, banner, hdr
from core.http import new_session, safe_get, ensure_requests

COMMON_PORTS = {
    21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS', 80: 'HTTP',
    110: 'POP3', 143: 'IMAP', 443: 'HTTPS', 445: 'SMB', 587: 'SMTP-TLS',
    993: 'IMAPS', 995: 'POP3S', 3306: 'MySQL', 3389: 'RDP', 5432: 'PostgreSQL',
    6379: 'Redis', 8080: 'HTTP-Alt', 8443: 'HTTPS-Alt', 27017: 'MongoDB',
}

TECH_SIGNATURES = {
    'WordPress': ['wp-content', 'wp-includes', 'wordpress'],
    'Joomla': ['joomla', '/media/jui/'],
    'Drupal': ['drupal', 'sites/default/files'],
    'Shopify': ['cdn.shopify.com', 'shopify'],
    'React': ['__next', 'react-root', '_reactroot'],
    'Next.js': ['__next', '/_next/'],
    'Angular': ['ng-version', 'angular'],
    'Vue.js': ['__vue__', 'data-v-'],
    'Laravel': ['laravel_session', 'XSRF-TOKEN'],
    'Django': ['csrftoken', 'django'],
    'Nginx': [],
    'Apache': [],
    'Cloudflare': [],
    'IIS': [],
}


def whois_lookup(domain):
    """Cliente WHOIS nativo vía sockets (puerto 43), con seguimiento de referral."""
    tld = domain.rsplit('.', 1)[-1].lower()
    iana_result = _whois_query('whois.iana.org', domain)
    server = None
    if iana_result:
        for line in iana_result.splitlines():
            if line.lower().startswith('refer:'):
                server = line.split(':', 1)[1].strip()
                break
    if not server:
        server = f'whois.nic.{tld}'

    result = _whois_query(server, domain)
    if not result or len(result.strip()) < 20:
        result = _whois_query('whois.verisign-grs.com', domain) or result
    return result or '(sin respuesta WHOIS — servidor no disponible para este TLD)'


def _whois_query(server, domain, timeout=6):
    try:
        with socket.create_connection((server, 43), timeout=timeout) as s:
            s.send((domain + '\r\n').encode())
            chunks = []
            while True:
                data = s.recv(4096)
                if not data:
                    break
                chunks.append(data)
            return b''.join(chunks).decode(errors='replace')
    except Exception:
        return None


def dns_records(domain):
    """Resuelve registros DNS. Usa dnspython si está disponible (MX/NS/TXT/SOA),
    con fallback a resolución A/AAAA vía socket si no lo está."""
    records = {}
    try:
        import dns.resolver
        resolver = dns.resolver.Resolver()
        resolver.timeout = 5
        resolver.lifetime = 5
        for rtype in ('A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA', 'CNAME'):
            try:
                answers = resolver.resolve(domain, rtype)
                records[rtype] = [str(a).strip() for a in answers]
            except Exception:
                records[rtype] = []
    except ImportError:
        try:
            addrs = socket.getaddrinfo(domain, None)
            ipv4 = sorted({a[4][0] for a in addrs if a[0] == socket.AF_INET})
            ipv6 = sorted({a[4][0] for a in addrs if a[0] == socket.AF_INET6})
            records['A'] = ipv4
            records['AAAA'] = ipv6
        except Exception:
            records['A'] = []
            records['AAAA'] = []
        records['_note'] = "Instala 'dnspython' (pip install dnspython) para MX/NS/TXT/SOA/CNAME."
    return records


def subdomains_crtsh(domain, timeout=15):
    """Enumera subdominios vía Certificate Transparency logs (crt.sh)."""
    if not ensure_requests():
        return []
    session = new_session()
    resp = safe_get(session, f'https://crt.sh/?q=%25.{domain}&output=json', timeout=timeout)
    found = set()
    if resp is not None and resp.status_code == 200:
        try:
            data = resp.json()
            for entry in data:
                name = entry.get('name_value', '')
                for line in name.split('\n'):
                    line = line.strip().lower()
                    if line.endswith(domain) and '*' not in line:
                        found.add(line)
        except Exception:
            pass
    return sorted(found)


def resolve_subdomains(subs, max_workers=30):
    """Resuelve cuáles subdominios están activos (tienen IP)."""
    alive = {}

    def _resolve(sub):
        try:
            ip = socket.gethostbyname(sub)
            return sub, ip
        except Exception:
            return sub, None

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        for sub, ip in ex.map(_resolve, subs):
            if ip:
                alive[sub] = ip
    return alive


def http_fingerprint(domain):
    """Cabeceras HTTP, certificado TLS y detección heurística de tecnologías."""
    result = {'https': None, 'http': None, 'tls': None, 'tech': []}
    if not ensure_requests():
        return result
    session = new_session()

    for scheme in ('https', 'http'):
        resp = safe_get(session, f'{scheme}://{domain}', timeout=8)
        if resp is not None:
            body_lower = resp.text.lower()[:20000] if resp.text else ''
            headers = dict(resp.headers)
            result[scheme] = {
                'status': resp.status_code,
                'headers': headers,
                'server': headers.get('Server', ''),
                'powered_by': headers.get('X-Powered-By', ''),
            }
            server = headers.get('Server', '')
            if 'nginx' in server.lower():
                result['tech'].append('Nginx')
            if 'apache' in server.lower():
                result['tech'].append('Apache')
            if 'cloudflare' in server.lower() or 'cf-ray' in {k.lower() for k in headers}:
                result['tech'].append('Cloudflare')
            if 'microsoft-iis' in server.lower():
                result['tech'].append('IIS')
            for tech, markers in TECH_SIGNATURES.items():
                if tech in result['tech']:
                    continue
                if any(mk in body_lower for mk in markers):
                    result['tech'].append(tech)

    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=6) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                subject = dict(x[0] for x in cert.get('subject', []))
                issuer = dict(x[0] for x in cert.get('issuer', []))
                result['tls'] = {
                    'subject_cn': subject.get('commonName', ''),
                    'issuer': issuer.get('commonName', ''),
                    'valid_from': cert.get('notBefore', ''),
                    'valid_to': cert.get('notAfter', ''),
                    'san': [x[1] for x in cert.get('subjectAltName', []) if x[0] == 'DNS'],
                }
    except Exception:
        pass

    return result


def port_scan(host, ports=None, timeout=1.0, max_workers=50):
    """Barrido ligero de puertos comunes vía TCP connect() — sin privilegios root."""
    ports = ports or list(COMMON_PORTS.keys())
    open_ports = {}

    def _check(port):
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return port, True
        except Exception:
            return port, False

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        for port, is_open in ex.map(_check, ports):
            if is_open:
                open_ports[port] = COMMON_PORTS.get(port, 'unknown')
    return open_ports


def run(domain=None, session_dir=None, silent=False, graph=None):
    """Ejecuta el recon completo. Si silent=True, no imprime menú (uso desde investigate.py)."""
    if not silent:
        banner()
        hdr(27, "Domain Recon", "WHOIS + DNS + Subdominios (crt.sh) + Fingerprint HTTP + Puertos")
        domain = domain or inp("Dominio objetivo (ej: example.com): ")
        if not domain:
            pause()
            return None

    domain = domain.strip().lower().replace('http://', '').replace('https://', '').split('/')[0]
    results = {'domain': domain, 'timestamp': str(datetime.now())}

    if not silent:
        print(f"\n  {cy('→')} WHOIS...")
    results['whois'] = whois_lookup(domain)

    if not silent:
        print(f"  {cy('→')} DNS records...")
    results['dns'] = dns_records(domain)

    if not silent:
        print(f"  {cy('→')} Subdominios (crt.sh)...")
    subs = subdomains_crtsh(domain)
    results['subdomains_found'] = subs
    if not silent:
        print(f"    {g(str(len(subs)))} subdominios únicos encontrados")
        print(f"  {cy('→')} Resolviendo subdominios activos (puede tardar)...")
    alive = resolve_subdomains(subs[:200])
    results['subdomains_alive'] = alive

    if not silent:
        print(f"  {cy('→')} Fingerprint HTTP/TLS/tecnologías...")
    results['http'] = http_fingerprint(domain)

    if not silent:
        print(f"  {cy('→')} Barrido de puertos comunes...")
    root_ip = results['dns'].get('A', [None])[0] if results['dns'].get('A') else None
    target_host = root_ip or domain
    results['open_ports'] = port_scan(target_host) if target_host else {}

    if graph is not None:
        graph.add_entity('domain', domain, {'source': 'domain_recon'})
        for sub, ip in alive.items():
            graph.add_entity('subdomain', sub, {'ip': ip})
            graph.add_relation(domain, sub, 'has_subdomain')
            if ip:
                graph.add_entity('ip', ip, {})
                graph.add_relation(sub, ip, 'resolves_to')
        for tech in results['http'].get('tech', []):
            graph.add_entity('technology', tech, {})
            graph.add_relation(domain, tech, 'uses_tech')
        for port, service in results['open_ports'].items():
            graph.add_entity('port', f'{target_host}:{port}', {'service': service})
            graph.add_relation(domain, f'{target_host}:{port}', 'open_port')

    if not silent:
        _print_summary(results)
        case = new_case(f'domain_recon_{domain.replace(".", "_")}')
        save_file(case / 'whois.txt', results['whois'])
        save_file(case / 'dns_records.json', json.dumps(results['dns'], indent=2))
        save_file(case / 'subdomains.json', json.dumps({'found': subs, 'alive': alive}, indent=2))
        save_file(case / 'http_fingerprint.json', json.dumps(results['http'], indent=2, default=str))
        save_file(case / 'open_ports.json', json.dumps(results['open_ports'], indent=2))
        save_file(case / 'full_results.json', json.dumps(results, indent=2, default=str))
        print(f"\n  {g('✓')} Resultados guardados en: {case}")
        pause()

    return results


def _print_summary(results):
    print(f"\n  {C.BD}{C.CY}── RESUMEN: {results['domain']} ──{C.RS}\n")

    dns = results['dns']
    print(f"  {w('DNS')}")
    for rtype in ('A', 'AAAA', 'MX', 'NS', 'TXT'):
        vals = dns.get(rtype, [])
        if vals:
            print(f"    {cy(rtype):<20} {', '.join(vals[:5])}")
    if dns.get('_note'):
        print(f"    {y(dns['_note'])}")

    print(f"\n  {w('Subdominios')}: {g(str(len(results['subdomains_found'])))} encontrados, "
          f"{g(str(len(results['subdomains_alive'])))} activos")
    for sub, ip in list(results['subdomains_alive'].items())[:10]:
        print(f"    {dm('•')} {sub} {dm('→')} {ip}")
    remaining = len(results['subdomains_alive']) - 10
    if remaining > 0:
        print(f"    {dm(f'... y {remaining} más (ver JSON)')}")

    http = results['http']
    print(f"\n  {w('HTTP/TLS')}")
    for scheme in ('https', 'http'):
        info = http.get(scheme)
        if info:
            print(f"    {cy(scheme.upper())} [{info['status']}] Server: {info['server'] or '?'}")
    if http.get('tls'):
        tls = http['tls']
        print(f"    {cy('Cert CN')}: {tls['subject_cn']}  {dm('Issuer:')} {tls['issuer']}  "
              f"{dm('Válido hasta:')} {tls['valid_to']}")
    if http.get('tech'):
        print(f"    {cy('Tecnologías')}: {', '.join(http['tech'])}")

    ports = results['open_ports']
    print(f"\n  {w('Puertos abiertos')}: ", end='')
    if ports:
        print(', '.join(f"{p}/{s}" for p, s in sorted(ports.items())))
    else:
        print(dm('ninguno detectado'))


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario.")
