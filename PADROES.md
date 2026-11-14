# Padrões do Projeto 2

## Código

- Python 3.13, a versão que o `uv init` gravou no `.python-version`.
- Rodamos tudo com `uv`: `uv sync` para instalar, `uv run python arquivo.py` para rodar, `uv run pytest` para testar.
- Os programas ficam na raiz da pasta do projeto, um arquivo por etapa: `baixar.py`, `ler.py` (com o feedparser), `acumular.py`, `sitemap.py`, `materias.py`, `tabela.py`, `conferir.py`, `rodar.py`.
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
