"""
Entity Graph — motor de correlación de entidades (dominios, IPs, emails, usernames,
perfiles, brechas...) descubiertas durante una investigación. Es el diferenciador
frente a herramientas que solo listan resultados sueltos por módulo: aquí se
correlacionan en un único grafo exportable.
"""
import json
from datetime import datetime


class EntityGraph:
    def __init__(self, case_name='investigacion'):
        self.case_name = case_name
        self.created = str(datetime.now())
        self.nodes = {}   # value -> {type, attrs}
        self.edges = []   # (src, dst, relation)

    def add_entity(self, etype, value, attrs=None):
        value = str(value)
        if value in self.nodes:
            self.nodes[value]['attrs'].update(attrs or {})
        else:
            self.nodes[value] = {'type': etype, 'attrs': attrs or {}}
        return value

    def add_relation(self, src, dst, relation):
        src, dst = str(src), str(dst)
        if src not in self.nodes:
            self.add_entity('unknown', src)
        if dst not in self.nodes:
            self.add_entity('unknown', dst)
        edge = (src, dst, relation)
        if edge not in self.edges:
            self.edges.append(edge)

    def merge(self, other):
        for value, data in other.nodes.items():
            self.add_entity(data['type'], value, data['attrs'])
        for src, dst, rel in other.edges:
            self.add_relation(src, dst, rel)

    def stats(self):
        by_type = {}
        for data in self.nodes.values():
            by_type[data['type']] = by_type.get(data['type'], 0) + 1
        return {'nodes': len(self.nodes), 'edges': len(self.edges), 'by_type': by_type}

    def to_dict(self):
        return {
            'case_name': self.case_name,
            'created': self.created,
            'nodes': self.nodes,
            'edges': self.edges,
        }

    def save_json(self, path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, default=str)

    @classmethod
    def load_json(cls, path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        g = cls(data.get('case_name', 'investigacion'))
        g.created = data.get('created', g.created)
        g.nodes = data.get('nodes', {})
        g.edges = [tuple(e) for e in data.get('edges', [])]
        return g

    def export_dot(self, path):
        lines = [f'digraph "{self.case_name}" {{', '  rankdir=LR;', '  node [shape=box, style=filled, fontname="Helvetica"];']
        colors = {
            'domain': '#2b6cb0', 'subdomain': '#4299e1', 'ip': '#805ad5', 'port': '#d69e2e',
            'technology': '#38a169', 'username': '#dd6b20', 'profile': '#ed8936',
            'email': '#e53e3e', 'breach': '#c53030', 'gravatar_profile': '#f56565',
            'gps_location': '#319795', 'file': '#718096', 'unknown': '#a0aec0',
        }
        for value, data in self.nodes.items():
            safe_val = value.replace('"', "'")[:60]
            color = colors.get(data['type'], '#a0aec0')
            lines.append(f'  "{value}" [label="{safe_val}\\n({data["type"]})", fillcolor="{color}", fontcolor=white];')
        for src, dst, rel in self.edges:
            lines.append(f'  "{src}" -> "{dst}" [label="{rel}", fontsize=9];')
        lines.append('}')
        content = '\n'.join(lines)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return content

    def export_html(self, path):
        """Genera una visualización HTML autocontenida (canvas + física simple, sin CDN)."""
        nodes_list = [{'id': v, 'type': d['type'], 'attrs': d['attrs']} for v, d in self.nodes.items()]
        edges_list = [{'source': s, 'target': t, 'relation': r} for s, t, r in self.edges]
        payload = json.dumps({'nodes': nodes_list, 'edges': edges_list, 'case': self.case_name})

        html = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<title>Nostraxiten — Grafo: {self.case_name}</title>
<style>
  body {{ background:#0d1117; color:#e6edf3; font-family: -apple-system, Segoe UI, sans-serif; margin:0; }}
  #hdr {{ padding:16px 24px; border-bottom:1px solid #30363d; }}
  #hdr h1 {{ margin:0; font-size:18px; color:#58a6ff; }}
  #hdr p {{ margin:4px 0 0; color:#8b949e; font-size:13px; }}
  #canvas {{ display:block; background:#0d1117; }}
  #legend {{ position:fixed; top:70px; right:16px; background:#161b22; border:1px solid #30363d;
             border-radius:8px; padding:12px 16px; font-size:12px; max-height:80vh; overflow:auto; }}
  #legend div {{ margin:4px 0; }}
  .dot {{ display:inline-block; width:10px; height:10px; border-radius:50%; margin-right:6px; }}
  #tooltip {{ position:fixed; background:#161b22; border:1px solid #58a6ff; border-radius:6px;
              padding:8px 10px; font-size:12px; pointer-events:none; display:none; max-width:300px; }}
