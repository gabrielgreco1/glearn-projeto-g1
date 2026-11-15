"""As regras da silver numa tabela escrita à mão: uma notícia boa, uma com o link repetido, uma de outro site
e uma do mapa do site ainda sem página."""

from datetime import date, datetime

import polars as pl

from validar import separar

VISTO = datetime(2026, 11, 15, 3, 3)
TABELA = pl.DataFrame({
    "link": ["https://g1.globo.com/a", "https://g1.globo.com/a", "https://exemplo.invalid/b", "https://g1.globo.com/c"],
    "dia": [date(2026, 11, 14)] * 3 + [date(2026, 11, 2)],
    "publicado_em": [datetime(2026, 11, 14, 2)] * 3 + [None],
    "visto_em": [VISTO] * 4,
    "palavras": [500, 500, 300, None],
    "fonte": ["agência", "agência", "repórter", None],
    "mesma_que": [None, None, None, None],
})


def test_a_conta_fecha_e_o_erro_sai_com_o_motivo():
    validos, rejeitados = separar(TABELA)
    assert validos["link"].to_list() == ["https://g1.globo.com/a", "https://g1.globo.com/c"]
    assert rejeitados.select("regra", "valor").rows() == [("link_unico", "https://g1.globo.com/a"),
                                                          ("link_do_g1", "https://exemplo.invalid/b")]


def test_noticia_sem_pagina_fica_com_aviso():
    validos, _ = separar(TABELA)
    assert validos["avisos"].to_list() == [None, "tem_pagina"]
