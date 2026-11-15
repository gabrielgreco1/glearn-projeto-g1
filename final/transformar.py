"""A etapa Transformar inteira, sobre o que já está em dados/: a silver conferida pelas regras e a gold.

Não faz pedido nenhum ao site. Pode rodar quantas vezes quiser: cada rodada refaz a silver e a gold do zero."""

import polars as pl

import gold
import repetidas
import silver
import validar
from baixar import registro


def main():
    registro.info("transformar 1 de 3: a silver")
    tabela, achados = silver.montar()
    para_ler = achados.filter(pl.col("nota") < repetidas.LIMIAR).height
    registro.info("%s notícias; %s repetidas; %s pares para você ler (uv run python silver.py mostra)",
                  tabela.height, tabela["mesma_que"].is_not_null().sum(), para_ler)
    registro.info("transformar 2 de 3: as regras")
    validos, rejeitados = validar.separar(tabela)
    registro.info("lidas %s = válidas %s + rejeitadas %s", tabela.height, validos.height, tabela.height - validos.height)
    validar.gravar(validos, rejeitados)
    registro.info("transformar 3 de 3: a gold")
    gold.main()


if __name__ == "__main__":
    main()
