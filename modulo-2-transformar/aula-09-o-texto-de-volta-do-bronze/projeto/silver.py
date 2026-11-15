"""A silver das notícias: uma linha por notícia, com a data no horário de Brasília e o texto medido de novo.

Lê o dados/noticias.csv e as páginas guardadas em dados/bronze/materias. Não faz pedido nenhum ao site."""

import polars as pl

import texto
from baixar import registro
from materias import arquivo_da

CSV = "dados/noticias.csv"
FUSO = "America/Sao_Paulo"
FEED = "%a, %d %b %Y %H:%M:%S %z"  # Sat, 14 Nov 2026 05:01:26 -0000
PAGINA = "%Y-%m-%dT%H:%M:%S%.f%:z"  # 2026-11-14T02:01:26.087-03:00
DIA = "%Y-%m-%d"  # 2026-10-31: nas notícias do mapa do site, o dia do endereço
VISTO = "%Y-%m-%dT%H:%M:%S%:z"  # 2026-11-15T06:03:23+00:00
COLUNAS = ["dia", "publicado_em", "precisao", "editoria", "titulo", "subtitulo", "autor", "palavras",
           "origem", "visto_em", "link"]


def datas(tabela):
    """publicado_em no horário de Brasília, a precisão dele e o dia. A página tem os milissegundos e o fuso; o feed,
    os segundos, em UTC; a notícia do mapa do site sem página só tem o dia do endereço."""
    instante = pl.coalesce(
        pl.col("publicado_pagina").str.to_datetime(PAGINA, strict=False),
        pl.col("publicado").str.to_datetime(FEED, strict=False),
    ).dt.convert_time_zone(FUSO)
    so_o_dia = pl.col("publicado").str.to_date(DIA, strict=False)
    return tabela.with_columns(
        instante.alias("publicado_em"),
        pl.when(instante.is_not_null()).then(pl.lit("hora"))
          .when(so_o_dia.is_not_null()).then(pl.lit("dia")).alias("precisao"),
        pl.coalesce(instante.dt.date(), so_o_dia).alias("dia"),
        pl.col("visto_em").str.to_datetime(VISTO).dt.convert_time_zone(FUSO),
    )


def da_pagina(tabela):
    """Lê de novo cada página guardada: o texto, só com os parágrafos, e as palavras dele.
    A notícia sem página (ainda não baixada, ou fora do ar) fica com as duas colunas vazias."""
    linhas = []
    for link in tabela["link"]:
        arquivo = arquivo_da({"link": link})
        html = arquivo.read_text(encoding="utf-8") if arquivo.exists() else ""
        if not html:
            linhas.append({"link": link, "texto": None, "palavras": None})
            continue
        corpo = " ".join(texto.paragrafos(html))
        linhas.append({"link": link, "texto": corpo, "palavras": texto.contar_palavras(corpo)})
    pagina = pl.DataFrame(linhas, schema={"link": pl.String, "texto": pl.String, "palavras": pl.Int64})
    return tabela.drop("palavras").join(pagina, on="link", how="left")


def montar(caminho=CSV):
    """A silver inteira, a partir do CSV da extração."""
    tabela = da_pagina(datas(pl.read_csv(caminho)))
    return tabela.select(COLUNAS).sort("dia", "publicado_em")


def main():
    tabela = montar()
    registro.info("%s notícias, de %s a %s", tabela.height, tabela["dia"].min(), tabela["dia"].max())
    registro.info("precisão: %s", dict(tabela.group_by("precisao").len().sort("precisao").iter_rows()))
    registro.info("a mais nova: %s", tabela["publicado_em"].max())
    registro.info("palavras: mediana %s (a extração contava %s); sem página: %s", tabela["palavras"].median(),
                  pl.read_csv(CSV)["palavras"].median(), tabela["palavras"].null_count())


if __name__ == "__main__":
    main()
