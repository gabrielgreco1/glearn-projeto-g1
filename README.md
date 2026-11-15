# Projeto G1 (G learn)

Repositório de referência do Projeto 2 do curso G learn: um programa em Python que acompanha as notícias de tecnologia do G1 pelo feed RSS e monta um CSV com uma linha por notícia, sem repetir nenhuma. Na segunda etapa, o mesmo programa transforma esse CSV e as páginas guardadas numa tabela limpa: a data em Brasília, o texto sem o que se repete em toda página, quem assina de verdade, a mesma notícia achada com outro link, regras escritas e a resposta em SQL. Na terceira, ele guarda essa tabela num Postgres que roda no Docker: cada notícia uma vez, pelo link, quem assina numa tabela só dos nomes e a gold refeita no banco. Na quarta, o projeto vira um flow do Prefect que roda sozinho de 3 em 3 horas, tapa pelo mapa do site o buraco de quando ficou parado, baixa de novo a página que a redação mudou, avisa o que sai do normal e tem os testes no GitHub.

## Como usar

Você faz o projeto na SUA pasta, `projeto-g1/`, no SEU repositório, seguindo as aulas na plataforma. Este repositório serve para conferir: a pasta `projeto/` de cada aula mostra como a sua pasta deve estar no fim daquela aula.

## As aulas

| Aula | Pasta | O que roda |
|---|---|---|
| 1 | [Antes de raspar, procure o feed](modulo-1-extrair/aula-01-antes-de-raspar-procure-o-feed) | Nada para rodar. Só o `README.md` com o plano. |
| 2 | [Pedir o feed, e só quando ele mudou](modulo-1-extrair/aula-02-pedir-o-feed) | `uv run python baixar.py` |
| 3 | [Do feed à notícia](modulo-1-extrair/aula-03-do-feed-a-noticia) | `uv run python ler.py` e `uv run pytest` |
| 4 | [Guardar sem repetir](modulo-1-extrair/aula-04-guardar-sem-repetir) | `uv run python acumular.py` |
| 5 | [O que o feed já não mostra](modulo-1-extrair/aula-05-o-que-o-feed-nao-mostra) | `uv run python sitemap.py 2026-11-01` |
| 6 | [A página de cada notícia, poucas por vez](modulo-1-extrair/aula-06-a-pagina-de-cada-noticia) | `uv run python materias.py` |
| 7 | [Fechar o projeto: uma rodada, um comando](modulo-1-extrair/aula-07-fechar-o-projeto) | `uv run python rodar.py` e `uv run pytest` |

### Etapa Transformar

| Aula | Pasta | O que roda |
|---|---|---|
| 8 | [Três jeitos de dizer quando](modulo-2-transformar/aula-08-tres-jeitos-de-dizer-quando) | `uv run python silver.py` |
| 9 | [O texto de volta do bronze](modulo-2-transformar/aula-09-o-texto-de-volta-do-bronze) | `uv run python silver.py` |
| 10 | [O que se repete em toda página](modulo-2-transformar/aula-10-o-que-se-repete-em-toda-pagina) | `uv run python texto.py` e `uv run python silver.py` |
| 11 | [Quem assina a notícia](modulo-2-transformar/aula-11-quem-assina-a-noticia) | `uv run python assinatura.py` e `uv run python silver.py` |
| 12 | [A mesma notícia duas vezes](modulo-2-transformar/aula-12-a-mesma-noticia-duas-vezes) | `uv run python silver.py` |
| 13 | [O que barra e o que só avisa](modulo-2-transformar/aula-13-o-que-barra-e-o-que-avisa) | `uv run python validar.py` |
| 14 | [Extrair e transformar num comando só](modulo-2-transformar/aula-14-extrair-e-transformar-num-comando) | `uv run python rodar.py` e `uv run pytest` |

### Etapa Carregar

