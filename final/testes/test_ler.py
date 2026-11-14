"""Testes da leitura do feed. Usam uma amostra escrita à mão: rodam sem internet."""

from pathlib import Path

from ler import data, editoria, ler_feed

AMOSTRA = Path(__file__).parent / "amostra_feed.xml"


def test_data_sem_fuso_vira_horario_de_brasilia():
    assert data("Fri, 13 Nov 2026 20:28:07 -0000") == "2026-11-13T17:28:07-03:00"


def test_data_perto_da_meia_noite_muda_de_dia():
    assert data("Fri, 13 Nov 2026 02:05:00 -0000") == "2026-11-12T23:05:00-03:00"


def test_editoria_sai_do_endereco():
    assert editoria("https://g1.globo.com/economia/noticia/2026/11/13/x.ghtml") == "economia"


def test_ler_feed_devolve_uma_noticia_por_item():
    noticias = ler_feed(AMOSTRA.read_bytes())
    assert len(noticias) == 2
    assert noticias[0]["titulo"] == "Notícia inventada número dois"
    assert noticias[0]["subtitulo"] == "Subtítulo inventado da segunda notícia."
    assert noticias[0]["imagem"] == "https://exemplo.invalid/foto.jpg"
    assert noticias[1]["subtitulo"] == ""
    assert noticias[1]["imagem"] == ""
