"""O texto de uma página escrita à mão: dois parágrafos de verdade, uma frase de boilerplate, uma legenda e um vídeo."""

from pathlib import Path

from texto import contar_palavras, espacos, paragrafos

AMOSTRA = Path(__file__).parent / "amostra_materia.html"


def test_so_os_paragrafos_do_texto_entram():
    assert paragrafos(AMOSTRA.read_text(encoding="utf-8")) == [
        "Primeiro parágrafo da notícia inventada, com espaços sobrando.",
        "🗒️Tem alguma sugestão de reportagem? Mande para o g1",
        "Segundo parágrafo — e o último.",
    ]


def test_espacos_tira_o_espaco_antes_da_virgula():
    assert espacos("Jensen Huang , a  vice\xa0. ") == "Jensen Huang, a vice."


def test_contar_palavras_nao_conta_travessao_nem_emoji():
    assert contar_palavras("Segundo parágrafo — e o último. 🗒️") == 5
