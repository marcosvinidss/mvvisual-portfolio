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

arq.write_text(fonte, encoding="utf-8")
print("index.html atualizado.")
