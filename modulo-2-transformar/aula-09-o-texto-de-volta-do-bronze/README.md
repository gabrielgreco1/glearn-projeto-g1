# Transformar · Aula 9 · O texto de volta do bronze

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pgt-02-o-texto-de-volta-do-bronze

O `texto.py` lê de novo cada página guardada e fica só com os parágrafos do texto; a silver conta as palavras de novo, sem legenda, vídeo nem anúncio.

A pasta `projeto/` mostra como a sua pasta `projeto-g1/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: texto.py, silver.py, testes/test_texto.py, testes/amostra_materia.html.

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
