"""Acha a mesma notícia publicada duas vezes, com endereços diferentes: o texto quase igual, em dias próximos.

Nada é apagado. A notícia mais nova de um par ganha, na coluna mesma_que, o link da mais antiga."""

from itertools import combinations

import polars as pl
from rapidfuzz import fuzz, utils

JANELA = 3  # dias: só compara notícias publicadas com até 3 dias de distância (o bloco)
REVISAR = 80  # a partir desta nota, o par aparece para você ler
LIMIAR = 90  # a partir desta nota, é a mesma notícia


def pares(tabela):
    """Compara o texto de cada par de notícias do mesmo bloco e devolve os pares com nota a partir de REVISAR,
    da maior nota para a menor. Em cada par, a antiga é a publicada primeiro."""
    noticias = (tabela.filter(pl.col("palavras") > 0).sort("publicado_em", nulls_last=True)
                .select("link", "dia", "texto").to_dicts())
    achados = []
    for antiga, nova in combinations(noticias, 2):
        if abs((nova["dia"] - antiga["dia"]).days) > JANELA:
            continue  # fora do bloco: nem compara
        nota = fuzz.ratio(antiga["texto"], nova["texto"], processor=utils.default_process)
        if nota >= REVISAR:
            achados.append({"antiga": antiga["link"], "nova": nova["link"], "nota": round(nota, 1)})
    return pl.DataFrame(achados, schema={"antiga": pl.String, "nova": pl.String, "nota": pl.Float64}).sort("nota", descending=True)


def marcar(tabela, achados):
    """Acrescenta a coluna mesma_que: na notícia mais nova de um par com nota a partir do LIMIAR, o link da mais antiga
    (a de nota maior, se houver mais de uma). Nas outras notícias, vazio."""
    iguais = (achados.filter(pl.col("nota") >= LIMIAR)
              .group_by("nova", maintain_order=True).agg(pl.col("antiga").first().alias("mesma_que"))
              .rename({"nova": "link"}))
    return tabela.join(iguais, on="link", how="left")
