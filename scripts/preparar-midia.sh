#!/bin/bash
# Prepara vídeos e capas para o site.
#
# Uso:
#   1. Coloque os vídeos brutos em midia-bruta/<arquivo>.mp4 (ou .mov)
#      <arquivo> = o campo "arquivo" do projeto em PROJETOS (ex.: termobolic). Para o fundo da capa, use "capa".
#   2. Rode, na pasta do portfólio:   bash scripts/preparar-midia.sh
#   3. Marque no index.html:  video: true  e  capa: true  nos projetos (ou USAR_VIDEO_CAPA = true)
#
# Gera:
#   videos/<arquivo>.mp4  — H.264, sem áudio, 720p, faststart (~3 MB para 15–20 s)
#   capas/<arquivo>.jpg   — frame do segundo 1, 800px de largura, qualidade ~75
#
# Precisa do ffmpeg:  https://ffmpeg.org/download.html  (no Mac: brew install ffmpeg)

set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ffmpeg não encontrado. Instale com: brew install ffmpeg  (ou baixe em https://ffmpeg.org/download.html)"
  exit 1
fi

mkdir -p videos capas
shopt -s nullglob nocaseglob
arquivos=(midia-bruta/*.mp4 midia-bruta/*.mov)
if [ ${#arquivos[@]} -eq 0 ]; then
  echo "Nenhum vídeo em midia-bruta/. Coloque os arquivos lá (ex.: midia-bruta/termobolic.mp4)."
  exit 0
fi

for entrada in "${arquivos[@]}"; do
  nome="$(basename "${entrada%.*}")"
  echo "→ $nome"
  # Vídeo: 720p no lado menor, sem áudio, qualidade CRF 28, limite de taxa para ficar leve
  ffmpeg -hide_banner -loglevel error -y -i "$entrada" \
    -an -vf "scale='if(gt(iw,ih),-2,720)':'if(gt(iw,ih),720,-2)',fps=30" \
    -c:v libx264 -profile:v high -pix_fmt yuv420p -preset slow -crf 28 \
    -maxrate 1500k -bufsize 3000k -movflags +faststart \
    "videos/$nome.mp4"
  # Capa: frame do segundo 1, 800px de largura, qualidade ~75
  ffmpeg -hide_banner -loglevel error -y -ss 1 -i "$entrada" -frames:v 1 \
    -vf "scale=800:-2" -q:v 5 "capas/$nome.jpg"
  echo "   videos/$nome.mp4  $(du -h "videos/$nome.mp4" | cut -f1)   capas/$nome.jpg  $(du -h "capas/$nome.jpg" | cut -f1)"
done

echo "Pronto. Agora marque video: true / capa: true nos projetos do index.html."
