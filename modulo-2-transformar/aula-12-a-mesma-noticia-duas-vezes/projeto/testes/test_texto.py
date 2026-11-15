"""O texto de uma página escrita à mão: dois parágrafos de verdade, uma frase de boilerplate, uma legenda e um vídeo."""

from pathlib import Path

from texto import candidatos, chave, contar_palavras, espacos, paragrafos, sem_boilerplate

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


def test_a_chave_junta_as_grafias_da_mesma_frase():
    assert chave("🗒️Tem alguma sugestão de reportagem? Mande para o g1") == chave("🗒️ Tem alguma sugestão de reportagem? Mande para o g1")


def test_sem_boilerplate_tira_so_o_que_esta_na_lista():
    lista = paragrafos(AMOSTRA.read_text(encoding="utf-8"))
    fixos = {chave("Tem alguma sugestão de reportagem? Mande para o g1")}
    assert sem_boilerplate(lista, fixos) == [lista[0], lista[2]]


def test_candidatos_conta_cada_pagina_uma_vez():
    paginas = [["Leia também:", "Texto A", "LEIA TAMBÉM"], ["Leia também", "Texto B"], ["Texto C"]]
    assert candidatos(paginas, minimo=2) == [("leia também", 2)]
