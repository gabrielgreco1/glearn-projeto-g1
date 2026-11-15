# Transformar · Aula 11 · Quem assina a notícia

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pgt-04-quem-assina-a-noticia

O `assinatura.py` lê a linha "Por ..." de cada página guardada, e o `fontes.csv` diz se o nome é da redação, de uma agência ou de publicidade.

A pasta `projeto/` mostra como a sua pasta `projeto-g1/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: assinatura.py, fontes.csv, silver.py, testes/test_assinatura.py.

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

Comandos da aula, nesta ordem: `uv run python assinatura.py`, `uv run python silver.py`, `uv run pytest`.
