# Carregar · Aula 19 · As perguntas no banco

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pgc-05-as-perguntas-no-banco

As views `noticias_fonte`, `por_dia` e `por_fonte` refazem a gold no banco, juntando as três tabelas, e a carga confere as views contra os arquivos da gold. A busca no título, com e sem índice.

A pasta `projeto/` mostra como a sua pasta `projeto-g1/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: schema.sql, carregar.py, testes/test_carregar.py.

## Como rodar esta pasta

Você precisa do Docker instalado e aberto (no Windows e no Mac, o Docker Desktop).

```
cd projeto
cp .env.example .env
```

Abra o `.env` e troque o contato pelo seu (um e-mail ou o endereço do seu repositório). Depois:

```
docker compose up -d --wait
uv sync
uv run python rodar.py
```

O `rodar.py` faz a coleta e a etapa Transformar; o `carregar.py` leva a silver ao banco.

Se o banco não estiver de pé (depois de desligar o computador, por exemplo), suba de novo com `docker compose up -d --wait`. O banco desta pasta usa a porta 5435: se outra pasta do projeto estiver com o banco ligado, desligue aquela com `docker compose down` antes.

Comandos da aula: `uv run python carregar.py`, as views no `psql` e `uv run pytest`.
