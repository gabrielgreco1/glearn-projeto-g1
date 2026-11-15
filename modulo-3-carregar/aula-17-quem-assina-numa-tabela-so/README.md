# Carregar · Aula 17 · Quem assina, numa tabela só

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pgc-03-quem-assina-numa-tabela-so

Os nomes que assinam vão para a tabela `autores`, uma vez cada, com o tipo da fonte, e a tabela `assinaturas` liga cada notícia aos nomes, com duas chaves estrangeiras.

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

Comandos da aula: `uv run python carregar.py`, as consultas no `psql` e `uv run pytest`.
