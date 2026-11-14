"""O nome do arquivo de cada notícia sai do endereço, sem precisar de nada guardado."""

from materias import PASTA, arquivo_da


def test_nome_do_arquivo_vem_do_caminho():
    noticia = {"link": "https://g1.globo.com/tecnologia/noticia/2026/11/13/chat-gpt-wallet.ghtml"}
    assert arquivo_da(noticia).name == "tecnologia_noticia_2026_11_13_chat-gpt-wallet.html"


def test_endereco_estranho_nao_escolhe_a_pasta():
    noticia = {"link": "https://g1.globo.com/tecnologia/..\\..\\outra-pasta/x.ghtml"}
    arquivo = arquivo_da(noticia)
    assert arquivo.parent == PASTA
    assert ".." not in arquivo.name and "\\" not in arquivo.name
