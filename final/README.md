# Projeto G1

Objetivo: acompanhar as notícias de tecnologia do G1 e montar um arquivo CSV com uma linha por notícia, sem repetir nenhuma.
Plano: o G1 publica um feed RSS da editoria, feito para programas. O programa pede o feed, guarda só o que é novo e, para o que o feed já não mostra, usa o mapa do site.

## Como rodar

```bash
cp .env.example .env        # e troque o contato dentro do G1_USER_AGENT
uv sync
uv run python rodar.py
uv run pytest
```

Rode de novo quando quiser. Cada rodada faz um pedido ao feed e baixa, no máximo, 20 páginas de notícia.

Para recuperar um dia que o feed já não mostra:

```bash
uv run python sitemap.py 2026-11-01
```

## O que sai

Tudo fica em `dados/`, que não vai para o Git:

- `bronze/feed/AAAA-MM-DD/HH-MM-SS.xml`: cada feed baixado, como veio, numa pasta com a data da coleta.
- `bronze/sitemap/`: o mapa do site de cada dia recuperado.
- `bronze/materias/`: a página de cada notícia, com o nome tirado do endereço.
- `estado.json`: o que o programa lembra de uma rodada para a outra.
- `noticias.jsonl`: uma notícia por linha, na ordem em que entraram.
- `noticias.csv`: a tabela final, uma linha por notícia. As datas ficam como vieram da fonte; converter é trabalho da etapa Transformar.

## Regras de coleta

- Todo pedido leva um `User-Agent` com o nome do projeto e um contato de verdade.
- Um pedido de cada vez, com 2 segundos de espera depois de cada um.
- O feed é pedido com o `etag` da última vez. Se não mudou, o servidor responde 304 e nada é baixado.
- Se o site recusar um pedido, o programa para. Não tente contornar.
- O texto das notícias é do G1. Ele fica só no seu computador.
