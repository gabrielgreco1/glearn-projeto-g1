# Transformar · Aula 13 · O que barra e o que só avisa

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pgt-06-o-que-barra-e-o-que

O `validar.py` confere a silver contra quatro regras de erro e quatro avisos, grava a silver em Parquet e os rejeitados com o motivo.

A pasta `projeto/` mostra como a sua pasta `projeto-g1/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: validar.py, testes/test_validar.py.

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

Comandos da aula, nesta ordem: `uv run python validar.py`, `uv run pytest`.
