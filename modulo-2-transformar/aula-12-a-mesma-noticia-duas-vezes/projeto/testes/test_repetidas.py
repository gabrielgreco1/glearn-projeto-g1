"""A mesma notícia com dois links: três textos inventados, dois quase iguais e um diferente, e um quarto fora do bloco."""

from datetime import date, datetime

import polars as pl

from repetidas import marcar, pares

TEXTO = "A empresa inventada anunciou nesta quinta-feira que vai demitir parte da equipe depois de um ano ruim."
TABELA = pl.DataFrame({
    "link": ["a", "b", "c", "d"],
    "dia": [date(2026, 11, 9), date(2026, 11, 12), date(2026, 11, 12), date(2026, 11, 20)],
    "publicado_em": [datetime(2026, 11, 9, 10), datetime(2026, 11, 12, 9), datetime(2026, 11, 12, 15), datetime(2026, 11, 20, 8)],
    "texto": [TEXTO, TEXTO.replace("quinta-feira", "sexta-feira"), "Um texto que fala de outra coisa, sem nada em comum.", TEXTO],
    "palavras": [18, 18, 11, 18],
})


def test_pares_acha_o_texto_quase_igual_dentro_do_bloco():
    achados = pares(TABELA)
    assert achados.select("antiga", "nova").rows() == [("a", "b")]  # o d é igual ao a, mas está 11 dias depois
    assert achados["nota"][0] >= 90


def test_marcar_poe_o_link_antigo_na_noticia_nova():
    marcado = marcar(TABELA, pares(TABELA))
    assert marcado["mesma_que"].to_list() == [None, "a", None, None]
