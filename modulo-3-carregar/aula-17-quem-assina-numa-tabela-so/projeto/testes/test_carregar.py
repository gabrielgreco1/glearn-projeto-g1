"""Testa o que a carga prepara, sem banco: as tuplas que vão para o COPY, o upsert que guarda a primeira vez e os
nomes que assinam."""

from datetime import date

import polars as pl

from carregar import COLUNAS, UPSERT, assinaturas, autores, linhas

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


def test_assinatura_na_ordem_e_sem_a_noticia_sem_pagina():
    tabela = pl.DataFrame({"link": ["a", "b", "c"], "autores": [["Ana Exemplo", "Beto Exemplo"], None, ["Reuters"]]})
    assert assinaturas(tabela) == [("a", 1, "Ana Exemplo"), ("a", 2, "Beto Exemplo"), ("c", 1, "Reuters")]


def test_cada_nome_uma_vez_com_o_tipo(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # o assinatura.fontes lê o fontes.csv da pasta atual
    (tmp_path / "fontes.csv").write_text("nome,tipo\nReuters,agência\n", encoding="utf-8")
    tabela = pl.DataFrame({"link": ["a", "b"], "autores": [["Reuters", "Ana Exemplo"], ["Reuters"]]})
    assert autores(tabela) == [("Ana Exemplo", "repórter"), ("Reuters", "agência")]


def test_nome_repetido_no_fontes_csv_vale_uma_vez(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "fontes.csv").write_text("nome,tipo\nReuters,repórter\nReuters,agência\n", encoding="utf-8")
    assert autores(pl.DataFrame({"link": ["a"], "autores": [["Reuters"]]})) == [("Reuters", "agência")]
    assert autores(pl.DataFrame({"link": ["b"], "autores": [None]}, schema={"link": pl.String, "autores": pl.List(pl.String)})) == []
