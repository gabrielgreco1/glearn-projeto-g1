# Projeto G1: versão final (só a parte de extrair)

Coleta as notícias da editoria Tecnologia do G1 (https://g1.globo.com/tecnologia/): a lista de manchetes, várias páginas dessa lista, e a página de cada matéria. Depois transforma tudo numa tabela, uma linha por matéria.

## Como rodar

```bash
cp .env.example .env        # e troque o contato dentro do G1_USER_AGENT
uv sync
uv run python src/coletar.py
uv run python src/extrair.py
uv run pytest
uv run ruff check .
```

Configuração (no `.env`):

- `G1_USER_AGENT`: identificação do seu programa, com um jeito de falar com você.
- `G1_PAUSA`: segundos entre um pedido e o próximo. Nunca menos de 1 (o código força esse mínimo).

## O que sai

- `dados/bronze/coleta=AAAA-MM-DD/`: os arquivos como vieram do site.
  - `robots.txt`: a regra do site, guardada no dia da coleta.
  - `lista-pagina-1.html`, `lista-pagina-2.html`, `lista-pagina-3.html`: as páginas de lista.
  - `materia-<16 caracteres>.html`: uma página por matéria. O nome vem de um hash da URL, então é sempre o mesmo para a mesma matéria.
  - Cada um desses arquivos tem ao lado um `.origem.json` com `url`, `status`, `tipo`, `instante`, `sha256` e `bytes`.
- `dados/silver/noticias.csv`: uma linha por matéria, com as colunas `url, titulo, subtitulo, publicado_em, autor, editoria, n_palavras`.
  - `publicado_em` vem em ISO 8601 com fuso, por exemplo `2026-11-11T11:40:07-03:00`.
  - `n_palavras` é a contagem de palavras do corpo. O texto da matéria não vai para o CSV.

Rodar `coletar.py` de novo no mesmo dia não baixa nada que já esteja em bronze. Ele só diz quantos arquivos já existiam.

## Como a paginação foi descoberta

Investigado com requisições comuns, em novembro de 2026:

1. A página `/tecnologia/` já traz a primeira leva de matérias. As matérias aparecem em blocos com a classe `feed-post` e dentro de um bloco JSON embutido na página (com `feedId`, `limit` e `nextPage`).
2. O feed do próprio site aponta para uma API (`falkor-cda.bastian.globo.com`). Pedir essa API com `?page=2` devolveu 404, então ela não é usada.
3. Tentei `https://g1.globo.com/index/feed/pagina-2.ghtml`, que devolveu a home do portal e não a editoria. Descartado.
4. `https://g1.globo.com/tecnologia/index/feed/pagina-2.ghtml` devolve a página da editoria com matérias novas, com o mesmo modelo de HTML. Pela página 2 aparecerem 9 links que não estavam na página 1, esse é o caminho usado. A página 3 segue o mesmo padrão e acrescenta mais 10.

Caminho usado: página 1 = `/tecnologia/`; página N (2 e 3) = `/tecnologia/index/feed/pagina-N.ghtml`. Os links das matérias saem das âncoras da página, e os repetidos são descartados.

Observação: o bloco JSON embutido informa `nextPage`, mas o valor muda de uma página para outra (4 na primeira, 3 na segunda). Por isso o código não usa esse número; ele monta o endereço da página pelo padrão acima.

## O que o robots.txt permite

Lido em 2026-11-11 em `https://g1.globo.com/robots.txt` (cópia salva no bronze). Para `User-agent: *`, estão proibidos entre outros: `/jornalismo/g1/`, `/_ssi/`, `/beta/`, `/componentes/`, `/busca/*`, `/zeta/`, `/content-aggregator/`, `/jogos-app/`, `/espiar/`, `/teste-*.html`, `*globo-cdn-src/*`.

Os caminhos usados aqui não são proibidos: `/tecnologia/`, `/tecnologia/index/feed/pagina-N.ghtml` e as matérias com `/noticia/AAAA/MM/DD/` (em `/tecnologia/`, `/economia/`, `/mundo/`, `/politica/`, `/mg/`, `/sp/`, entre outros). A busca do site não é usada. O código confere o robots.txt e a lista acima antes de cada pedido. O robots.txt também aponta mapas do site (sitemap), que este projeto não usa.

## Regras de coleta

- Uma requisição por vez, com pausa de `G1_PAUSA` segundos depois de cada uma.
- Em 429 ou 5xx: espera e tenta de novo, no máximo 3 vezes, dobrando a espera (2, 4 e 8 segundos). Depois disso, registra e segue.
- Em 403 ou página de bloqueio ou de acesso negado: a coleta para e o erro é registrado. Não há navegador automatizado, proxy nem troca de identidade.

## Como os campos são lidos

Ordem de preferência em `src/extrair.py`:

- `titulo`: metatag `og:title` (sem o sufixo ` | G1`). Se faltar, o `h1`.
- `subtitulo`: não existe dado estruturado para isso nesta página, então o `h2` com `itemprop="alternativeHeadline"`.
- `publicado_em`: microdado `datePublished` (metatag com `content`). Se faltar, o `time`.
- `autor`: microdado `author` com o `name`. Se o G1 não trouxer autor, o campo fica vazio.
- `editoria`: JSON-LD `articleSection` (última posição, por exemplo `Tecnologia`). Se faltar, `article:section`.
- `n_palavras`: palavras do bloco `articleBody`.

Escolha: os dados estruturados vêm primeiro porque são feitos para máquina e mudam menos que o layout. O HTML entra quando o estruturado não existe.

## Direito autoral

O texto das matérias não vai para o repositório: `dados/` está no `.gitignore` inteiro. O CSV guarda título, subtítulo e a contagem de palavras.

A amostra de teste em `testes/amostras/` foi escrita à mão, com conteúdo inventado. Tem a mesma estrutura de uma página real, mas não é cópia de matéria. O comentário no topo de cada arquivo diz isso.

## Limites

- No máximo 3 páginas de lista. É o que mostrou que o feed tem matérias novas, e cada página é um pedido a mais.
- No máximo 30 matérias no total. Mantém a coleta pequena e dentro da pausa de 1 segundo por pedido.
- Cada matéria exige um pedido. Com 30 matérias, mais as 3 listas e o robots.txt, são 34 pedidos numa coleta nova, o que leva uns 40 segundos.
- Se o G1 mudar o layout, a leitura pode falhar. Se a página de lista vier sem links de matéria, a coleta segue sem matérias e o CSV sai vazio. Campos ausentes numa matéria ficam vazios.