| Aula | Pasta | O que roda |
|---|---|---|
| 15 | [Um banco para as notícias](modulo-3-carregar/aula-15-um-banco-para-as-noticias) | `docker compose up -d --wait` e `uv run python banco.py` |
| 16 | [Cada notícia uma vez, pelo link](modulo-3-carregar/aula-16-cada-noticia-uma-vez) | `uv run python carregar.py` |
| 17 | [Quem assina, numa tabela só](modulo-3-carregar/aula-17-quem-assina-numa-tabela-so) | `uv run python carregar.py` e as consultas no `psql` |
| 18 | [A notícia que mudou depois](modulo-3-carregar/aula-18-a-noticia-que-mudou-depois) | `uv run python materias.py`, `tabela.py`, `transformar.py` e `carregar.py` |
| 19 | [As perguntas no banco](modulo-3-carregar/aula-19-as-perguntas-no-banco) | `uv run python carregar.py` e as views no `psql` |
| 20 | [Extrair, transformar e carregar num comando](modulo-3-carregar/aula-20-extrair-transformar-e-carregar) | `uv run python rodar.py` e `uv run pytest` |

### Etapa Orquestrar

| Aula | Pasta | O que roda |
|---|---|---|
| 21 | [O projeto G1 no Prefect](modulo-4-orquestrar/aula-21-o-projeto-no-prefect) | `uv run python fluxo.py` |
| 22 | [A janela do feed e a hora de rodar](modulo-4-orquestrar/aula-22-a-janela-do-feed) | `uv run python janela.py` e `uv run python fluxo.py agendar` |
| 23 | [A página que a redação mudou](modulo-4-orquestrar/aula-23-a-pagina-que-a-redacao-mudou) | `uv run python fluxo.py` |
| 24 | [A vigia: o feed parado e a página sem texto](modulo-4-orquestrar/aula-24-a-vigia) | `uv run python vigiar.py` e `uv run python fluxo.py` |
| 25 | [Uma execução por vez](modulo-4-orquestrar/aula-25-uma-execucao-por-vez) | `uv run prefect gcl create projeto-g1 --limit 1` e duas vezes `uv run python fluxo.py` |
| 26 | [Os testes no GitHub e a prova final](modulo-4-orquestrar/aula-26-os-testes-no-github-e-a-prova-final) | `uv run pytest` sem o `.env` e a prova numa cópia limpa |

O README de cada pasta diz a ordem dos comandos. As pastas são cumulativas: a de cada aula tem tudo o que veio antes. O projeto pronto está em [final/](final), igual à aula 26. A partir da aula 15, o projeto precisa do Docker: o Postgres roda num container, na porta 5435.

## O que foi rodado

Em 14 de novembro de 2026, com Python 3.13, uv 0.10.11, httpx 0.28.1, feedparser 6.0.14, beautifulsoup4 4.15.0, python-dotenv 1.2.4 e pytest 9.2.0. Cada pasta de aula foi copiada para uma pasta limpa e rodada do zero com os comandos do README dela. As saídas estão em [saidas/](saidas), uma por aula.

- Do zero (`rm -rf dados` e `uv run python rodar.py`): 1 pedido ao feed, 100 notícias novas, 20 páginas de notícia.
- Segunda rodada, logo em seguida: o feed respondeu 304, nenhuma notícia nova, mais 20 páginas.
- `uv run python sitemap.py 2026-11-01`: 2 notícias que o feed já não mostrava, lidas da parte 1 do mapa do dia (a parte 2 veio vazia).
- A rodada seguinte põe essas 2 notícias no começo da tabela, no lugar do dia delas: `notícias do dia 2026-10-31 ao dia 2026-11-14`.
- `uv run pytest`: 9 testes.

### Etapa Transformar

Em 15 de novembro de 2026, com polars 2.1.0, rapidfuzz 3.14.6 e duckdb 2.0.0. Um `dados/` coletado entre 3h03 e 3h09 (o feed, os mapas do site de 1 a 4/11 e seis rodadas de páginas: 110 notícias, 104 páginas) foi copiado para uma pasta limpa de cada aula, e as aulas 8 a 14 rodaram sobre ele. As saídas estão em [saidas/transformar/](saidas/transformar).

