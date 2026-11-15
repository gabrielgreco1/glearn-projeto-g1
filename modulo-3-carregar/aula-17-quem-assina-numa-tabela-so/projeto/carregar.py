"""Carrega a silver das notícias no Postgres, cada notícia uma vez, pelo link. A notícia nova entra; a que mudou na
silver é atualizada e guarda quando entrou; a igual fica como está; a que saiu da silver sai do banco. Quem assina vai
para duas tabelas: os nomes, uma vez cada, e as assinaturas, que ligam a notícia aos nomes. Tudo numa transação.
Carregar de novo deixa o banco igual."""

from pathlib import Path

import polars as pl

from assinatura import fontes
from baixar import registro
from banco import conectar, criar_tabelas

SILVER = Path("dados/silver/noticias.parquet")
# As colunas da silver que vão para a tabela noticias, na ordem dela. Quem assina vai para as tabelas autores e assinaturas.
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
AUTORES = """
INSERT INTO autores AS a (nome, tipo)
SELECT nome, tipo FROM chegando_autores ORDER BY nome
ON CONFLICT (nome) DO UPDATE
    SET tipo = EXCLUDED.tipo
    WHERE a.tipo IS DISTINCT FROM EXCLUDED.tipo
RETURNING (xmax = 0) AS novo
"""
# As assinaturas que chegaram, com o id da notícia e o id do nome no lugar do link e do nome.
CHEGARAM = """
SELECT n.id AS noticia_id, c.ordem, a.id AS autor_id
FROM chegando_assinaturas c
JOIN noticias n ON n.link = c.link
JOIN autores a ON a.nome = c.nome
"""
SAIR = f"""
DELETE FROM assinaturas s
WHERE NOT EXISTS (
    SELECT 1 FROM ({CHEGARAM}) c
    WHERE c.noticia_id = s.noticia_id AND c.ordem = s.ordem AND c.autor_id = s.autor_id
)
"""
ENTRAR = f"""
INSERT INTO assinaturas (noticia_id, ordem, autor_id)
{CHEGARAM}
ON CONFLICT (noticia_id, ordem) DO NOTHING
"""


def ler_silver():
    """A silver validada: uma linha por notícia."""
    return pl.read_parquet(SILVER)


def linhas(tabela, colunas):
    """Cada linha vira uma tupla, na ordem das colunas. O vazio do Polars chega como None, que o Postgres grava como NULL."""
    return tabela.select(colunas).rows()


def assinaturas(tabela):
    """Uma tupla por nome assinado: (link, ordem, nome), com a ordem da linha "Por ...", a partir de 1.
    A notícia sem página não tem assinatura e não entra."""
    return [(link, ordem, nome)
            for link, nomes in tabela.select("link", "autores").rows()
            for ordem, nome in enumerate(nomes or [], start=1)]


def autores(tabela):
    """Cada nome que assina alguma notícia, uma vez, com o tipo: (nome, tipo). O tipo sai do assinatura.fontes, a mesma
    regra da coluna fonte da silver, aplicada a cada nome, e não só ao primeiro. Um nome escrito duas vezes no
    fontes.csv fica uma vez só, com o tipo da última linha: o upsert não aceita o mesmo nome duas vezes na carga."""
    nomes = sorted({nome for _, _, nome in assinaturas(tabela)})
    cada_um = pl.DataFrame({"autores": [[nome] for nome in nomes]}, schema={"autores": pl.List(pl.String)})
    tipos = dict(fontes(cada_um).select(pl.col("autores").list.first(), "fonte").rows())  # um nome, um tipo
    return sorted(tipos.items())


def copiar(cursor, destino, colunas, tuplas):
    """Grava as tuplas na tabela destino com COPY, na ordem das colunas."""
    with cursor.copy(f"COPY {destino} ({', '.join(colunas)}) FROM STDIN") as copia:
        for linha in tuplas:
            copia.write_row(linha)


def carregar_noticias(conexao, tabela):
    """COPY para uma tabela temporária e, de lá, um upsert pelo link. Devolve quantas notícias entraram, quantas
    mudaram e quantas ficaram iguais."""
    conexao.execute(CHEGANDO)
    with conexao.cursor() as cursor:
        copiar(cursor, "chegando", COLUNAS, linhas(tabela, COLUNAS))
        tocadas = cursor.execute(UPSERT).fetchall()
    novas = sum(1 for (nova,) in tocadas if nova)
    return novas, len(tocadas) - novas, tabela.height - len(tocadas)


def tirar_as_que_sairam(conexao):
    """Apaga a notícia que está no banco e não está mais na silver. Devolve quantas saíram."""
    return conexao.execute(FORA_DA_SILVER).rowcount


def carregar_assinaturas(conexao, tabela):
    """Primeiro os nomes, com upsert pelo nome, porque a assinatura aponta para eles. Depois as assinaturas: sai a que
    a silver não tem mais, entra a que falta. Devolve os nomes novos, os que mudaram de tipo, as assinaturas que
    saíram e as que entraram."""
    conexao.execute("CREATE TEMP TABLE chegando_autores (nome text, tipo text) ON COMMIT DROP")
    conexao.execute("CREATE TEMP TABLE chegando_assinaturas (link text, ordem smallint, nome text) ON COMMIT DROP")
    with conexao.cursor() as cursor:
        copiar(cursor, "chegando_autores", ["nome", "tipo"], autores(tabela))
        copiar(cursor, "chegando_assinaturas", ["link", "ordem", "nome"], assinaturas(tabela))
        tocados = cursor.execute(AUTORES).fetchall()
        sairam = cursor.execute(SAIR).rowcount
        entraram = cursor.execute(ENTRAR).rowcount
    novos = sum(1 for (novo,) in tocados if novo)
    return novos, len(tocados) - novos, sairam, entraram


def main():
    tabela = ler_silver()
    with conectar() as conexao:  # uma transação só: notícias, nomes e assinaturas mudam juntos, ou nada muda
        criar_tabelas(conexao)
        novas, mudaram, iguais = carregar_noticias(conexao, tabela)
        nomes_novos, nomes_mudaram, assinaturas_sairam, assinaturas_entraram = carregar_assinaturas(conexao, tabela)
        sairam = tirar_as_que_sairam(conexao)  # depois das assinaturas: a chave estrangeira recusa apagar antes
    registro.info("notícias: %s na silver; novas %s, mudaram %s, iguais %s; saíram do banco %s",
                  tabela.height, novas, mudaram, iguais, sairam)
    registro.info("nomes: %s novos, %s mudaram de tipo; assinaturas: %s saíram, %s entraram",
                  nomes_novos, nomes_mudaram, assinaturas_sairam, assinaturas_entraram)


if __name__ == "__main__":
    main()
