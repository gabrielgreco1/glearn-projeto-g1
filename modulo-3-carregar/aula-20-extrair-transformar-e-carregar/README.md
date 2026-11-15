# Carregar · Aula 20 · Extrair, transformar e carregar num comando

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pgc-06-extrair-transformar-e-carregar-num-comando

O `rodar.py` faz as seis etapas, da coleta à carga, e a prova numa cópia limpa mostra a carga do zero e a segunda rodada que só atualiza as notícias que ganharam página.

A pasta `projeto/` mostra como a sua pasta `projeto-g1/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: rodar.py, README.md.

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

O `rodar.py` faz a coleta, a etapa Transformar e a carga no banco.

Se o banco não estiver de pé (depois de desligar o computador, por exemplo), suba de novo com `docker compose up -d --wait`. O banco desta pasta usa a porta 5435: se outra pasta do projeto estiver com o banco ligado, desligue aquela com `docker compose down` antes.

Comandos da aula: `uv run python rodar.py` e `uv run pytest`.
