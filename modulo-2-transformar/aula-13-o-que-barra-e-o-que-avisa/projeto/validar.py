"""Confere a silver contra regras escritas e grava as duas saídas: a silver em Parquet e os rejeitados em CSV.

Uma notícia que falha numa regra de erro sai da silver e vai para os rejeitados, com o motivo. Uma notícia que falha
num aviso fica, com o nome do aviso na coluna avisos: muitos avisos se resolvem sozinhos na rodada seguinte."""

from pathlib import Path

import polars as pl

import silver
from baixar import registro

SILVER = Path("dados/silver/noticias.parquet")
REJEITADOS = Path("dados/silver/rejeitados.csv")

REGRAS = [
    {"id": "link_unico", "severidade": "erro", "coluna": "link", "descricao": "cada link aparece uma vez",
     "expr": pl.col("link").is_first_distinct()},
    {"id": "link_do_g1", "severidade": "erro", "coluna": "link", "descricao": "o link é uma página do g1",
     "expr": pl.col("link").str.starts_with("https://g1.globo.com/")},
    {"id": "tem_dia", "severidade": "erro", "coluna": "dia", "descricao": "a notícia tem o dia da publicação",
     "expr": pl.col("dia").is_not_null()},
    {"id": "antes_de_ver", "severidade": "erro", "coluna": "publicado_em",
     "descricao": "publicada antes de o programa ver a notícia",
     "expr": pl.col("publicado_em") <= pl.col("visto_em")},
    {"id": "tem_pagina", "severidade": "aviso", "coluna": "palavras",
     "descricao": "a página foi baixada (o materias.py baixa 20 por rodada)",
     "expr": pl.col("palavras").is_not_null()},
    {"id": "tem_texto", "severidade": "aviso", "coluna": "palavras", "descricao": "a página tem texto",
     "expr": pl.col("palavras") > 0},
    {"id": "nao_e_publicidade", "severidade": "aviso", "coluna": "fonte", "descricao": "não é conteúdo pago",
     "expr": pl.col("fonte") != "publicidade"},
    {"id": "primeira_vez", "severidade": "aviso", "coluna": "mesma_que",
     "descricao": "não repete uma notícia já guardada com outro link",
     "expr": pl.col("mesma_que").is_null()},
]


def separar(tabela, regras=REGRAS):
    """Devolve a silver válida, com a coluna avisos, e os rejeitados, uma linha por falha de erro. Nulo conta como
    passou: uma notícia do mapa do site ainda sem página não tem como falhar na regra antes_de_ver."""
    marcado = tabela.with_columns([r["expr"].fill_null(True).alias(r["id"]) for r in regras])
    erros = [r["id"] for r in regras if r["severidade"] == "erro"]
    avisos = pl.concat_str([pl.when(~pl.col(r["id"])).then(pl.lit(r["id"])) for r in regras if r["severidade"] == "aviso"],
                           separator=",", ignore_nulls=True)
    validos = (marcado.filter(pl.all_horizontal(erros))
               .with_columns(pl.when(avisos != "").then(avisos).alias("avisos"))
               .drop([r["id"] for r in regras]))
    rejeitados = pl.concat([
        marcado.filter(~pl.col(r["id"])).select(
            "link", "dia", pl.lit(r["id"]).alias("regra"), pl.lit(r["descricao"]).alias("motivo"),
            pl.col(r["coluna"]).cast(pl.String).alias("valor"))
        for r in regras if r["severidade"] == "erro"
    ])
    if tabela.height != validos.height + marcado.filter(~pl.all_horizontal(erros)).height:
        raise RuntimeError("a conta não fechou: lidas != válidas + rejeitadas")
    return validos, rejeitados


def gravar(validos, rejeitados):
    SILVER.parent.mkdir(parents=True, exist_ok=True)
    validos.write_parquet(SILVER)
    rejeitados.write_csv(REJEITADOS)
    registro.info("gravei %s notícias em %s e %s rejeições em %s", validos.height, SILVER, rejeitados.height, REJEITADOS)


def main():
    tabela, _ = silver.montar()
    validos, rejeitados = separar(tabela)
    registro.info("lidas %s = válidas %s + rejeitadas %s", tabela.height, validos.height, tabela.height - validos.height)
    for r in REGRAS:
        if r["severidade"] == "aviso":
            n = validos.filter(pl.col("avisos").str.contains(r["id"])).height
            registro.info("  aviso %-18s %s", r["id"], n)
    gravar(validos, rejeitados)


if __name__ == "__main__":
    main()
