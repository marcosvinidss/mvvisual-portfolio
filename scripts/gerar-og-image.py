"""Gera og-image.jpg (1200x630), a imagem que aparece na prévia do link (WhatsApp, Instagram, LinkedIn).

Precisa de Playwright e Pillow (só no seu computador, não no site):
    python3 -m pip install playwright pillow
    python3 -m playwright install chromium
Uso, na pasta do portfólio:
    python3 scripts/gerar-og-image.py
"""
import io, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image

raiz = Path(__file__).resolve().parent.parent
HTML = """<!doctype html><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@900&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*{margin:0;box-sizing:border-box}
body{width:1200px;height:630px;background:#000;color:#EFEFEF;padding:56px 60px 52px;display:flex;flex-direction:column;justify-content:space-between;overflow:hidden}
.mono{font-family:"JetBrains Mono",monospace;font-size:20px;letter-spacing:.04em;text-transform:uppercase;display:flex;justify-content:space-between}
.dim{color:#8E8E8E}
.dot{display:inline-block;width:11px;height:11px;border-radius:50%;background:#BA9986;margin-right:14px;vertical-align:2px}
h1{font-family:"Inter Tight",sans-serif;font-weight:900;text-transform:uppercase;letter-spacing:-.045em;line-height:.8;white-space:nowrap;font-size:100px;display:inline-block}
h1 span{color:#BA9986}
.base{border-top:1px solid rgba(239,239,239,.16);padding-top:22px}
</style>
<div class="mono"><span><i class="dot"></i>mvvisual.co</span><span class="dim">Brasília — DF</span></div>
<div><h1 id="w">MVVISUAL<span>.</span></h1></div>
<div class="mono base"><span>Vídeo · Sites · Design</span><span class="dim">Do roteiro ao site no ar</span></div>
<script>
document.fonts.ready.then(() => {
  const h = document.getElementById('w'), livre = 1200 - 120;
  h.style.fontSize = (100 * livre / h.scrollWidth) + 'px';
  document.body.dataset.pronto = '1';
});
</script>"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1200, "height": 630})
    pg.set_content(HTML, wait_until="networkidle")
    pg.wait_for_selector("body[data-pronto]", state="attached")
    caixas = pg.evaluate("""() => [...document.querySelectorAll('h1, .mono')].map(e => {
        const r = e.getBoundingClientRect(); return [e.tagName, r.left, r.right, r.top, r.bottom]; })""")
    for nome, l, r, t, bt in caixas:            # confere se nada estoura as bordas
        if l < 0 or r > 1200 or t < 0 or bt > 630:
            sys.exit(f"Texto estourando a borda: {nome} {l:.0f}-{r:.0f} x {t:.0f}-{bt:.0f}")
    png = pg.screenshot(type="png")
    b.close()

Image.open(io.BytesIO(png)).convert("RGB").save(raiz / "og-image.jpg", quality=88, optimize=True)
print("og-image.jpg gerado (1200x630).")
