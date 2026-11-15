"""O texto de cada notícia, lido de novo da página guardada, sem pedir nada ao site.

Só os parágrafos do texto entram: legenda de foto, título de vídeo, anúncio e cartão de oferta ficam de fora."""

import re
import unicodedata

from bs4 import BeautifulSoup


def espacos(texto):
    """Um espaço só entre as palavras, nenhum nas pontas nem antes de vírgula e ponto, e os acentos na forma
    composta (NFC). 'Jensen Huang , a vice' vira 'Jensen Huang, a vice'."""
    junto = " ".join(unicodedata.normalize("NFC", texto).split())
    return re.sub(r" ([,.;:!?)])", r"\1", junto)


def paragrafos(html):
    """Os parágrafos do texto da notícia, na ordem da página. Uma página sem texto devolve a lista vazia."""
    pagina = BeautifulSoup(html, "html.parser")
    achados = [espacos(p.get_text(" ")) for p in pagina.select('[itemprop="articleBody"] p.content-text__container')]
    return [p for p in achados if p]


def contar_palavras(corpo):
    """Os pedaços separados por espaço que têm ao menos uma letra ou um número. Emoji e travessão sozinhos não contam."""
    return sum(1 for pedaco in corpo.split() if re.search(r"\w", pedaco))
