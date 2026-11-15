"""As datas da silver, a partir de um noticias.csv escrito à mão: uma notícia do mapa, uma do feed sem página e uma com página."""

from datetime import date
from pathlib import Path

import polars as pl

from silver import datas

AMOSTRA = Path(__file__).parent / "amostra_noticias.csv"


def test_a_pagina_vale_mais_que_o_feed_e_vira_horario_de_brasilia():
    linha = datas(pl.read_csv(AMOSTRA)).row(2, named=True)
    assert linha["publicado_em"].isoformat() == "2026-11-14T02:01:26.087000-03:00"
    assert linha["precisao"] == "hora"


def test_o_feed_em_utc_cai_no_dia_anterior_em_brasilia():
    linha = datas(pl.read_csv(AMOSTRA)).row(1, named=True)
    assert linha["publicado_em"].isoformat() == "2026-11-10T21:01:13-03:00"
    assert linha["dia"] == date(2026, 11, 10)


def test_a_noticia_do_mapa_so_tem_o_dia():
    linha = datas(pl.read_csv(AMOSTRA)).row(0, named=True)
    assert linha["publicado_em"] is None
    assert linha["precisao"] == "dia"
    assert linha["dia"] == date(2026, 10, 31)
