# Projeto G1 (G learn)

Repositório de referência do Projeto 2 do curso G learn: um programa em Python que acompanha as notícias de tecnologia do G1 pelo feed RSS e monta um CSV com uma linha por notícia, sem repetir nenhuma. Na segunda etapa, o mesmo programa transforma esse CSV e as páginas guardadas numa tabela limpa: a data em Brasília, o texto sem o que se repete em toda página, quem assina de verdade, a mesma notícia achada com outro link, regras escritas e a resposta em SQL.

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

O README de cada pasta diz a ordem dos comandos. As pastas são cumulativas: a de cada aula tem tudo o que veio antes. O projeto pronto está em [final/](final), igual à aula 14.

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

Os números mudam com o tempo: o feed é outro a cada hora.

## Regras do projeto

Estão em [PADROES.md](PADROES.md).
