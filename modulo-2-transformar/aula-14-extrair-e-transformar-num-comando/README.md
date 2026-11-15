# Transformar · Aula 14 · Extrair e transformar num comando só

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pgt-07-extrair-e-transformar-num-comando-so

O `gold.py` responde em SQL quantas notícias o g1 escreveu e quantas vieram de fora; o `transformar.py` roda a etapa inteira, e o `rodar.py` faz extrair e transformar com um comando.

A pasta `projeto/` mostra como a sua pasta `projeto-g1/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: gold.py, transformar.py, rodar.py, README.md, pyproject.toml, uv.lock, testes/test_gold.py.

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

O `rodar.py` faz a coleta e a etapa Transformar inteira. Numa pasta nova, só as 20 primeiras notícias têm página; cada rodada baixa mais 20.

Comandos da aula, nesta ordem: `uv run python rodar.py`, `uv run pytest`.
