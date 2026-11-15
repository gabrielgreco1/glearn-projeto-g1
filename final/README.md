# Projeto G1

Objetivo: acompanhar as notícias de tecnologia do G1, montar um arquivo CSV com uma linha por notícia, sem repetir nenhuma, e transformar esse arquivo numa tabela limpa que responde quem escreve o que o feed traz.
Plano: o G1 publica um feed RSS da editoria, feito para programas. O programa pede o feed, guarda só o que é novo e, para o que o feed já não mostra, usa o mapa do site. A etapa Transformar lê de novo o que foi guardado, sem pedir nada ao site.

## Como rodar

```bash
cp .env.example .env        # e troque o contato dentro do G1_USER_AGENT
uv sync
uv run python rodar.py
uv run pytest
```

Rode de novo quando quiser. Cada rodada faz um pedido ao feed, baixa, no máximo, 20 páginas de notícia e refaz a etapa Transformar inteira.

Para recuperar um dia que o feed já não mostra:

```bash
uv run python sitemap.py 2026-11-01
```

Para refazer só a etapa Transformar, sem pedido nenhum: `uv run python transformar.py`.

No Windows, os comandos são os mesmos no PowerShell. Para apagar a pasta `dados/` e começar do zero: `Remove-Item -Recurse -Force dados` (no macOS e no Linux, `rm -rf dados`).

## As etapas

| Etapa | Programa | O que faz |
|---|---|---|
| 1 | `baixar.py` | pede o feed, só se ele mudou |
| 2 | `acumular.py` | guarda as notícias novas em `noticias.jsonl` |
| 3 | `materias.py` | baixa a página de até 20 notícias |
| 4 | `tabela.py` e `conferir.py` | monta e confere o `noticias.csv` |
| 5 | `transformar.py` | a silver (`silver.py`, com `texto.py`, `assinatura.py` e `repetidas.py`), as regras (`validar.py`) e a gold (`gold.py`) |

## O que sai

Tudo fica em `dados/`, que não vai para o Git:

- `bronze/feed/`, `bronze/sitemap/` e `bronze/materias/`: o que veio do G1, como veio.
- `estado.json`: o que o programa lembra de uma rodada para a outra.
- `noticias.jsonl` e `noticias.csv`: as notícias guardadas e a tabela da extração, com as datas como a fonte escreveu.
- `silver/noticias.parquet`: uma linha por notícia, com o dia e a hora em Brasília, as palavras do texto sem o boilerplate, quem assina, o tipo da fonte (redação, repórter, agência ou publicidade), o link da notícia repetida e os avisos.
- `silver/rejeitados.csv`: as notícias que falharam numa regra de erro, com o motivo.
- `gold/por_dia.parquet` e `gold/por_fonte.parquet`: as notícias de cada dia, quantas o g1 escreveu e quantas vieram de fora, e o tamanho do texto.

Os dois arquivos que você mantém à mão: `boilerplate.txt`, com as frases que saem do texto, e `fontes.csv`, com o tipo de cada nome que não é de um repórter.

## Regras de coleta

- Todo pedido leva um `User-Agent` com o nome do projeto e um contato de verdade.
- Um pedido de cada vez, com 2 segundos de espera depois de cada um.
- O feed é pedido com o `etag` da última vez. Se não mudou, o servidor responde 304 e nada é baixado.
- Se o site recusar um pedido, o programa para. Não tente contornar.
- O texto das notícias é do G1. Ele fica só no seu computador.

## O que o projeto não faz

- Uma notícia guardada não é atualizada. Se a redação corrige o título depois, o arquivo fica com o título da primeira vez que o programa viu a notícia.
- A notícia do mapa do site sem página só tem o dia, sem a hora (`precisao` = `dia`). A hora chega quando o `materias.py` baixa a página, numa das rodadas seguintes.
- Um nome que não está no `fontes.csv` conta como repórter. Uma agência nova, ou um jornalista de um veículo parceiro, aparece como repórter até você acrescentar uma linha.
- Uma frase repetida nova só sai do texto quando você a põe no `boilerplate.txt`. O `uv run python texto.py` mostra as candidatas.
- A notícia repetida é achada pelo texto quase igual (nota 90 ou mais), em até 3 dias. Os pares entre 80 e 90 ficam para você ler: `uv run python silver.py` mostra.
- Nada roda sozinho: o programa roda quando você manda.
