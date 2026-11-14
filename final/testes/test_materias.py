"""O nome do arquivo de cada notícia sai do endereço, sem precisar de nada guardado."""

from materias import arquivo_da


def test_nome_do_arquivo_vem_do_caminho():
    noticia = {"link": "https://g1.globo.com/tecnologia/noticia/2026/11/13/chat-gpt-wallet.ghtml"}
    assert arquivo_da(noticia).name == "tecnologia_noticia_2026_11_13_chat-gpt-wallet.html"
