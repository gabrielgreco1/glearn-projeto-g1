# Transformar · Aula 12 · A mesma notícia duas vezes

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pgt-05-a-mesma-noticia-duas-vezes

O `repetidas.py` compara o texto das notícias publicadas com até 3 dias de distância e marca a mais nova de cada par quase igual com o link da mais antiga.

A pasta `projeto/` mostra como a sua pasta `projeto-g1/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: repetidas.py, silver.py, pyproject.toml, uv.lock, testes/test_repetidas.py.

## Como rodar esta pasta

```
cd projeto
cp .env.example .env
```

Abra o `.env` e troque o contato pelo seu (um e-mail ou o endereço do seu repositório). Depois:

```
uv sync
uv run python rodar.py
```

O `rodar.py` faz a rodada da extração e cria a pasta `dados/` com o feed, as páginas de até 20 notícias e o `noticias.csv`. A etapa Transformar só lê o que está em `dados/`; rode o `rodar.py` mais vezes para ter mais páginas.

Comandos da aula, nesta ordem: `uv run python silver.py`, `uv run pytest`.
