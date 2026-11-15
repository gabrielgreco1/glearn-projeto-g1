"""A gold sobre uma silver escrita à mão, numa pasta temporária: a repetida e a publicidade ficam fora da conta do dia."""

from datetime import date

import duckdb
import polars as pl

import gold


def test_por_dia_conta_sem_a_repetida_e_sem_a_publicidade(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # o gold.py lê e grava em dados/, relativo à pasta atual
    (tmp_path / "dados/silver").mkdir(parents=True)
    pl.DataFrame({
        "dia": [date(2026, 11, 12)] * 4,
        "fonte": ["repórter", "agência", "agência", "publicidade"],
        "palavras": [400, 600, 600, 500],
        "mesma_que": [None, None, "https://g1.globo.com/a", None],
    }).write_parquet("dados/silver/noticias.parquet")
    gold.main()
    linha = duckdb.sql("SELECT * FROM 'dados/gold/por_dia.parquet'").fetchall()[0]
    assert linha == (date(2026, 11, 12), 2, 1, 1, 0, 500.0)
