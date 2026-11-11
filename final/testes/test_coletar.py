"""Testes do nome estável do arquivo em bronze e das regras de caminho."""

import re

from comum import nome_estavel
from coletar import url_da_pagina_de_lista


def test_nome_estavel_e_o_mesmo_para_a_mesma_url():
    url = "https://g1.globo.com/tecnologia/noticia/2026/11/11/exemplo-uma-noticia.ghtml"
    assert nome_estavel(url) == nome_estavel(url)


def test_nome_estavel_muda_com_a_url_e_tem_formato_fixo():
    a = nome_estavel("https://g1.globo.com/tecnologia/noticia/2026/11/11/a.ghtml")
    b = nome_estavel("https://g1.globo.com/tecnologia/noticia/2026/11/11/b.ghtml")
    assert a != b
    assert re.fullmatch(r"materia-[0-9a-f]{16}\.html", a)


def test_paginas_de_lista():
    assert url_da_pagina_de_lista(1) == "https://g1.globo.com/tecnologia/"
    assert url_da_pagina_de_lista(2) == "https://g1.globo.com/tecnologia/index/feed/pagina-2.ghtml"
