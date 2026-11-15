# Orquestrar · Aula 26 · Os testes no GitHub e a prova final

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pgo-06-os-testes-no-github-e-a

Os testes rodam no GitHub a cada push, sem o .env e sem dados/. A prova final é numa cópia limpa, com um Ctrl+C no meio das páginas e uma execução pedida ao agendamento.

A pasta `projeto/` mostra como a sua pasta `projeto-g1/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: .github/workflows/testes.yml, baixar.py, testes/test_baixar.py, README.md.

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

Num terminal só dele, deixe o servidor do Prefect ligado: `uv run prefect server start`. Uma vez na sua máquina: `uv run prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api`. A partir desta aula, também uma vez: `uv run prefect gcl create projeto-g1 --limit 1`. O painel fica em http://127.0.0.1:4200.

O banco desta pasta usa a porta 5435: se outra pasta do projeto estiver com o banco ligado, desligue aquela com `docker compose down` antes. Esta pasta começa sem `dados/`: a primeira rodada pede o feed e baixa 20 páginas. No Windows, os comandos são os mesmos no PowerShell.

Comandos da aula: `uv run pytest` (sem o `.env`), `git push`, e a prova numa cópia limpa com `uv run python fluxo.py`.
