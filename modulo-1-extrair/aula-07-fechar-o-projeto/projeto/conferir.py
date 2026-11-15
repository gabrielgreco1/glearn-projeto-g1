"""Confere o resultado: nenhuma notícia repetida, nenhum campo obrigatório vazio."""

import csv
from pathlib import Path

from baixar import registro
from tabela import CSV, dia


def conferir(caminho=CSV):
    with Path(caminho).open(encoding="utf-8", newline="") as arquivo:
        linhas = list(csv.DictReader(arquivo))
    links = [linha["link"] for linha in linhas]
    repetidas = len(links) - len(set(links))
    sem_data = sum(1 for linha in linhas if not linha["publicado"])
    sem_titulo = sum(1 for linha in linhas if not linha["titulo"])
    com_pagina = sum(1 for linha in linhas if linha["palavras"] not in ("", "0"))
    registro.info("conferência: %s notícias, %s repetidas, %s sem data, %s sem título, %s com a página lida",
                  len(linhas), repetidas, sem_data, sem_titulo, com_pagina)
    if repetidas or sem_data:
        raise SystemExit("A conferência achou problema. Leia a linha acima.")
    if linhas:
        registro.info("notícias do dia %s ao dia %s", dia(linhas[0]), dia(linhas[-1]))
    return len(linhas)


if __name__ == "__main__":
    conferir()
