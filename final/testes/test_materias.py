"""O nome do arquivo de cada notícia sai do endereço, sem precisar de nada guardado. A página que a redação mudou
depois de baixada é achada pelo mapa do site."""

from materias import PASTA, arquivo_da, mudou

LINK = "https://g1.globo.com/tecnologia/noticia/2026/11/14/x.ghtml"
PAGINA = '<html><head><meta itemprop="dateModified" content="2026-11-14T10:31:22.232-03:00"></head></html>'


def test_nome_do_arquivo_vem_do_caminho():
    noticia = {"link": "https://g1.globo.com/tecnologia/noticia/2026/11/13/chat-gpt-wallet.ghtml"}
    assert arquivo_da(noticia).name == "tecnologia_noticia_2026_11_13_chat-gpt-wallet.html"


def test_endereco_estranho_nao_escolhe_a_pasta():
    noticia = {"link": "https://g1.globo.com/tecnologia/..\\..\\outra-pasta/x.ghtml"}
    arquivo = arquivo_da(noticia)
    assert arquivo.parent == PASTA
    assert ".." not in arquivo.name and "\\" not in arquivo.name


def guardar_pagina(tmp_path, monkeypatch, html):
    monkeypatch.chdir(tmp_path)  # a PASTA das páginas é relativa à pasta atual
    PASTA.mkdir(parents=True)
    arquivo_da({"link": LINK}).write_text(html, encoding="utf-8")


def test_mudou_quando_o_mapa_e_mais_novo_que_a_pagina(tmp_path, monkeypatch):
    guardar_pagina(tmp_path, monkeypatch, PAGINA)
    assert mudou({"link": LINK}, {LINK: "2026-11-14T21:08:47.234000+00:00"})


def test_a_mesma_hora_com_outros_milesimos_nao_mudou(tmp_path, monkeypatch):
    guardar_pagina(tmp_path, monkeypatch, PAGINA)
    assert not mudou({"link": LINK}, {LINK: "2026-11-14T13:31:22.611000+00:00"})


def test_pagina_vazia_ou_fora_do_mapa_nao_mudou(tmp_path, monkeypatch):
    guardar_pagina(tmp_path, monkeypatch, "")
    assert not mudou({"link": LINK}, {LINK: "2026-11-14T21:08:47.234000+00:00"})
    assert not mudou({"link": LINK}, {})
