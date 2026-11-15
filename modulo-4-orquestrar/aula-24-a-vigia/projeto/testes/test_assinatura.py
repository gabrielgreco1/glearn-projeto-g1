"""Quem assina: a linha "Por ..." de uma página escrita à mão e o tipo de cada fonte."""

from pathlib import Path

import polars as pl

from assinatura import autores, fontes

AMOSTRA = Path(__file__).parent / "amostra_materia.html"


def test_autores_saem_do_title_da_assinatura():
    assert autores(AMOSTRA.read_text(encoding="utf-8")) == ["Ana Exemplo", "Beto Exemplo"]


def test_pagina_sem_assinatura_fica_sem_autores():
    assert autores("<html><body><p>Sem assinatura</p></body></html>") is None


def test_fonte_pelo_mapa_e_reporter_quando_o_nome_nao_esta_nele(tmp_path):
    mapa = tmp_path / "fontes.csv"
    mapa.write_text("nome,tipo\nReuters,agência\n", encoding="utf-8")
    tabela = pl.DataFrame({"link": ["a", "b", "c"], "autores": [["Reuters"], ["Ana Exemplo", "Beto Exemplo"], None]})
    assert fontes(tabela, mapa)["fonte"].to_list() == ["agência", "repórter", None]
