# Orquestrar · Aula 23 · A página que a redação mudou

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pgo-03-a-pagina-que-a-redacao-mudou

O mapa do site de hoje e de ontem diz quando cada notícia mudou pela última vez. A página que a redação mudou depois de baixada é baixada de novo, sem passar do limite de 20 por rodada, e a carga atualiza a notícia no banco.

A pasta `projeto/` mostra como a sua pasta `projeto-g1/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: materias.py, testes/test_materias.py, runbook.md.

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

Comandos da aula: `uv run python fluxo.py` e `uv run pytest`.
