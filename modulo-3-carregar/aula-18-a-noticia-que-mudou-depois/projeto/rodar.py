"""Roda o projeto inteiro, na ordem: extrair e transformar. Pode rodar quantas vezes quiser: só o que é novo entra."""

import acumular
import conferir
import materias
import tabela
import transformar
from baixar import baixar_feed, registro
from ler import feed_mais_novo, ler_feed


def main():
    registro.info("etapa 1 de 5: o feed")
    baixar_feed()
    registro.info("etapa 2 de 5: guardar só o que é novo")
    # Lê o feed mais novo guardado, mesmo quando o G1 respondeu 304: se a rodada anterior parou antes
    # desta etapa, as notícias dela entram agora. As que já estão guardadas não entram de novo.
    acumular.acumular(ler_feed(feed_mais_novo().read_bytes()), "feed")
    registro.info("etapa 3 de 5: a página das notícias que faltam")
    materias.baixar_materias()
    registro.info("etapa 4 de 5: a tabela e a conferência")
    tabela.gravar_csv(tabela.montar())
    conferir.conferir()
    registro.info("etapa 5 de 5: transformar")
    transformar.main()


if __name__ == "__main__":
    main()
