"""Gera as partes estáticas do index.html a partir dos dados do bloco "EDITE AQUI".

Por que existe: os buscadores e os apps que montam a prévia de link (WhatsApp, Instagram)
nem sempre rodam JavaScript. Este script escreve no HTML, entre comentários GERADO,
o mesmo conteúdo que o JavaScript monta na tela. Os dados continuam num lugar só: o bloco EDITE AQUI.

Uso, na pasta do portfólio (não precisa instalar nada):
    python3 scripts/gerar-estatico.py
Rode sempre que mudar SITE_URL, CONTATO, PROJETOS, SITES_IA ou SERVICOS.
"""
import html, json, re, sys
from pathlib import Path

raiz = Path(__file__).resolve().parent.parent
arq = raiz / "index.html"
fonte = arq.read_text(encoding="utf-8")


def js_para_python(texto):
    """Converte um literal JS simples (objetos/listas com chaves sem aspas) em dado Python."""
    t = re.sub(r"/\*.*?\*/", "", texto, flags=re.S)             # comentários /* */
    t = re.sub(r"(?m)^\s*//.*$", "", t)                         # linhas de comentário //
    t = re.sub(r"(?m)\s//[^\"\n]*$", "", t)                     # // no fim da linha (fora de strings com aspas)
    t = re.sub(r"'([^'\\]*)'", lambda m: json.dumps(m.group(1)), t)  # 'texto' -> "texto"
    t = re.sub(r"([{,]\s*)([A-Za-z_]\w*)\s*:", r'\1"\2":', t)   # chave: -> "chave":
    t = re.sub(r",(\s*[}\]])", r"\1", t)                        # vírgula final
    return json.loads(t)


def ler(nome, obrigatorio=True):
    m = re.search(r"const " + nome + r"\s*=\s*", fonte)
    if not m:
        if obrigatorio:
            sys.exit(f"Não achei 'const {nome}' no index.html")
        return None
    i = m.end()
    if fonte[i] == '"':
        return json.loads(fonte[i:fonte.index('"', i + 1) + 1])
    abre = fonte[i]; fecha = "}" if abre == "{" else "]"
    nivel, j, aspas = 0, i, False
    while True:
        c = fonte[j]
        if c == '"' and fonte[j - 1] != "\\":
            aspas = not aspas
        elif not aspas and c in "{[":
            nivel += 1
        elif not aspas and c in "}]":
            nivel -= 1
            if nivel == 0:
                break
        j += 1
    return js_para_python(fonte[i:j + 1])


def trocar(texto, marca, conteudo, indent=""):
    padrao = re.compile(r"(<!-- " + marca + r":INICIO[^>]*-->)(.*?)(" + r"[ \t]*<!-- " + marca + r":FIM -->)", re.S)
    if not padrao.search(texto):
        sys.exit(f"Não achei os comentários {marca}:INICIO / {marca}:FIM no index.html")
    corpo = "\n".join(indent + l if l else l for l in conteudo.strip("\n").split("\n"))
    return padrao.sub(lambda m: m.group(1) + "\n" + corpo + "\n" + m.group(3), texto, count=1)


e = html.escape
url = ler("SITE_URL")
contato = ler("CONTATO")
titulo = re.search(r"<title>(.*?)</title>", fonte).group(1)
descricao = re.search(r'<meta name="description" content="([^"]*)"', fonte).group(1)

# ---------- <head>: prévia de link + canonical + dados estruturados
ld = {
    "@context": "https://schema.org",
    "@type": ["ProfessionalService", "LocalBusiness"],
    "name": "mvvisual.co",
    "description": html.unescape(descricao),
    "url": url,
    "image": url + "og-image.jpg",
    "logo": url + "apple-touch-icon.png",
    "email": contato["email"],
    "telephone": "+" + contato["whatsapp"],
    "address": {"@type": "PostalAddress", "addressLocality": "Brasília", "addressRegion": "DF", "addressCountry": "BR"},
    "areaServed": "Brasil",
    "sameAs": [f"https://www.instagram.com/{contato['instagram']}/", f"https://wa.me/{contato['whatsapp']}"],
}
head = f"""<link rel="canonical" href="{e(url)}">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="mvvisual.co">
<meta property="og:title" content="{titulo}">
<meta property="og:description" content="{descricao}">
<meta property="og:url" content="{e(url)}">
<meta property="og:image" content="{e(url)}og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="mvvisual.co — Vídeo · Sites · Design">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{titulo}">
<meta name="twitter:description" content="{descricao}">
<meta name="twitter:image" content="{e(url)}og-image.jpg">
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
</script>"""
fonte = trocar(fonte, "GERADO-HEAD", head)

