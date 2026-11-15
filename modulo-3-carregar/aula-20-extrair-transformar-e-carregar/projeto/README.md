# Projeto G1

Objetivo: acompanhar as notícias de tecnologia do G1, montar um arquivo CSV com uma linha por notícia, sem repetir nenhuma, transformar esse arquivo numa tabela limpa que responde quem escreve o que o feed traz e guardar essa tabela num banco que outros programas leem.
Plano: o G1 publica um feed RSS da editoria, feito para programas. O programa pede o feed, guarda só o que é novo e, para o que o feed já não mostra, usa o mapa do site. A etapa Transformar lê de novo o que foi guardado, sem pedir nada ao site. A etapa Carregar leva a silver para um Postgres que roda no Docker: cada notícia uma vez, pelo link, e quem assina numa tabela só dos nomes.

## Como rodar

Você precisa do [uv](https://docs.astral.sh/uv/) e do [Docker](https://docs.docker.com/get-started/get-docker/) instalados. No Windows e no Mac, o Docker é o Docker Desktop, e ele precisa estar aberto.

```bash
cp .env.example .env        # e troque o contato dentro do G1_USER_AGENT
docker compose up -d --wait
uv sync
uv run python rodar.py
uv run pytest
```

Rode de novo quando quiser. Cada rodada faz um pedido ao feed, baixa, no máximo, 20 páginas de notícia, refaz a etapa Transformar inteira e leva ao banco só o que mudou: a notícia nova entra, a que mudou é atualizada e guarda quando entrou, e a igual fica como está.

O banco fica de pé até você desligar o computador ou rodar `docker compose stop`. Se o `rodar.py` disser que o banco não respondeu, suba de novo com `docker compose up -d --wait`: os dados ficam no volume do Docker, e a rodada seguinte carrega tudo o que faltou.

Para recuperar um dia que o feed já não mostra:

```bash
uv run python sitemap.py 2026-11-01
```

Para refazer só a etapa Transformar, sem pedido nenhum: `uv run python transformar.py`. Só a carga: `uv run python carregar.py`.

No Windows, os comandos são os mesmos no PowerShell, e o `cp` também funciona nele. Para apagar a pasta `dados/` e começar do zero: `Remove-Item -Recurse -Force dados` (no macOS e no Linux, `rm -rf dados`). Para apagar o banco também: `docker compose down -v`. Se a saída do `psql` abrir uma tela que não volta ao terminal, aperte `q`. No Windows, se os acentos aparecerem trocados no `psql`, use o Windows Terminal.

## As etapas

| Etapa | Programa | O que faz |
|---|---|---|
| 1 | `baixar.py` | pede o feed, só se ele mudou |
| 2 | `acumular.py` | guarda as notícias novas em `noticias.jsonl` |
| 3 | `materias.py` | baixa a página de até 20 notícias |
| 4 | `tabela.py` e `conferir.py` | monta e confere o `noticias.csv` |
| 5 | `transformar.py` | a silver (`silver.py`, com `texto.py`, `assinatura.py` e `repetidas.py`), as regras (`validar.py`) e a gold (`gold.py`) |
| 6 | `carregar.py` | leva a silver ao Postgres do `compose.yaml` (`banco.py` conecta e cria as tabelas do `schema.sql`) e confere a carga contra a silver e a gold |

## O que sai

Tudo fica em `dados/`, que não vai para o Git:

- `bronze/feed/`, `bronze/sitemap/` e `bronze/materias/`: o que veio do G1, como veio.
- `estado.json`: o que o programa lembra de uma rodada para a outra.
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
- Se o site recusar um pedido, o programa para. Não tente contornar.
- O texto das notícias é do G1. Ele fica só no seu computador: nem a silver nem o banco guardam o texto, só as palavras.

## O que o projeto não faz

- Uma notícia guardada não é atualizada pela redação. A página de cada notícia é baixada uma vez: se a redação corrige o título depois, o banco fica com o da página que o programa baixou. O que muda no banco é o que o programa descobre depois: a página que chegou, um tipo novo no `fontes.csv`, uma frase nova no `boilerplate.txt`, a notícia repetida achada.
- A notícia do mapa do site sem página só tem o dia, sem a hora (`precisao` = `dia`), e fica sem título e sem assinatura. Tudo isso chega quando o `materias.py` baixa a página, numa das rodadas seguintes, e a carga atualiza a notícia.
- O banco segue a silver: uma notícia que sai da silver (porque passou a falhar numa regra de erro) sai também do banco, com as assinaturas, e a tabela `cargas` conta quantas saíram. Por isso, apagar a pasta `dados/` e rodar de novo deixa no banco só as notícias que a silver nova tem.
- Um nome que deixou de assinar fica na tabela `autores`, sem assinatura nenhuma.
- Um nome que não está no `fontes.csv` conta como repórter. Uma agência nova, ou um jornalista de um veículo parceiro, aparece como repórter até você acrescentar uma linha.
- Uma frase repetida nova só sai do texto quando você a põe no `boilerplate.txt`. O `uv run python texto.py` mostra as candidatas.
- A notícia repetida é achada pelo texto quase igual (nota 90 ou mais), em até 3 dias. Os pares entre 80 e 90 ficam para você ler: `uv run python silver.py` mostra.
- Nada roda sozinho: o programa roda quando você manda.
