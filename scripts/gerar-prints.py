"""Tira prints dos sites da seção "Sites com IA" e salva em sites/<print>.jpg.

Lê os sites direto do index.html (bloco SITES_IA), então os dados ficam num lugar só.
Precisa de Playwright e Pillow (só no seu computador, não no site):
    python3 -m pip install playwright pillow
    python3 -m playwright install chromium
Uso, na pasta do portfólio:
    python3 scripts/gerar-prints.py
"""
import io, re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image

raiz = Path(__file__).resolve().parent.parent
html = (raiz / "index.html").read_text(encoding="utf-8")
bloco = re.search(r"const SITES_IA = \[(.*?)\n  \];", html, re.S).group(1)
sites = re.findall(r'print:\s*"([^"]+)".*?link:\s*"([^"]*)"', bloco, re.S)
if not sites:
    sys.exit("Nenhum site com print/link encontrado em SITES_IA.")

(raiz / "sites").mkdir(exist_ok=True)
with sync_playwright() as p:
    nav = p.chromium.launch()
    pag = nav.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
    for nome, link in sites:
        if not link:
            continue
        print(f"→ {nome}: {link}")
        pag.goto(link, wait_until="networkidle", timeout=60000)
        pag.wait_for_timeout(1500)  # deixa animações de entrada terminarem
        png = pag.screenshot(type="png")
        img = Image.open(io.BytesIO(png)).convert("RGB").resize((1200, 750), Image.LANCZOS)
        destino = raiz / "sites" / f"{nome}.jpg"
        img.save(destino, "JPEG", quality=75, optimize=True, progressive=True)
        print(f"   {destino.relative_to(raiz)}  {destino.stat().st_size // 1024} KB")
    nav.close()
