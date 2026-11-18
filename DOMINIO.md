# Ligar um domínio próprio (ex.: mvvisual.co ou mvvisual.com.br)

Hoje o site está em `https://marcosvinidss.github.io/mvvisual-portfolio/`.
Siga os passos abaixo **na ordem**. Não crie o arquivo `CNAME` antes de comprar o domínio.

## 1. Comprar o domínio
- `.com.br`: [registro.br](https://registro.br) (precisa de CPF ou CNPJ).
- `.co`, `.com`: Cloudflare Registrar, Namecheap, Porkbun etc.

## 2. Avisar o GitHub
1. No GitHub, abra o repositório **mvvisual-portfolio** → **Settings** → **Pages**.
2. Em **Custom domain**, digite o domínio (ex.: `mvvisual.com.br`) e clique em **Save**.
   O GitHub cria sozinho um arquivo `CNAME` no repositório com esse nome.
   (Se preferir fazer à mão: crie um arquivo chamado `CNAME`, sem extensão, só com `mvvisual.com.br` dentro.)

## 3. Configurar o DNS (no site onde comprou o domínio)
Para o domínio "raiz" (`mvvisual.com.br`), crie **4 registros A**:

| Tipo | Nome | Valor |
|------|------|-------|
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |

Opcional, para IPv6, crie 4 registros **AAAA**: `2606:50c0:8000::153`, `2606:50c0:8001::153`, `2606:50c0:8002::153`, `2606:50c0:8003::153`.

Para o `www` funcionar também, crie **1 registro CNAME**:

| Tipo | Nome | Valor |
|------|------|-------|
| CNAME | www | marcosvinidss.github.io |

> Se o DNS estiver na Cloudflare, deixe a nuvem **cinza** (DNS only) até o HTTPS do GitHub ficar ativo.

O DNS leva de alguns minutos a 24 horas para propagar. Dá para conferir em [dnschecker.org](https://dnschecker.org).

## 4. Ligar o HTTPS
De volta em **Settings → Pages**, quando aparecer "DNS check successful", marque **Enforce HTTPS**.
(Pode levar até 1 hora para o certificado ficar pronto.)

## 5. Atualizar o endereço no site
1. No `index.html`, no bloco "EDITE AQUI", troque:
   ```js
   const SITE_URL = "https://marcosvinidss.github.io/mvvisual-portfolio/";
   ```
   por (com a barra no final):
   ```js
   const SITE_URL = "https://mvvisual.com.br/";
   ```
2. Rode, na pasta do portfólio:
   ```bash
   python3 scripts/gerar-estatico.py
   ```
   Isso atualiza o canonical, as tags de prévia de link (og:url, og:image) e os dados do Google.
3. Faça commit e push.

## 6. Atualizar a prévia no WhatsApp e no Instagram
Os apps guardam a prévia antiga por um tempo. Para forçar a nova:
- Facebook/Instagram/WhatsApp: [developers.facebook.com/tools/debug](https://developers.facebook.com/tools/debug) → cole o endereço → **Scrape Again**.
- No WhatsApp, a prévia nova aparece em conversas novas (as antigas continuam com a imagem antiga).

## 7. Analytics
Se já usa o Cloudflare Web Analytics, adicione o domínio novo no painel da Cloudflare (o token continua o mesmo).
