# Transformar · Aula 8 · Três jeitos de dizer quando

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pgt-01-tres-jeitos-de-dizer-quando

O `silver.py` junta as datas do feed (UTC), da página (com o fuso) e do mapa do site (só o dia) num instante no horário de Brasília, com a precisão de cada notícia.

A pasta `projeto/` mostra como a sua pasta `projeto-g1/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: silver.py, pyproject.toml, uv.lock, testes/test_silver.py, testes/amostra_noticias.csv.

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
