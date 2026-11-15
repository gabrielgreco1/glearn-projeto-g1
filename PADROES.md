# Padrões do Projeto 2

## Código

- Python 3.13, a versão que o `uv init` gravou no `.python-version`.
- Rodamos tudo com `uv`: `uv sync` para instalar, `uv run python arquivo.py` para rodar, `uv run pytest` para testar.
- Os programas ficam na raiz da pasta do projeto, um arquivo por etapa: `baixar.py`, `ler.py` (com o feedparser), `acumular.py`, `sitemap.py`, `materias.py`, `tabela.py`, `conferir.py`, `rodar.py` na extração; `silver.py`, `texto.py`, `assinatura.py`, `repetidas.py`, `validar.py`, `gold.py` e `transformar.py` na transformação.
- Nomes de arquivos, funções e variáveis em português.
- O programa registra com `logging`.
- Testes com pytest onde há transformação de dado. Os testes usam amostras escritas à mão e rodam sem internet.

## Configuração e segredos

- O contato do `User-Agent` fica no arquivo `.env`. O `.env.example` mostra o campo, sem dado de verdade.
- O `.env` nunca vai para o Git. Ele está no `.gitignore`.
- Nenhuma senha ou chave no código.

## Dados

- Tudo o que o programa baixa ou gera fica em `dados/`. O que veio da fonte fica em `dados/bronze/`, como veio, com a data da coleta no caminho.
- As datas ficam como a fonte escreveu. Converter fuso e formato é da etapa Transformar.
- A pasta `dados/` não vai para o Git. O texto das notícias é do G1.
- Rodar duas vezes não repete notícia nem estraga nada. O arquivo de notícias só cresce.

## Transformar

- A etapa Transformar não faz pedido nenhum ao site. Ela lê o `noticias.csv` e as páginas guardadas em `dados/bronze/materias/`, e pode ser refeita a qualquer hora.
- Tabelas com Polars; perguntas em SQL com DuckDB. A silver e a gold ficam em Parquet.
- As datas viram um instante no horário de Brasília, com a precisão de cada uma: a notícia que só tem o dia fica com o dia, sem hora inventada.
- O texto das notícias é do G1: ele é lido das páginas guardadas para contar as palavras e comparar notícias, mas não vai para a silver.
- Duas listas são mantidas à mão, porque pedem uma decisão: `boilerplate.txt` (as frases que saem do texto) e `fontes.csv` (o tipo de cada nome que não é de um repórter). Os programas mostram o que conferir.
- Nenhuma notícia é apagada em silêncio: o que quebra uma regra de erro vai para `dados/silver/rejeitados.csv`, com o motivo; o que quebra um aviso fica na silver, marcado. A notícia repetida fica, com o link da primeira em `mesma_que`.

## Educação com o site do G1

- A fonte é o feed RSS, que o G1 publica para programas. A página de lista não é raspada.
- Todo pedido leva um `User-Agent` com o nome do projeto e um contato de verdade.
- Um pedido de cada vez, com 2 segundos de espera depois de cada um. No máximo 20 páginas de notícia por rodada.
- O feed é pedido com `If-None-Match`. Se não mudou, nada é baixado.
- Se o site recusar o pedido, o programa para e você lê a mensagem. Não tente contornar.

## Git

- O aluno trabalha na pasta dele, `projeto-g1/`, criada na aula 1. Ela é o repositório do aluno.
- Este repositório do curso é a referência.
- Um commit por aula, com push ao fim de cada aula.