</style></head>
<body>
  <div id="hdr"><h1>Nostraxiten — Grafo de Entidades</h1><p>Caso: {self.case_name} · {len(nodes_list)} nodos · {len(edges_list)} relaciones</p></div>
  <canvas id="canvas"></canvas>
  <div id="legend"></div>
  <div id="tooltip"></div>
<script>
const DATA = {payload};
const COLORS = {{
  domain:'#2b6cb0', subdomain:'#4299e1', ip:'#805ad5', port:'#d69e2e',
  technology:'#38a169', username:'#dd6b20', profile:'#ed8936',
  email:'#e53e3e', breach:'#c53030', gravatar_profile:'#f56565',
  gps_location:'#319795', file:'#718096', unknown:'#a0aec0'
}};
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
function resize() {{ canvas.width = window.innerWidth; canvas.height = window.innerHeight - 70; }}
resize(); window.addEventListener('resize', resize);

const nodes = DATA.nodes.map((n, i) => ({{
  ...n,
  x: canvas.width/2 + Math.cos(i) * 200 + Math.random()*100,
  y: canvas.height/2 + Math.sin(i) * 200 + Math.random()*100,
  vx: 0, vy: 0
}}));
const idx = {{}};
nodes.forEach((n, i) => idx[n.id] = i);
const edges = DATA.edges.filter(e => idx[e.source] !== undefined && idx[e.target] !== undefined);

function step() {{
  const k = 0.02, rep = 3000, damp = 0.85;
  for (let i=0;i<nodes.length;i++) {{
    for (let j=i+1;j<nodes.length;j++) {{
      let dx = nodes[j].x-nodes[i].x, dy = nodes[j].y-nodes[i].y;
      let dist = Math.sqrt(dx*dx+dy*dy)||1;
      let f = rep/(dist*dist);
      dx/=dist; dy/=dist;
      nodes[i].vx -= dx*f; nodes[i].vy -= dy*f;
      nodes[j].vx += dx*f; nodes[j].vy += dy*f;
    }}
  }}
  edges.forEach(e => {{
    const a = nodes[idx[e.source]], b = nodes[idx[e.target]];
    let dx = b.x-a.x, dy = b.y-a.y;
    let dist = Math.sqrt(dx*dx+dy*dy)||1;
    let f = (dist-140)*k;
    dx/=dist; dy/=dist;
    a.vx += dx*f; a.vy += dy*f;
    b.vx -= dx*f; b.vy -= dy*f;
  }});
  nodes.forEach(n => {{
    n.vx *= damp; n.vy *= damp;
    n.x += n.vx; n.y += n.vy;
    n.x = Math.max(30, Math.min(canvas.width-30, n.x));
    n.y = Math.max(30, Math.min(canvas.height-30, n.y));
  }});
}}

function draw() {{
  ctx.clearRect(0,0,canvas.width,canvas.height);
  ctx.strokeStyle = '#30363d';
  edges.forEach(e => {{
    const a = nodes[idx[e.source]], b = nodes[idx[e.target]];
    ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(b.x,b.y); ctx.stroke();
  }});
  nodes.forEach(n => {{
    ctx.beginPath();
    ctx.fillStyle = COLORS[n.type] || COLORS.unknown;
    ctx.arc(n.x, n.y, 9, 0, Math.PI*2);
    ctx.fill();
    ctx.fillStyle = '#e6edf3';
    ctx.font = '10px sans-serif';
    const label = n.id.length > 24 ? n.id.slice(0,24)+'…' : n.id;
    ctx.fillText(label, n.x+12, n.y+4);
  }});
}}

function loop() {{ step(); draw(); requestAnimationFrame(loop); }}
loop();

const tooltip = document.getElementById('tooltip');
canvas.addEventListener('mousemove', (ev) => {{
  const rect = canvas.getBoundingClientRect();
  const mx = ev.clientX - rect.left, my = ev.clientY - rect.top;
  let hit = null;
  for (const n of nodes) {{
    if (Math.hypot(n.x-mx, n.y-my) < 12) {{ hit = n; break; }}
  }}
  if (hit) {{
    tooltip.style.display = 'block';
    tooltip.style.left = (ev.clientX+14)+'px';
    tooltip.style.top = (ev.clientY+14)+'px';
    tooltip.innerHTML = '<b>'+hit.id+'</b><br>tipo: '+hit.type+'<br>'+JSON.stringify(hit.attrs);
  }} else {{
    tooltip.style.display = 'none';
  }}
}});

const legend = document.getElementById('legend');
const types = [...new Set(nodes.map(n => n.type))];
legend.innerHTML = '<b>Leyenda</b><br>' + types.map(t =>
  '<div><span class="dot" style="background:'+(COLORS[t]||COLORS.unknown)+'"></span>'+t+'</div>'
).join('');
</script>
</body></html>"""
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        return path
