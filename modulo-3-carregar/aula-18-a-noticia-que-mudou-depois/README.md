# Carregar · Aula 18 · A notícia que mudou depois

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pgc-04-a-noticia-que-mudou-depois

A notícia do mapa do site ganha a página numa rodada seguinte: a carga atualiza a notícia, guarda quando ela entrou e quando mudou, confere o banco contra a silver e registra a carga na tabela `cargas`.

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

Comandos da aula: `uv run python materias.py`, `uv run python tabela.py`, `uv run python transformar.py`, `uv run python carregar.py` e `uv run pytest`.
