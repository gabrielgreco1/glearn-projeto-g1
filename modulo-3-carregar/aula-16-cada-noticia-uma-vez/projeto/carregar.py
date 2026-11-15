"""Carrega a silver das notícias no Postgres, cada notícia uma vez, pelo link. A notícia nova entra; a que mudou na
silver é atualizada e guarda quando entrou; a igual fica como está; a que saiu da silver sai do banco. Tudo numa
transação. Carregar de novo deixa o banco igual."""

from pathlib import Path

import polars as pl

from baixar import registro
from banco import conectar, criar_tabelas

SILVER = Path("dados/silver/noticias.parquet")
# As colunas da silver que vão para a tabela noticias, na ordem dela. Quem assina vai para outras tabelas (aula 17).
COLUNAS = ["link", "dia", "publicado_em", "precisao", "editoria", "titulo", "subtitulo", "palavras", "mesma_que",
           "origem", "visto_em", "avisos"]
DADOS = COLUNAS[1:]  # tudo menos o link, que é a chave

CHEGANDO = f"CREATE TEMP TABLE chegando ON COMMIT DROP AS SELECT {', '.join(COLUNAS)} FROM noticias WITH NO DATA"
UPSERT = f"""
INSERT INTO noticias AS n ({", ".join(COLUNAS)})
SELECT {", ".join(COLUNAS)} FROM chegando ORDER BY link
ON CONFLICT (link) DO UPDATE
    SET {", ".join(f"{coluna} = EXCLUDED.{coluna}" for coluna in DADOS)}, mudou_em = now()
    WHERE ({", ".join(f"n.{coluna}" for coluna in DADOS)}) IS DISTINCT FROM ({", ".join(f"EXCLUDED.{coluna}" for coluna in DADOS)})
RETURNING (xmax = 0) AS nova
"""
FORA_DA_SILVER = "DELETE FROM noticias n WHERE NOT EXISTS (SELECT 1 FROM chegando c WHERE c.link = n.link)"


def ler_silver():
    """A silver validada: uma linha por notícia."""
    return pl.read_parquet(SILVER)


def linhas(tabela, colunas):
    """Cada linha vira uma tupla, na ordem das colunas. O vazio do Polars chega como None, que o Postgres grava como NULL."""
    return tabela.select(colunas).rows()


def carregar_noticias(conexao, tabela):
    """COPY para uma tabela temporária e, de lá, um upsert pelo link. Devolve quantas notícias entraram, quantas
    mudaram e quantas ficaram iguais."""
    conexao.execute(CHEGANDO)
    with conexao.cursor() as cursor:
        with cursor.copy(f"COPY chegando ({', '.join(COLUNAS)}) FROM STDIN") as copia:
            for linha in linhas(tabela, COLUNAS):
                copia.write_row(linha)
        tocadas = cursor.execute(UPSERT).fetchall()
    novas = sum(1 for (nova,) in tocadas if nova)
    return novas, len(tocadas) - novas, tabela.height - len(tocadas)


def tirar_as_que_sairam(conexao):
    """Apaga a notícia que está no banco e não está mais na silver. Devolve quantas saíram."""
    return conexao.execute(FORA_DA_SILVER).rowcount


def main():
    tabela = ler_silver()
    with conectar() as conexao:  # uma transação só: a carga inteira entra, ou nada entra
        criar_tabelas(conexao)
        novas, mudaram, iguais = carregar_noticias(conexao, tabela)
        sairam = tirar_as_que_sairam(conexao)
    registro.info("notícias: %s na silver; novas %s, mudaram %s, iguais %s; saíram do banco %s",
                  tabela.height, novas, mudaram, iguais, sairam)


if __name__ == "__main__":
    main()
