"""Testes da leitura do feed. Usam uma amostra escrita à mão: rodam sem internet."""

from pathlib import Path

from ler import editoria, ler_feed

AMOSTRA = Path(__file__).parent / "amostra_feed.xml"


def test_ler_feed_devolve_uma_noticia_por_item():
    noticias = ler_feed(AMOSTRA.read_bytes())
    assert len(noticias) == 2
    assert noticias[0]["titulo"] == "Notícia inventada número dois"
    assert noticias[0]["subtitulo"] == "Subtítulo inventado da segunda notícia."
    assert noticias[0]["imagem"] == "https://exemplo.invalid/foto.jpg"


def test_a_data_fica_como_veio_no_feed():
    noticias = ler_feed(AMOSTRA.read_bytes())
    assert noticias[0]["publicado"] == "Fri, 13 Nov 2026 20:28:07 -0000"


def test_campo_que_o_item_nao_tem_fica_vazio():
    noticias = ler_feed(AMOSTRA.read_bytes())
    assert noticias[1]["subtitulo"] == ""
    assert noticias[1]["imagem"] == ""


def test_editoria_sai_do_endereco():
    assert editoria("https://g1.globo.com/economia/noticia/2026/11/13/x.ghtml") == "economia"
