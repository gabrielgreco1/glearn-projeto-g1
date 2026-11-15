# Transformar · Aula 10 · O que se repete em toda página

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pgt-03-o-que-se-repete-em-toda

O `texto.py` lista as frases que aparecem em muitas páginas; o `boilerplate.txt` guarda as que você decidiu tirar, e a silver conta as palavras sem elas.

A pasta `projeto/` mostra como a sua pasta `projeto-g1/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: texto.py, boilerplate.txt, silver.py, testes/test_texto.py.

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

Comandos da aula, nesta ordem: `uv run python texto.py`, `uv run python silver.py`, `uv run pytest`.
