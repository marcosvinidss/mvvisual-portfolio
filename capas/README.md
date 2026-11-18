# Capas (miniaturas dos cases)

Imagem que aparece no card de cada case, no lugar da capa do Instagram.

- **Nome:** `capas/<arquivo>.jpg`, onde `<arquivo>` é o campo `arquivo` do projeto em `PROJETOS` (no `index.html`, bloco "EDITE AQUI").
  Exemplo: `capas/termobolic.jpg`.
- **Tamanho:** JPG com 800px de largura, qualidade ~75 (fica com ~80–150 KB).
  Vertical em 4:5 (800×1000) para reels; horizontal em 16:9 (800×450) para vídeos deitados.
- **Ativar:** no projeto, acrescente `capa: true`.
  Exemplo: `{ arquivo: "termobolic", capa: true, titulo: "Lançamento Termobolic", ... }`

Dica: o script `scripts/preparar-midia.sh` gera a capa automaticamente a partir do vídeo bruto.
