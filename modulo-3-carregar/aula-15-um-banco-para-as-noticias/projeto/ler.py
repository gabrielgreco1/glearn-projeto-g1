"""Lê o feed com o feedparser e devolve uma lista de notícias, cada uma como um dicionário.

Os campos ficam como vieram: a data continua no texto do feed. Converter é trabalho da etapa Transformar."""

import sys
from pathlib import Path
from urllib.parse import urlparse

import feedparser


def editoria(link):
    """O primeiro pedaço do caminho do endereço: 'tecnologia', 'economia', 'mundo'."""
    return urlparse(link).path.strip("/").split("/")[0]


def ler_feed(xml):
    """Recebe o conteúdo do feed e devolve as notícias, na ordem do feed: da mais nova para a mais antiga."""
    feed = feedparser.parse(xml)
    if feed.bozo:
        raise ValueError(f"o feed veio quebrado: {feed.bozo_exception}")
    noticias = []
    for item in feed.entries:
        imagens = item.get("media_content", [])
        noticias.append({
            "id": item.id,
            "titulo": item.title,
            "subtitulo": item.get("subtitle", ""),
            "link": item.link,
            "publicado": item.get("published", ""),
            "editoria": editoria(item.link),
            "imagem": imagens[0]["url"] if imagens else "",
        })
    return noticias


def feed_mais_novo():
    """O último feed baixado. Pastas e nomes começam pela data, então a ordem alfabética é a ordem do tempo."""
    arquivos = sorted(Path("dados/bronze/feed").glob("*/*.xml"))
    if not arquivos:
        raise SystemExit("Nenhum feed em dados/bronze/feed. Rode antes: uv run python baixar.py")
    return arquivos[-1]


if __name__ == "__main__":
    arquivo = Path(sys.argv[1]) if len(sys.argv) > 1 else feed_mais_novo()
    noticias = ler_feed(arquivo.read_bytes())
    print(f"{arquivo}: {len(noticias)} notícias")
    for campo, valor in noticias[0].items():
        print(f"  {campo}: {valor}")
