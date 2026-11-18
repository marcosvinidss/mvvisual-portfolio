# Vídeos próprios

Vídeos que tocam sozinhos (sem som, em loop) no lugar do embed do Instagram.

- **Cases:** `videos/<arquivo>.mp4`, onde `<arquivo>` é o campo `arquivo` do projeto em `PROJETOS`.
  Ativar: acrescente `video: true` no projeto (e `capa: true` se também tiver a capa, que vira o poster).
- **Fundo da capa do site:** `videos/capa.mp4`.
  Ativar: no `index.html`, troque `const USAR_VIDEO_CAPA = false;` para `true`.
- **Formato recomendado:** MP4 H.264, **sem áudio**, 720p, até ~3 MB cada (10–20 segundos).
  O GitHub recusa arquivos acima de 100 MB, e vídeo pesado deixa o site lento no celular.

Dica: coloque o vídeo bruto em `midia-bruta/<arquivo>.mp4` e rode `scripts/preparar-midia.sh`,
que comprime o vídeo para cá e tira a capa para `capas/`.
