# Carregar · Aula 16 · Cada notícia uma vez, pelo link

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pgc-02-cada-noticia-uma-vez-pelo-link

O `carregar.py` leva a silver ao banco com COPY e um upsert pelo link: a notícia nova entra, a que mudou é atualizada sem perder quando entrou, e a que saiu da silver sai do banco.

A pasta `projeto/` mostra como a sua pasta `projeto-g1/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: carregar.py, testes/test_carregar.py.

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

Comandos da aula: `uv run python carregar.py` (duas vezes) e `uv run pytest`.
