"""Testes da leitura do mapa do site. Usam uma amostra escrita à mão: rodam sem internet."""

from pathlib import Path

from sitemap import dia_do_endereco, ler_mapa

AMOSTRA = Path(__file__).parent / "amostra_mapa.xml"


def test_mapa_fica_so_com_a_editoria():
    noticias = ler_mapa(AMOSTRA.read_bytes())
    assert [noticia["link"] for noticia in noticias] == [
        "https://g1.globo.com/tecnologia/noticia/2026/10/31/noticia-inventada.ghtml"]


def test_publicado_e_o_dia_do_endereco_e_lastmod_fica_na_sua_coluna():
    noticia = ler_mapa(AMOSTRA.read_bytes())[0]
    assert noticia["publicado"] == "2026-10-31"
    assert noticia["lastmod"] == "2026-11-01T00:27:31.045000+00:00"


def test_endereco_sem_data_fica_sem_dia():
    assert dia_do_endereco("https://g1.globo.com/tecnologia/2026/franca-ataque-geladeiras.ghtml") == ""
