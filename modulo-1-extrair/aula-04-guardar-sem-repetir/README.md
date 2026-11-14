# Aula 4 · Guardar sem repetir

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pg-04-guardar-sem-repetir

O `acumular.py` acrescenta ao `dados/noticias.jsonl` só as notícias cujo `guid` ainda não está lá.

A pasta `projeto/` mostra como a sua pasta `projeto-g1/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: acumular.py.

## Como rodar esta pasta

```
cd projeto
cp .env.example .env
```

Abra o `.env` e troque o contato pelo seu (um e-mail ou o endereço do seu repositório). Depois:

```
uv sync
```

Comandos da aula, nesta ordem: `uv run python baixar.py`, `uv run python acumular.py`, `uv run python acumular.py`, `uv run pytest`. Cada programa lê o que o anterior gravou em `dados/`.
