"""Recupera um dia que o feed já não mostra, pelo mapa do site (sitemap) daquele dia.

Uso: uv run python sitemap.py 2026-11-01"""

import sys
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

from acumular import acumular
from baixar import pedir, registro
from ler import editoria

MAPA = "https://g1.globo.com/sitemap/g1/{dia:%Y/%m/%d}_{parte}.xml"
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}  # o namespace das marcas do mapa do site
EDITORIA = "tecnologia"


def baixar_mapa(dia, parte):
    """Baixa uma parte do mapa do dia. A de um dia que já passou não muda mais, então o arquivo é reaproveitado."""
    destino = Path("dados/bronze/sitemap") / f"{dia}_{parte}.xml"
    if destino.exists() and dia < date.today():
        registro.info("já tenho %s, não peço de novo", destino)
        return destino
    resposta = pedir(MAPA.format(dia=dia, parte=parte))
    if resposta.status_code == 404:
        registro.warning("não existe a parte %s do mapa do dia %s", parte, dia)
        return None
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(resposta.content)
    registro.info("baixei o mapa de %s, parte %s: %s bytes em %s", dia, parte, len(resposta.content), destino)
    return destino


def partes_do_dia(dia):
    """Um dia movimentado tem o mapa dividido em partes de até 1000 endereços. Baixa uma parte de cada vez
    e para na primeira que vier sem endereço nenhum. Devolve os arquivos das partes com endereços."""
    arquivos = []
    for parte in range(1, 100):  # 99 partes no máximo: um limite de segurança, muito acima do que o G1 usa
        arquivo = baixar_mapa(dia, parte)
        if arquivo is None or not ET.fromstring(arquivo.read_bytes()).findall("sm:url", NS):
            break
        arquivos.append(arquivo)
    return arquivos


def ler_mapa(xml):
    """Devolve as notícias da editoria que aparecem no mapa. O mapa traz o endereço e a data, sem o título."""
    noticias = []
    for url in ET.fromstring(xml).findall("sm:url", NS):
        link = url.findtext("sm:loc", namespaces=NS).strip()
        if editoria(link) != EDITORIA or "/noticia/" not in link:
            continue
        noticias.append({"id": link, "titulo": "", "subtitulo": "", "link": link,
                         "publicado": url.findtext("sm:lastmod", default="", namespaces=NS),  # como veio
                         "editoria": EDITORIA, "imagem": ""})
    return noticias


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Diga o dia. Exemplo: uv run python sitemap.py 2026-11-01")
    dia = date.fromisoformat(sys.argv[1])
    if dia > date.today():
        raise SystemExit(f"O dia {dia} ainda não chegou. O G1 responde com um mapa vazio.")
    for arquivo in partes_do_dia(dia):
        acumular(ler_mapa(arquivo.read_bytes()), "sitemap")
