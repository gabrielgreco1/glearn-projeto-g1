# Projeto G1 (G learn)

Repositório de referência do Projeto 2 do curso G learn: um programa em Python que acompanha as notícias de tecnologia do G1 pelo feed RSS e monta um CSV com uma linha por notícia, sem repetir nenhuma.

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

O README de cada pasta diz a ordem dos comandos. O projeto pronto está em [final/](final), igual à aula 7.

## O que foi rodado

Em 14 de novembro de 2026, com Python 3.13, uv 0.10.11, httpx 0.28.1, feedparser 6.0.14, beautifulsoup4 4.15.0, python-dotenv 1.2.4 e pytest 9.2.0. As saídas estão em [saidas/](saidas).

- Do zero (`rm -rf dados` e `uv run python rodar.py`): 1 pedido ao feed, 100 notícias novas, 20 páginas de notícia.
- Segunda rodada, logo em seguida: o feed respondeu 304, nenhuma notícia nova, mais 20 páginas.
- `uv run python sitemap.py 2026-11-01`: 2 notícias que o feed já não mostrava.
- `uv run pytest`: 5 testes.

## Regras do projeto

Estão em [PADROES.md](PADROES.md).
