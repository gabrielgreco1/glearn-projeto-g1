"""Lê o XML do feed e devolve uma lista de notícias, cada uma como um dicionário."""

import sys
import xml.etree.ElementTree as ET
from datetime import timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlparse

from baixar import FUSO

# Marcas que não são do RSS básico têm um endereço na frente do nome. O apelido evita escrever o endereço inteiro.
APELIDOS = {"atom": "http://www.w3.org/2005/Atom", "media": "http://search.yahoo.com/mrss/"}


def data(texto):
    """'Fri, 13 Nov 2026 20:28:07 -0000' vira '2026-11-13T17:28:07-03:00', no horário de Brasília."""
    instante = parsedate_to_datetime(texto)
    if instante.tzinfo is None:  # o -0000 do G1 chega sem fuso; a hora está em UTC
        instante = instante.replace(tzinfo=timezone.utc)
    return instante.astimezone(FUSO).isoformat()


def editoria(link):
    """O primeiro pedaço do caminho do endereço: 'tecnologia', 'economia', 'mundo'."""
    return urlparse(link).path.strip("/").split("/")[0]


def ler_feed(xml):
    """Recebe o conteúdo do feed e devolve as notícias, da mais nova para a mais antiga."""
    raiz = ET.fromstring(xml)
    noticias = []
    for item in raiz.iter("item"):
        link = item.findtext("link").strip()
        imagem = item.find("media:content", APELIDOS)
        noticias.append({
            "id": item.findtext("guid").strip(),
            "titulo": item.findtext("title").strip(),
            "subtitulo": (item.findtext("atom:subtitle", default="", namespaces=APELIDOS) or "").strip(),
            "link": link,
            "publicado_em": data(item.findtext("pubDate")),
            "editoria": editoria(link),
            "imagem": imagem.get("url") if imagem is not None else "",
        })
    return noticias


def feed_mais_novo():
    """O último feed baixado. Os nomes começam pela data, então a ordem alfabética é a ordem do tempo."""
    arquivos = sorted(Path("dados/feed").glob("*.xml"))
    if not arquivos:
        raise SystemExit("Nenhum feed em dados/feed. Rode antes: uv run python baixar.py")
    return arquivos[-1]


if __name__ == "__main__":
    arquivo = Path(sys.argv[1]) if len(sys.argv) > 1 else feed_mais_novo()
    noticias = ler_feed(arquivo.read_bytes())
    print(f"{arquivo}: {len(noticias)} notícias")
    print(f"da mais nova, {noticias[0]['publicado_em']}, até a mais antiga, {noticias[-1]['publicado_em']}")
    for campo, valor in noticias[0].items():
        print(f"  {campo}: {valor}")
