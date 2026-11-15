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
2. **`Failed` em `feed`, `guardar` ou `paginas`, depois das tentativas.** É a internet ou o G1 fora do ar (um 5xx). A `guardar` só pede algo ao G1 quando acha um buraco: aí ela pede o mapa do site dos dias dele. A `paginas` pede as páginas e, quando sobra lugar no limite de 20, o mapa do site de hoje e de ontem, para achar as que mudaram. Abra https://g1.globo.com no navegador. Quando ele responder, rode de novo: o feed é pedido com o etag, o mapa de um dia que já acabou não é pedido outra vez, e uma página já baixada também não.
3. **`Failed` em `guardar`, com `o feed veio quebrado`.** O G1 mandou um feed que o feedparser não leu. O arquivo está em `dados/bronze/feed/`: abra o mais novo e veja se é XML.
4. **`Failed` em `carregar`, com `a carga não fecha` ou `não bate com`.** O banco não ficou igual à silver ou à gold, e a carga foi desfeita: nada foi publicado. Rode `uv run python transformar.py` e depois `uv run python carregar.py`, e leia a mensagem de novo.
5. **`Crashed` com `interrupt signal`.** Alguém apertou Ctrl+C ou a máquina desligou no meio. Rode de novo.

## Linhas de ATENÇÃO

A execução terminou em `Completed` e as notícias foram publicadas, mas a vigia (`vigiar.py`) viu algo fora do normal no banco. Nada parou; a linha diz o que olhar.

1. **A notícia mais nova saiu há mais de 24 horas.** O maior silêncio medido no feed foi de 18 h 39 min. Abra o feed no navegador: se o primeiro item é novo e o projeto não o guardou, olhe o log da task `feed` (o etag, o 304); se o feed também está parado, o G1 mudou o endereço do feed ou deixou de atualizá-lo.
2. **Metade das páginas mais novas veio sem texto ou sem assinatura.** O G1 pode ter mudado a página. Abra uma delas no navegador, veja o código (Ctrl+U) e procure o `itemprop="articleBody"` e a linha "Por ...". Se mudou, o seletor do `texto.py` ou do `assinatura.py` precisa acompanhar; depois de mudar, apague as páginas dessas notícias em `dados/bronze/materias/` e rode de novo.
3. **Muitas notícias esperam a página.** Depois de um buraco, é normal: 20 por rodada, e a fila desce sozinha. Se ela não desce de uma rodada para a outra, olhe o log da task `paginas`.

Para rodar de novo, com o agendamento ligado (`uv run python fluxo.py agendar`, num terminal que fica aberto): `uv run prefect deployment run projeto-g1/a-cada-3-horas`. Sem ele: `uv run python fluxo.py`.
