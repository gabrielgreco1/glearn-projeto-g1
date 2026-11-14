"""Recupera um dia que o feed já não mostra, pelo mapa do site (sitemap) daquele dia.

Uso: uv run python sitemap.py 2026-11-01"""

import sys
import xml.etree.ElementTree as ET
from datetime import date, datetime
from pathlib import Path

from acumular import acumular
from baixar import FUSO, pedir, registro
from ler import editoria

MAPA = "https://g1.globo.com/sitemap/g1/{dia:%Y/%m/%d}_1.xml"
APELIDOS = {"mapa": "http://www.sitemaps.org/schemas/sitemap/0.9"}
EDITORIA = "tecnologia"


def baixar_mapa(dia):
    """Baixa o mapa do dia. O de um dia que já passou não muda mais, então o arquivo é reaproveitado."""
    destino = Path("dados/sitemap") / f"{dia}.xml"
    if destino.exists() and dia < date.today():
        registro.info("já tenho %s, não peço de novo", destino)
        return destino
    resposta = pedir(MAPA.format(dia=dia))
    if resposta.status_code == 404:
        registro.warning("não existe mapa do site para o dia %s", dia)
        return None
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(resposta.content)
    registro.info("baixei o mapa de %s: %s bytes em %s", dia, len(resposta.content), destino)
    return destino


def ler_mapa(xml):
    """Devolve as notícias da editoria que aparecem no mapa. O mapa traz o endereço e a data, sem o título."""
    noticias = []
    for url in ET.fromstring(xml).iterfind("mapa:url", APELIDOS):
        link = url.findtext("mapa:loc", namespaces=APELIDOS).strip()
        if editoria(link) != EDITORIA or "/noticia/" not in link:
            continue
        mudou = datetime.fromisoformat(url.findtext("mapa:lastmod", namespaces=APELIDOS))
        noticias.append({"id": link, "titulo": "", "subtitulo": "", "link": link,
                         "publicado_em": mudou.astimezone(FUSO).replace(microsecond=0).isoformat(),
                         "editoria": EDITORIA, "imagem": ""})
    return noticias


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Diga o dia. Exemplo: uv run python sitemap.py 2026-11-01")
    mapa = baixar_mapa(date.fromisoformat(sys.argv[1]))
    if mapa:
        acumular(ler_mapa(mapa.read_bytes()), "sitemap")
