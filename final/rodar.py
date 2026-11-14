"""Roda o projeto inteiro, na ordem. Pode rodar quantas vezes quiser: só o que é novo entra."""

import acumular
import conferir
import materias
import tabela
from baixar import baixar_feed, registro
from ler import ler_feed


def main():
    registro.info("etapa 1 de 4: o feed")
    feed = baixar_feed()
    registro.info("etapa 2 de 4: guardar só o que é novo")
    if feed:
        acumular.acumular(ler_feed(feed.read_bytes()), "feed")
    registro.info("etapa 3 de 4: a página das notícias que faltam")
    materias.baixar_materias()
    registro.info("etapa 4 de 4: a tabela e a conferência")
    tabela.gravar_csv(tabela.montar())
    conferir.conferir()


if __name__ == "__main__":
    main()