- As datas: 104 notícias com hora, 6 só com o dia (do mapa do site, ainda sem página). Uma notícia do TSE, publicada às 21h01 de 10/11 em Brasília, é 0h01 de 11/11 no feed, em UTC.
- O texto: a mediana de palavras cai de 692,5 (a página inteira) para 598,5 (só os parágrafos) e para 589,5 (sem o boilerplate, 5 frases).
- Quem assina: a marca `author` diz G1 em 39 páginas que a assinatura visível dá à Reuters, à France Presse, à BBC, à Associated Press, à Deutsche Welle e à Serasa Experian (publicidade).
- A mesma notícia com outro link: 3 pares com o texto 90% igual ou mais, e 1 par para ler.
- As regras: 110 lidas, 110 válidas, 0 rejeitadas. A gold: das 107 notícias sem as repetidas, 41 vieram de fora e 58 o g1 escreveu.
- Do zero, numa pasta limpa, contra o G1 ao vivo (3h27): 100 notícias, 20 páginas, 80% sem página na gold; a segunda rodada recebe 304, baixa mais 20 páginas e acha a primeira repetida. 26 testes.

### Etapa Carregar

Em 15 de novembro de 2026, com psycopg 3.3.9 e Postgres 18.7 (`postgres:18`) no Docker 29.5.2 (Colima, Apple M). O mesmo `dados/` congelado da etapa Transformar foi a pasta do aluno, e as aulas 15 a 19 rodaram em ordem, com o banco zerado no começo. As saídas estão em [saidas/carregar/](saidas/carregar).

- A carga: 110 notícias novas; a segunda rodada, 110 iguais. O id vai de 1 a 110, e a sequência já está em 220: cada linha que tentou entrar de novo gastou um número.
- Quem assina: 26 nomes e 107 assinaturas. Sem a linha da Reuters no `fontes.csv`, a coluna fonte da silver muda em 18 notícias; no banco, muda uma linha da tabela `autores`.
- As 6 notícias do mapa do site sem página: o `materias.py` baixou as 6 páginas às 6h03, e a carga seguinte atualizou as 6 (`carregada_em` ficou, `mudou_em` andou), com 6 assinaturas e 1 nome novo.
- As views `por_dia` e `por_fonte`, montadas sobre as três tabelas, dão as mesmas linhas que a gold. Com a gold velha, a carga para e é desfeita.
- O título: 36 de 110 falam da Nvidia. O índice de trigramas ocupa 128 kB, o dobro da tabela, e o Postgres prefere ler a tabela.
- Do zero, numa cópia limpa (`git clone .`), contra o G1 ao vivo (6h16): 100 notícias novas, 20 páginas; a segunda rodada recebeu 304, baixou mais 20 páginas, e a carga atualizou 20 notícias; a terceira carga, nada. 33 testes.

Os números mudam com o tempo: o feed é outro a cada hora.

### Etapa Orquestrar

Em 15 de novembro de 2026, com Prefect 3.9.3 e o servidor local do Prefect. A pasta do aluno veio do `final/` da etapa Carregar, com o `dados/` da etapa (110 notícias) e um banco novo, e as aulas 21 a 26 rodaram em ordem, das 10h28 às 11h25, contra o G1 ao vivo, com as falhas provocadas de verdade. As saídas estão em [saidas/orquestrar/](saidas/orquestrar), e o que cada aula mostrou está no README do [final/](final), em "O que a etapa Orquestrar mostrou".

- Sem rede (um proxy que não existe), o feed foi tentado 4 vezes e a execução terminou em `Failed`; com o banco desligado, em `Crashed`. As duas deixaram uma linha em `avisos.log`.
- A janela do feed: 100 notícias, 10 dias e 22 horas. Um buraco de propósito recuperou 28 notícias pelo mapa do site de 9 dias.
- 59 de 141 páginas mudaram mais de 1 hora depois de publicadas. A página mudada é baixada de novo pelo `lastmod` do mapa do site.
- Páginas sem texto de propósito: tudo terminou em `Completed`, e só a vigia avisou. Duas rodadas ao mesmo tempo baixaram as mesmas 12 páginas; com o limite `projeto-g1`, a segunda esperou e não baixou nenhuma.
- Os testes no GitHub: vermelho no primeiro push (o contato lido no import), verde depois do conserto, 52 testes. Uma execução marcada pelo agendamento, com um cron de 2 em 2 minutos numa cópia do `fluxo.py`, rodou sozinha (`verifica-cron.txt`).
- Cada pasta de aula numa cópia limpa, com banco novo e o G1 ao vivo (`limpas.txt`), e o `final/` clonado do GitHub para uma pasta nova, com Ctrl+C no meio das páginas, a retomada e uma execução pelo agendamento (`prova-final-clone-do-repositorio.txt`).

## Regras do projeto

Estão em [PADROES.md](PADROES.md).
