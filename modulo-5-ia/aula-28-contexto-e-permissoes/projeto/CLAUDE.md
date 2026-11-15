# Projeto G1

Notícias de Tecnologia do G1: o feed RSS, o mapa do site e a página de cada notícia, numa silver com quem assina, e um
Postgres na porta 5435. Etapas e regras completas: `README.md` e `PADROES.md` do repositório do curso.

## Como trabalhar aqui

- Responda e escreva commits em português do Brasil.
- Python 3.13 com `uv`: `uv run pytest` para testar. Nunca `pip install`.
- Nomes em português. Caminhos com `pathlib.Path`. Roda em macOS, Linux e Windows: nada de comando de shell no código.

## Testes

- Teste é a especificação. Nunca apague, pule ou mude um teste para ele passar; se o teste parece errado, pare e explique.
- Teste novo usa as amostras de `testes/` (feed, mapa, página), sem internet e sem banco.
- Rode `uv run pytest` antes de dizer que terminou.

## O site do G1

- Você NÃO roda `baixar.py`, `sitemap.py`, `materias.py`, `rodar.py` nem `fluxo.py`: eles pedem ao G1 de verdade.
- O feed é pedido com `If-None-Match` (o `etag` guardado em `dados/estado.json`); 304 quer dizer que nada mudou.
- 2 segundos de pausa depois de cada pedido, no máximo 20 páginas de notícia por rodada.
- O texto das notícias é do G1: não copie texto de notícia para teste, commit ou resposta. Só título e link.

## Git

- Uma branch por issue, um commit por mudança, mensagem que diz o porquê. Não faça push nem abra PR.
- `dados/` e `.env` não vão para o Git, e você não lê o `.env`.
