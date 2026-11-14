# Aula 2 · Pedir o feed, e só quando ele mudou

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pg-02-pedir-o-feed-e-so-quando

O `baixar.py` pede o feed de Tecnologia, guarda a resposta como veio em `dados/bronze/feed/`, com a data da coleta no caminho, e guarda o `ETag`. Na segunda rodada o G1 responde 304 e nada é baixado.

A pasta `projeto/` mostra como a sua pasta `projeto-g1/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: baixar.py, pyproject.toml, uv.lock, .python-version, .env.example, .gitignore.

## Como rodar esta pasta

```
cd projeto
cp .env.example .env
```

Abra o `.env` e troque o contato pelo seu (um e-mail ou o endereço do seu repositório). Depois:

```
uv sync
```

Comandos da aula, nesta ordem: `uv run python baixar.py`, `uv run python baixar.py`. Cada programa lê o que o anterior gravou em `dados/`.
