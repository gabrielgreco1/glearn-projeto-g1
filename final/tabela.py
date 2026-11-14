"""Monta o CSV final: uma linha por notícia, com o que veio do feed e o que veio da página."""

import csv
from pathlib import Path

from acumular import ler_noticias
from baixar import registro
from materias import arquivo_da, ler_materia

CSV = Path("dados/noticias.csv")
COLUNAS = ["publicado", "publicado_pagina", "editoria", "titulo", "subtitulo", "autor", "secao", "palavras", "atualizado_em",
           "origem", "visto_em", "link"]


def montar():
    """Devolve as linhas da tabela, da notícia mais antiga para a mais nova."""
    linhas = []
    for noticia in ler_noticias():
        arquivo = arquivo_da(noticia)
        html = arquivo.read_text(encoding="utf-8") if arquivo.exists() else ""
        pagina = ler_materia(html) if html else {}
        linha = {**noticia, **pagina}
        linha["titulo"] = noticia["titulo"] or pagina.get("titulo_pagina", "")  # o mapa do site não traz título
        linhas.append({coluna: linha.get(coluna, "") for coluna in COLUNAS})
    return linhas  # na ordem em que entraram no noticias.jsonl


def gravar_csv(linhas, destino=CSV):
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=COLUNAS)
        escritor.writeheader()
        escritor.writerows(linhas)
    registro.info("gravei %s linhas em %s", len(linhas), destino)


if __name__ == "__main__":
    gravar_csv(montar())
