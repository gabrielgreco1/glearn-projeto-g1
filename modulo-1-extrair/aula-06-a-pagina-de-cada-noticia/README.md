# Aula 6 · A página de cada notícia, poucas por vez

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pg-06-a-pagina-de-cada-noticia-poucas

O `materias.py` baixa no máximo 20 páginas de notícia por rodada e lê autor, datas e seção dos dados que a página traz para programas.

A pasta `projeto/` mostra como a sua pasta `projeto-g1/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: materias.py, testes/test_materias.py, pyproject.toml, uv.lock.

## Como rodar esta pasta

```
cd projeto
cp .env.example .env
```

Abra o `.env` e troque o contato pelo seu (um e-mail ou o endereço do seu repositório). Depois:

```
uv sync
```

Comandos da aula, nesta ordem: `uv run python baixar.py`, `uv run python acumular.py`, `uv run python materias.py`, `uv run pytest`. Cada programa lê o que o anterior gravou em `dados/`.
