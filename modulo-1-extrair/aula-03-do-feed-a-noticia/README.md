# Aula 3 · Do feed à notícia

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pg-03-do-feed-a-noticia

O `ler.py` lê o feed com o feedparser e transforma cada item num dicionário, com a data como veio.

A pasta `projeto/` mostra como a sua pasta `projeto-g1/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: ler.py, testes/test_ler.py, testes/amostra_feed.xml, pyproject.toml, uv.lock.

## Como rodar esta pasta

```
cd projeto
cp .env.example .env
```

Abra o `.env` e troque o contato pelo seu (um e-mail ou o endereço do seu repositório). Depois:

```
uv sync
```

Comandos da aula, nesta ordem: `uv run python baixar.py`, `uv run python ler.py`, `uv run pytest`. Cada programa lê o que o anterior gravou em `dados/`.
