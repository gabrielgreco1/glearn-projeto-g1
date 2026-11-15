"""Roda o projeto inteiro, na ordem: extrair, transformar e carregar no Postgres. Pode rodar quantas vezes quiser: só o
que é novo entra, e no banco só muda a notícia que mudou. O banco precisa estar de pé (docker compose up -d --wait)."""

import acumular
import carregar
import conferir
import materias
import tabela
import transformar
from baixar import baixar_feed, registro
from ler import feed_mais_novo, ler_feed


def main():
    registro.info("etapa 1 de 6: o feed")
    baixar_feed()
    registro.info("etapa 2 de 6: guardar só o que é novo")
    # Lê o feed mais novo guardado, mesmo quando o G1 respondeu 304: se a rodada anterior parou antes
    # desta etapa, as notícias dela entram agora. As que já estão guardadas não entram de novo.
    acumular.acumular(ler_feed(feed_mais_novo().read_bytes()), "feed")
    registro.info("etapa 3 de 6: a página das notícias que faltam")
    materias.baixar_materias()
    registro.info("etapa 4 de 6: a tabela e a conferência")
    tabela.gravar_csv(tabela.montar())
    conferir.conferir()
    registro.info("etapa 5 de 6: transformar")
    transformar.main()
    registro.info("etapa 6 de 6: carregar no banco")
    carregar.main()


if __name__ == "__main__":
    main()
