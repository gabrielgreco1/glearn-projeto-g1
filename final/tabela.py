"""Monta o CSV final: uma linha por notícia, com o que veio do feed e o que veio da página."""

import csv
from email.utils import parsedate_to_datetime
from pathlib import Path

from acumular import ler_noticias
from baixar import registro
from materias import arquivo_da, ler_materia
from sitemap import dia_do_endereco

CSV = Path("dados/noticias.csv")
COLUNAS = ["publicado", "publicado_pagina", "editoria", "titulo", "subtitulo", "autor", "secao", "palavras", "atualizado_em",
           "lastmod", "origem", "visto_em", "link"]


def dia(noticia):
    """O dia que ordena a tabela. Vem do endereço da notícia, o dia em Brasília. Alguns endereços do feed não têm data:
    aí vem do publicado do feed, convertido só para ordenar. A coluna publicado continua como veio."""
    do_endereco = dia_do_endereco(noticia["link"])
    if do_endereco or not noticia["publicado"]:
        return do_endereco
    return f"{parsedate_to_datetime(noticia['publicado']):%Y-%m-%d}"


def montar():
    """Devolve as linhas da tabela, do dia mais antigo para o mais novo. Um dia recuperado pelo mapa do site entra
    no fim do noticias.jsonl; na tabela, ele vai para o lugar do dia dele."""
    linhas = []
    for noticia in sorted(ler_noticias(), key=dia):  # no mesmo dia, a ordem em que entraram
        arquivo = arquivo_da(noticia)
        html = arquivo.read_text(encoding="utf-8") if arquivo.exists() else ""
        pagina = ler_materia(html) if html else {}
        linha = {**noticia, **pagina}
        linha["titulo"] = noticia["titulo"] or pagina.get("titulo_pagina", "")  # o mapa do site não traz título
        linhas.append({coluna: linha.get(coluna, "") for coluna in COLUNAS})
    return linhas


def gravar_csv(linhas, destino=CSV):
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=COLUNAS)
        escritor.writeheader()
        escritor.writerows(linhas)
    registro.info("gravei %s linhas em %s", len(linhas), destino)


if __name__ == "__main__":
    gravar_csv(montar())
