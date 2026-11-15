# Projeto G1

Objetivo: acompanhar as notícias de tecnologia do G1, montar um arquivo CSV com uma linha por notícia, sem repetir nenhuma, transformar esse arquivo numa tabela limpa que responde quem escreve o que o feed traz e guardar essa tabela num banco que outros programas leem.
Plano: o G1 publica um feed RSS da editoria, feito para programas. O programa pede o feed, guarda só o que é novo e, para o que o feed já não mostra, usa o mapa do site. A etapa Transformar lê de novo o que foi guardado, sem pedir nada ao site. A etapa Carregar leva a silver para um Postgres que roda no Docker: cada notícia uma vez, pelo link, e quem assina numa tabela só dos nomes. A etapa Orquestrar põe tudo num flow do [Prefect](https://docs.prefect.io/), que roda sozinho de 3 em 3 horas, tapa pelo mapa do site o buraco de quando ficou parado, baixa de novo a página que a redação mudou e avisa quando algo sai do normal.

## Como rodar

Você precisa do [uv](https://docs.astral.sh/uv/) e do [Docker](https://docs.docker.com/get-started/get-docker/) instalados. No Windows e no Mac, o Docker é o Docker Desktop, e ele precisa estar aberto.

```bash
cp .env.example .env        # e troque o contato dentro do G1_USER_AGENT
docker compose up -d --wait
uv sync
uv run pytest
```

Os testes não precisam do banco, do `.env` nem da pasta `dados/`: é assim que eles rodam no GitHub, a cada push (`.github/workflows/testes.yml`).

O projeto roda de três jeitos. Os dois primeiros precisam do servidor do Prefect ligado, num terminal só dele: `uv run prefect server start`. Uma vez na sua máquina: `uv run prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api` e `uv run prefect gcl create projeto-g1 --limit 1`, o limite de uma execução por vez. O painel fica em http://127.0.0.1:4200.

| Comando | O que faz |
|---|---|
| `uv run python fluxo.py agendar` | fica ligado e roda o projeto de 3 em 3 horas (0h, 3h, 6h … 21h, no horário de Brasília). Para rodar agora, noutro terminal: `uv run prefect deployment run projeto-g1/a-cada-3-horas` |
| `uv run python fluxo.py` | roda uma vez, agora, como um flow do Prefect |
| `uv run python rodar.py` | roda as seis etapas sem o Prefect, sem tentativas, sem aviso, sem vigia e sem o limite |

Cada rodada faz um pedido ao feed (quase sempre respondido com 304), baixa no máximo 20 páginas de notícia, refaz a etapa Transformar inteira e leva ao banco só o que mudou: a notícia nova entra, a que mudou é atualizada e guarda quando entrou, e a igual fica como está. Quando sobra lugar nas 20 páginas, ela também pede o mapa do site de hoje e de ontem, para achar as páginas que a redação mudou depois de baixadas.

O banco fica de pé até você desligar o computador ou rodar `docker compose stop`. Se o `rodar.py` disser que o banco não respondeu, suba de novo com `docker compose up -d --wait`: os dados ficam no volume do Docker, e a rodada seguinte carrega tudo o que faltou.

Para medir quanto tempo o feed cobre: `uv run python janela.py`. Para ver o que a vigia diria agora: `uv run python vigiar.py`. Para recuperar à mão um dia que o feed já não mostra (o `fluxo.py` faz isso sozinho quando acha um buraco):

```bash
uv run python sitemap.py 2026-11-01
```

Para refazer só a etapa Transformar, sem pedido nenhum: `uv run python transformar.py`. Só a carga: `uv run python carregar.py`.

No Windows, os comandos são os mesmos no PowerShell, e o `cp` também funciona nele. Para apagar a pasta `dados/` e começar do zero: `Remove-Item -Recurse -Force dados` (no macOS e no Linux, `rm -rf dados`). Para apagar o banco também: `docker compose down -v`. Se a saída do `psql` abrir uma tela que não volta ao terminal, aperte `q`. No Windows, se os acentos aparecerem trocados no `psql`, use o Windows Terminal.

## As etapas

| Etapa | Programa | O que faz |
|---|---|---|
| 1 | `baixar.py` | pede o feed, só se ele mudou |
| 2 | `janela.py` e `acumular.py` | guarda as notícias novas em `noticias.jsonl`; antes, se o feed já não encosta na rodada anterior, guarda as do mapa do site dos dias do buraco |
| 3 | `materias.py` | baixa a página de até 20 notícias: as que faltam e, com lugar sobrando, as que a redação mudou |
| 4 | `tabela.py` e `conferir.py` | monta e confere o `noticias.csv` |
| 5 | `transformar.py` | a silver (`silver.py`, com `texto.py`, `assinatura.py` e `repetidas.py`), as regras (`validar.py`) e a gold (`gold.py`) |
| 6 | `carregar.py` | leva a silver ao Postgres do `compose.yaml` (`banco.py` conecta e cria as tabelas do `schema.sql`) e confere a carga contra a silver e a gold |
| Orquestrar | `fluxo.py` | as seis etapas como tasks de um flow do Prefect, com novas tentativas no feed, no buraco e nas páginas, aviso de falha, uma execução por vez e o agendamento |
| Orquestrar | `vigiar.py` | depois da carga, olha no banco a notícia mais nova, as páginas sem texto e a fila de páginas, e devolve os avisos |

O `rodar.py` chama as seis etapas na ordem. O `fluxo.py` faz o mesmo, uma task por etapa, e acrescenta a vigia.

## O que sai

Tudo fica em `dados/`, que não vai para o Git:

- `bronze/feed/`, `bronze/sitemap/` e `bronze/materias/`: o que veio do G1, como veio.
- `estado.json`: o que o programa lembra de uma rodada para a outra: o `etag` do feed e o instante da notícia mais nova que ele já viu no feed.
- `noticias.jsonl` e `noticias.csv`: as notícias guardadas e a tabela da extração, com as datas como a fonte escreveu.
- `silver/noticias.parquet`: uma linha por notícia, com o dia e a hora em Brasília, as palavras do texto sem o boilerplate, quem assina, o tipo da fonte (redação, repórter, agência ou publicidade), o link da notícia repetida e os avisos.
- `silver/rejeitados.csv`: as notícias que falharam numa regra de erro, com o motivo.
- `gold/por_dia.parquet` e `gold/por_fonte.parquet`: as notícias de cada dia, quantas o g1 escreveu e quantas vieram de fora, e o tamanho do texto.

No banco, um Postgres 18 que roda no Docker na porta 5435 (o `compose.yaml`), com os dados num volume do Docker, fora da pasta:

- `noticias`: uma linha por notícia, com as colunas da silver, menos quem assina. O link é único; `carregada_em` diz quando a notícia entrou no banco, e `mudou_em`, a última vez que ela mudou.
- `autores`: uma linha por nome que assina, com o tipo da fonte.
- `assinaturas`: quem assina cada notícia, na ordem da linha "Por ...", ligando `noticias` a `autores`.
- `cargas`: uma linha por carga, com quantas notícias entraram, mudaram e ficaram iguais, e o que aconteceu com os nomes e as assinaturas.
- `noticias_fonte`, `por_dia` e `por_fonte`, três views: a fonte de cada notícia e as duas perguntas da gold, refeitas no banco.

Para consultar: `docker compose exec banco psql -U postgres`, ou qualquer programa com o endereço do `DATABASE_URL`.

Os dois arquivos que você mantém à mão: `boilerplate.txt`, com as frases que saem do texto, e `fontes.csv`, com o tipo de cada nome que não é de um repórter. Mudar o tipo de um nome no `fontes.csv` muda uma linha da tabela `autores`, e não as notícias dele.

## Regras de coleta

- Todo pedido leva um `User-Agent` com o nome do projeto e um contato de verdade.
- Um pedido de cada vez, com 2 segundos de espera depois de cada um.
- O feed é pedido com o `etag` da última vez. Se não mudou, o servidor responde 304 e nada é baixado.
- Se o site recusar um pedido (403, 429), o programa para, sem nova tentativa. Não tente contornar. Um erro do site (5xx) ou a rede fora são tentados de novo 3 vezes, com 10 segundos entre elas.
- No máximo 20 páginas de notícia por rodada, novas ou de novo; o mapa do site de hoje e de ontem só é pedido quando sobra lugar nelas.
- O texto das notícias é do G1. Ele fica só no seu computador: nem a silver nem o banco guardam o texto, só as palavras.

## A orquestração

- O feed, o buraco e as páginas são as tasks que falam com o G1, e são tentadas de novo 3 vezes, com 10 segundos entre elas, quando a rede falha ou o G1 responde um erro 5xx. Uma recusa (403, 429) para a execução sem nova tentativa. Tentar o feed de novo custa um 304: o `etag` vai junto.
- Uma execução que termina em `Failed` ou `Crashed` deixa uma linha `AVISO` em `avisos.log`. Uma que termina bem, mas com algo estranho no banco, deixa uma linha `ATENÇÃO`. O `runbook.md` diz o que fazer com cada uma.
- O feed mostra as últimas 100 notícias. O programa anota, em `dados/estado.json`, a notícia mais nova que ele já viu no feed. Se a mais antiga do feed de agora é mais nova que ela, há um buraco: as notícias do meio podem ter saído do feed sem passar pelo programa, e ele vai ao mapa do site de cada dia do buraco. O mapa de um dia que já acabou não é pedido de novo.
- Uma página que a redação mudou depois de baixada é baixada de novo: o `lastmod` do mapa do site de hoje e de ontem é mais novo que o `dateModified` da página guardada. A página nova é gravada com outro nome e trocada de uma vez; a carga atualiza a notícia, e `mudou_em` anda.
- Uma execução por vez, pelo limite `projeto-g1` do Prefect. A segunda espera a primeira terminar, até 15 minutos. Se o servidor do Prefect cair no meio de uma rodada, a vaga fica presa: o `runbook.md` diz como soltar.
- A carga continua sendo uma transação conferida contra a silver e a gold: o que não fecha não é publicado.

## O que a etapa Orquestrar mostrou, em 15 de novembro de 2026

- O feed de tecnologia tinha 100 notícias, de 04/11 10h33 a 15/11 9h06: uma janela de 10 dias e 22 horas, 9,1 notícias por dia, e o maior intervalo sem notícia nova foi de 18 h 39 min. O G1 guarda a cópia do feed por 10 minutos (`max-age=600`).
- O feed escreve as datas com `-0000`, e o Python lê essas datas sem fuso. Sem pôr o UTC, a primeira medida da janela saiu três horas fora.
- Um buraco de propósito (a última notícia vista em 27/10) levou a rodada aos mapas de 27/10 a 04/11: 5 dias pedidos ao G1, 4 já no disco, 28 notícias recuperadas, 20 páginas baixadas na rodada e 8 na seguinte.
- De 141 páginas, 59 mudaram mais de 1 hora depois de publicadas e 36 mais de 3 horas depois; a mediana foi de 31 minutos e a maior, de 21 h 29 min. O `lastmod` do mapa do site e o `dateModified` da página dão o mesmo instante, com milésimos diferentes.
- O feed de tecnologia traz notícias de outras editorias (inovação, mundo, trabalho e carreira). Por isso as mudanças são procuradas em todos os endereços do mapa, e não só nos da editoria.
- Com as páginas de hoje e de ontem trocadas por uma sem texto, a carga mudou 12 notícias, nada falhou, e só a vigia avisou: 10 das 10 páginas mais novas sem texto ou sem assinatura. Apagadas, as 12 foram baixadas de novo na rodada seguinte.
- Duas rodadas ao mesmo tempo, sem o limite, baixaram as mesmas 12 páginas, 24 pedidos para 12 páginas. Com o limite, a segunda esperou 55 segundos e não baixou nenhuma.

## O que o projeto não faz

- Uma página que a redação muda é baixada de novo só se a mudança aparece no mapa do site de hoje ou de ontem. Uma correção feita três dias depois não chega ao banco. A página guardada é sempre a última versão baixada: a anterior não fica.
- A notícia do mapa do site sem página só tem o dia, sem a hora (`precisao` = `dia`), e fica sem título e sem assinatura. Tudo isso chega quando o `materias.py` baixa a página, numa das rodadas seguintes, e a carga atualiza a notícia.
- O banco segue a silver: uma notícia que sai da silver (porque passou a falhar numa regra de erro) sai também do banco, com as assinaturas, e a tabela `cargas` conta quantas saíram. Por isso, apagar a pasta `dados/` e rodar de novo deixa no banco só as notícias que a silver nova tem.
- Um nome que deixou de assinar fica na tabela `autores`, sem assinatura nenhuma.
- Um nome que não está no `fontes.csv` conta como repórter. Uma agência nova, ou um jornalista de um veículo parceiro, aparece como repórter até você acrescentar uma linha.
- Uma frase repetida nova só sai do texto quando você a põe no `boilerplate.txt`. O `uv run python texto.py` mostra as candidatas.
- A notícia repetida é achada pelo texto quase igual (nota 90 ou mais), em até 3 dias. Os pares entre 80 e 90 ficam para você ler: `uv run python silver.py` mostra.
- O agendamento roda enquanto o `fluxo.py agendar` e o servidor do Prefect estão ligados, na sua máquina. Com o computador desligado, nada roda; na volta, a primeira rodada tapa o buraco pelo mapa do site.
- O banco é de treino: a senha do `.env` é simples, e o Docker abre a porta 5435 também para a sua rede local. Não guarde nele nada que precise de proteção.
