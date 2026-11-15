"""A gold: as perguntas do projeto respondidas em SQL, com o DuckDB lendo a silver em Parquet.

Quantas notícias o feed de Tecnologia traz por dia, quantas o g1 escreveu e quantas vieram de fora, e de que tamanho.
A notícia repetida (mesma_que preenchida) e o conteúdo pago não entram nas contas: só são contados à parte."""

from pathlib import Path

import duckdb

from baixar import registro

SILVER = "dados/silver/noticias.parquet"
GOLD = Path("dados/gold")

POR_DIA = f"""
SELECT dia,
       count(*) AS noticias,
       count(*) FILTER (WHERE fonte IN ('redação', 'repórter')) AS do_g1,
       count(*) FILTER (WHERE fonte = 'agência') AS de_fora,
       count(*) FILTER (WHERE fonte IS NULL) AS sem_pagina,
       median(palavras) FILTER (WHERE palavras > 0) AS palavras_mediana
FROM '{SILVER}'
WHERE mesma_que IS NULL AND (fonte IS NULL OR fonte <> 'publicidade')
GROUP BY dia
ORDER BY dia
"""

POR_FONTE = f"""
SELECT coalesce(fonte, 'sem página') AS fonte,
       count(*) AS noticias,
       round(100 * count(*) / sum(count(*)) OVER (), 1) AS porcento,
       median(palavras) FILTER (WHERE palavras > 0) AS palavras_mediana
FROM '{SILVER}'
WHERE mesma_que IS NULL
GROUP BY 1
ORDER BY noticias DESC
"""


def main():
    GOLD.mkdir(parents=True, exist_ok=True)
    for nome, sql in [("por_dia", POR_DIA), ("por_fonte", POR_FONTE)]:
        resultado = duckdb.sql(sql)
        resultado.show()
        resultado.write_parquet(str(GOLD / f"{nome}.parquet"))
        registro.info("gravei %s linhas em %s", len(resultado.fetchall()), GOLD / f"{nome}.parquet")


if __name__ == "__main__":
    main()
