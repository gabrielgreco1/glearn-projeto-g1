"""Lê o feed com o feedparser e devolve uma lista de notícias, cada uma como um dicionário.

Os campos ficam como vieram: a data continua no texto do feed. Converter é trabalho da etapa Transformar."""

import sys
from pathlib import Path
from urllib.parse import urlparse

import feedparser


def editoria(link):
    """O primeiro pedaço do caminho do endereço: 'tecnologia', 'economia', 'mundo'."""
    return urlparse(link).path.strip("/").split("/")[0]


def ler_feed(xml, feed=""):
    """Recebe o conteúdo do feed e devolve as notícias, na ordem do feed: da mais nova para a mais antiga. feed é o
    nome do feed de onde veio ('tecnologia', 'economia') e fica em cada notícia. Não é a editoria, que sai do endereço:
    o feed de tecnologia também traz notícias de mundo, inovação..."""
    lido = feedparser.parse(xml)
    if lido.bozo:
        raise ValueError(f"o feed veio quebrado: {lido.bozo_exception}")
    noticias = []
    for item in lido.entries:
        imagens = item.get("media_content", [])
        noticias.append({
            "id": item.id,
            "titulo": item.title,
            "subtitulo": item.get("subtitle", ""),
            "link": item.link,
            "publicado": item.get("published", ""),
            "editoria": editoria(item.link),
            "feed": feed,
            "imagem": imagens[0]["url"] if imagens else "",
        })
    return noticias


def feed_mais_novo(feed="tecnologia"):
    """O último arquivo baixado de um feed. Pastas e nomes começam pela data, então a ordem alfabética é a do tempo."""
    arquivos = sorted((Path("dados/bronze/feed") / feed).glob("*/*.xml"))
    if not arquivos:
        raise SystemExit(f"Nenhum feed de {feed} em dados/bronze/feed/{feed}. Rode antes: uv run python baixar.py")
    return arquivos[-1]


if __name__ == "__main__":
    arquivo = Path(sys.argv[1]) if len(sys.argv) > 1 else feed_mais_novo()
    noticias = ler_feed(arquivo.read_bytes(), arquivo.parts[-3])  # dados/bronze/feed/<feed>/<dia>/<hora>.xml
    print(f"{arquivo}: {len(noticias)} notícias")
    for campo, valor in noticias[0].items():
        print(f"  {campo}: {valor}")
