# Orquestrar · Aula 22 · A janela do feed e a hora de rodar

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pgo-02-a-janela-do-feed-e-a

O janela.py mede quanto tempo o feed cobre e, quando o feed de agora já não encosta no da rodada anterior, tapa o buraco pelo mapa do site. O fluxo.py agendar roda o projeto de 3 em 3 horas, no horário de Brasília.

A pasta `projeto/` mostra como a sua pasta `projeto-g1/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: janela.py, testes/test_janela.py, fluxo.py, rodar.py, runbook.md.

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
```

Num terminal só dele, deixe o servidor do Prefect ligado: `uv run prefect server start`. Uma vez na sua máquina: `uv run prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api`. O painel fica em http://127.0.0.1:4200.

O banco desta pasta usa a porta 5435: se outra pasta do projeto estiver com o banco ligado, desligue aquela com `docker compose down` antes. Esta pasta começa sem `dados/`: a primeira rodada pede o feed e baixa 20 páginas. No Windows, os comandos são os mesmos no PowerShell.

Comandos da aula: `uv run python janela.py`, `uv run python fluxo.py` (com um buraco de propósito no `dados/estado.json`), `uv run python fluxo.py agendar` e `uv run prefect deployment run projeto-g1/a-cada-3-horas`.
