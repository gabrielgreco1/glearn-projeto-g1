# Aula 7 · Fechar o projeto: uma rodada, um comando

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pg-07-fechar-o-projeto-uma-rodada-um

O `rodar.py` faz a rodada inteira, o `tabela.py` monta o CSV e o `conferir.py` confere. O README explica o projeto.

A pasta `projeto/` mostra como a sua pasta `projeto-g1/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: tabela.py, conferir.py, rodar.py, README.md.

## Como rodar esta pasta

```
cd projeto
cp .env.example .env
```

Abra o `.env` e troque o contato pelo seu (um e-mail ou o endereço do seu repositório). Depois:

```
uv sync
```

Comandos da aula, nesta ordem: `uv run python rodar.py`, `uv run python rodar.py`, `uv run pytest`. Cada programa lê o que o anterior gravou em `dados/`.
