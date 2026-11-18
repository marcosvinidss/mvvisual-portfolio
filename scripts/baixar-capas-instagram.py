"""Baixa a imagem de capa de cada reel do Instagram e salva em capas/<arquivo>.jpg.

Serve para as miniaturas dos cases ficarem nítidas e no tamanho certo, sem depender do embed.
Lê PROJETOS do index.html. Pula projetos que já têm capas/<arquivo>.jpg (use --refazer para sobrescrever).
Depois de rodar, marque capa: true nos projetos (o script avisa quais).

Precisa de Playwright e Pillow (só no seu computador):
    python3 -m pip install playwright pillow
    python3 -m playwright install chromium
Uso, na pasta do portfólio:
    python3 scripts/baixar-capas-instagram.py [--refazer]
"""
import io, re, sys
from pathlib import Path
from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

raiz = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(raiz / "scripts"))
fonte = (raiz / "index.html").read_text(encoding="utf-8")
# reaproveita o leitor de dados do gerar-estatico.py
src = (raiz / "scripts" / "gerar-estatico.py").read_text(encoding="utf-8")
ns = {"re": re, "json": __import__("json"), "fonte": fonte, "sys": sys}
exec(src[src.index("def js_para_python"):src.index("def trocar(")], ns)
projetos = ns["ler"]("PROJETOS")
refazer = "--refazer" in sys.argv


def embed(link):
    m = re.search(r"/(p|reel|reels|tv)/([^/?#]+)", link)
    return f"https://www.instagram.com/{'reel' if m.group(1) == 'reels' else m.group(1)}/{m.group(2)}/embed/"


def tirar_faixas(img):
    """Remove faixas pretas (pillarbox/letterbox) em volta da imagem."""
    cinza = img.convert("L").point(lambda v: 255 if v > 18 else 0)
    caixa = cinza.getbbox()
    return img.crop(caixa) if caixa else img


def recortar(img, proporcao):
    """Recorte central na proporção largura/altura pedida."""
    w, h = img.size
    if w / h > proporcao:
        nw = int(h * proporcao); x = (w - nw) // 2
        return img.crop((x, 0, x + nw, h))
    nh = int(w / proporcao); y = (h - nh) // 2
    return img.crop((0, y, w, y + nh))


(raiz / "capas").mkdir(exist_ok=True)
feitos = []
with sync_playwright() as p:
    nav = p.chromium.launch()
    pag = nav.new_page(viewport={"width": 1080, "height": 1400})
    for pr in projetos:
        destino = raiz / "capas" / f'{pr["arquivo"]}.jpg'
        if destino.exists() and not refazer:
            print(f"= {pr['arquivo']} (já existe)"); feitos.append(pr["arquivo"]); continue
        pag.goto(embed(pr["instagram"]), wait_until="networkidle", timeout=60000)
        url = pag.evaluate("""() => { const i = document.querySelector('.EmbeddedMediaImage');
            if(!i) return null; const s = (i.srcset || '').split(',').map(x => x.trim().split(' '));
            s.sort((a, b) => parseInt(b[1]) - parseInt(a[1])); return (s[0] && s[0][0]) || i.currentSrc || i.src; }""")
        if not url:
            print(f"! {pr['arquivo']}: não achei a capa no embed"); continue
        img = Image.open(io.BytesIO(pag.request.get(url).body())).convert("RGB")
        img = tirar_faixas(img)
        vertical = pr.get("formato") != "16:9" or pr.get("conteudo") == "vertical"
        img = recortar(img, 4 / 5 if vertical else 16 / 9)
        largura = 800
        img = img.resize((largura, round(largura * img.height / img.width)), Image.LANCZOS)
        img.save(destino, "JPEG", quality=75, optimize=True, progressive=True)
        feitos.append(pr["arquivo"])
        print(f"→ {pr['arquivo']}: {img.size[0]}x{img.size[1]}  {destino.stat().st_size // 1024} KB")
    nav.close()

faltam = [pr["arquivo"] for pr in projetos if pr["arquivo"] in feitos and not pr.get("capa")]
if faltam:
    print("\nMarque capa: true nestes projetos do index.html:", ", ".join(faltam))