# ---------- Seções: versão estática do que o JavaScript monta (o JS substitui ao carregar)
def trocar_secao(texto, nome, conteudo, indent):
    padrao = re.compile(r"(<!-- GERADO:INICIO " + nome + r" -->)(.*?)([ \t]*<!-- GERADO:FIM " + nome + r" -->)", re.S)
    if not padrao.search(texto):
        sys.exit(f"Não achei <!-- GERADO:INICIO {nome} --> no index.html")
    corpo = "\n".join(indent + l for l in conteudo.strip("\n").split("\n")) if conteudo.strip() else ""
    return padrao.sub(lambda m: m.group(1) + ("\n" + corpo if corpo else "") + "\n" + m.group(3), texto, count=1)

servicos = ler("SERVICOS")
projetos = ler("PROJETOS")
sites = ler("SITES_IA")
capa = ler("REEL_CAPA")

html_serv = "\n".join(
    f'<li><div class="row"><span class="n">{i:02d}</span><span class="t">{e(t)}</span><span class="d">{e(d)}</span></div></li>'
    for i, (t, d) in enumerate(servicos, 1))

def vertical(p):
    return p.get("formato") != "16:9" or p.get("conteudo") == "vertical"

html_cases = "\n".join(
    f'<article class="item"><a class="thumb" href="{e(p["instagram"])}" target="_blank" rel="noopener" style="aspect-ratio:{"4/5" if vertical(p) else "16/9"}">'
    f'<span class="lbl"><span>{e(p["cliente"])}</span><span>{e(p["categoria"])}</span></span>'
    f'<span class="ttl"><b>{e(p["titulo"])}</b></span></a></article>'
    for p in projetos if p["instagram"] != capa["link"])

html_clientes = "\n".join(f"<li>{e(c)}</li>" for c in dict.fromkeys(p["cliente"] for p in projetos))

def host(u):
    return re.sub(r"^https?://", "", u).rstrip("/")

partes = []
for s in sites:
    img = (f'<img src="sites/{e(s["print"])}.jpg" alt="Prévia do site {e(s["titulo"])} — {e(s["cliente"])}" width="1200" height="750" loading="lazy" decoding="async">'
           if s.get("print") and s.get("link") and (raiz / "sites" / f'{s["print"]}.jpg').exists()
           else '<div class="soon">Prévia em breve</div>')
    abre = f'<a class="site" href="{e(s["link"])}" target="_blank" rel="noopener">' if s.get("link") else '<div class="site">'
    fecha = "</a>" if s.get("link") else "</div>"
    partes.append(
        f'{abre}<div class="meta mono"><span>{e(s["cliente"])}</span><span class="dim">{e(s["tipo"])}</span></div>'
        f'<div class="browser"><div class="chrome"><i></i><i></i><i></i><span class="url">{e(host(s["link"])) if s.get("link") else "—"}</span></div><div class="view">{img}</div></div>'
        f'<h3>{e(s["titulo"])}</h3><p>{e(s["descricao"])}</p>{fecha}')
html_sites = "\n".join(partes)

fonte = trocar_secao(fonte, "servicos", html_serv, "    ")
fonte = trocar_secao(fonte, "cases", html_cases, "    ")
fonte = trocar_secao(fonte, "clientes", html_clientes, "      ")
fonte = trocar_secao(fonte, "sites", html_sites, "    ")

arq.write_text(fonte, encoding="utf-8")
print("index.html atualizado.")
