# Runbook: o projeto G1 não carregou

O que fazer quando chega um aviso. Siga as checagens na ordem: a primeira que explicar o aviso é a causa.

## Sintoma

Uma linha nova em `avisos.log`, com a execução terminada em `Failed` ou `Crashed`. No painel do Prefect (http://127.0.0.1:4200), a mesma execução aparece em vermelho ou laranja, com o log de cada task.

## Impacto

O banco continua com a última carga que deu certo, inteira: a carga é uma transação, e a que falha não grava nada. Quem lê o banco vê as notícias até a rodada anterior. Nada se perde enquanto o feed ainda mostra as notícias que faltam: elas entram na rodada seguinte que der certo.

## Checagens, nesta ordem

1. **`Crashed` com `Python system exit call`.** O programa parou de propósito. A mensagem do que fazer sai no fim do terminal onde o projeto rodou, depois do aviso, e não vai para o painel.
   - "respondeu 403" ou "respondeu 429": o G1 recusou. Não rode de novo agora. Confira o contato no `G1_USER_AGENT` do `.env` e espere até o dia seguinte; se a recusa continuar, pare o projeto.
   - "O banco não respondeu": suba o banco com `docker compose up -d --wait`.
   - "Falta ... no arquivo .env": copie a linha do `.env.example` para o `.env`.
   - "A conferência achou problema": a linha de conferência, no log da task `tabela_e_conferencia`, diz quantas notícias repetidas ou sem data o `noticias.csv` tem. Rodar de novo dá o mesmo resultado: procure as linhas repetidas em `dados/noticias.jsonl`.
2. **`Failed` em `feed` ou em `paginas`, depois das tentativas.** É a internet ou o G1 fora do ar (um 5xx). Abra https://g1.globo.com no navegador. Quando ele responder, rode de novo: o feed é pedido com o etag, e uma página já baixada não é pedida outra vez.
3. **`Failed` em `guardar`, com `o feed veio quebrado`.** O G1 mandou um feed que o feedparser não leu. O arquivo está em `dados/bronze/feed/`: abra o mais novo e veja se é XML.
4. **`Failed` em `carregar`, com `a carga não fecha` ou `não bate com`.** O banco não ficou igual à silver ou à gold, e a carga foi desfeita: nada foi publicado. Rode `uv run python transformar.py` e depois `uv run python carregar.py`, e leia a mensagem de novo.
5. **`Crashed` com `interrupt signal`.** Alguém apertou Ctrl+C ou a máquina desligou no meio. Rode de novo.

Para rodar de novo: `uv run python fluxo.py`.
