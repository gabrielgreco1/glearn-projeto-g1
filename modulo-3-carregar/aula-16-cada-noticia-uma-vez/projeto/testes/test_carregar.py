"""Testa o que a carga prepara, sem banco: as tuplas que vão para o COPY e o upsert que guarda a primeira vez."""

from datetime import date

import polars as pl

from carregar import COLUNAS, UPSERT, linhas

# Duas notícias com links de exemplo: uma com página e uma do mapa do site, ainda sem título nem palavras.
AMOSTRA = pl.DataFrame({coluna: [None, None] for coluna in COLUNAS}).with_columns(
    pl.Series("link", ["https://g1.globo.com/tecnologia/noticia/a.ghtml", "https://g1.globo.com/tecnologia/noticia/b.ghtml"]),
    pl.Series("dia", [date(2026, 11, 12), date(2026, 11, 2)]),
    pl.Series("titulo", ["Uma notícia com página", None]),
    pl.Series("palavras", [512, None]),
)


def test_vazio_vira_none():
    com_pagina, do_mapa = linhas(AMOSTRA, COLUNAS)
    assert len(com_pagina) == len(COLUNAS)
    assert com_pagina[COLUNAS.index("palavras")] == 512
    assert do_mapa[COLUNAS.index("titulo")] is None
    assert do_mapa[COLUNAS.index("palavras")] is None


def test_upsert_nao_reescreve_a_primeira_vez():
    assert "ON CONFLICT (link)" in UPSERT
    assert "carregada_em" not in UPSERT  # quando a notícia entrou no banco não muda mais
    assert "mudou_em = now()" in UPSERT
