# Aula 5 · O que o feed já não mostra

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pg-05-o-que-o-feed-ja-nao

O `sitemap.py` recupera as notícias de tecnologia de um dia que o feed já não mostra, pelo mapa do site daquele dia.

A pasta `projeto/` mostra como a sua pasta `projeto-g1/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: sitemap.py.

## Como rodar esta pasta

```
cd projeto
cp .env.example .env
```

Abra o `.env` e troque o contato pelo seu (um e-mail ou o endereço do seu repositório). Depois:

```
uv sync
```

Comandos da aula, nesta ordem: `uv run python baixar.py`, `uv run python acumular.py`, `uv run python sitemap.py 2026-11-01`, `uv run pytest`. Cada programa lê o que o anterior gravou em `dados/`.
