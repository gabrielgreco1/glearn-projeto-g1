"""Quem assina cada notícia, lido da linha "Por ..." da página guardada, e de que tipo é a fonte.

A marca author da página diz "G1" também nas notícias da Reuters, da France Presse e da BBC. A assinatura visível
diz quem escreveu. O fontes.csv diz o tipo de cada nome que não é de um repórter: redação, agência ou publicidade."""

import polars as pl
from bs4 import BeautifulSoup

from acumular import ler_noticias
from baixar import registro
from materias import arquivo_da
from texto import espacos

FONTES = "fontes.csv"


def autores(html):
    """Os nomes da assinatura, na ordem da página, ou None se a página não tem assinatura.
    O atributo title da linha "Por ..." tem só os nomes: 'Darlan Helder, Lígia Vieira' vira ['Darlan Helder', 'Lígia Vieira']."""
    marca = BeautifulSoup(html, "html.parser").select_one(".content-publication-data__from")
    nomes = [espacos(nome) for nome in marca.get("title", "").split(",")] if marca else []
    return [nome for nome in nomes if nome] or None


def fontes(tabela, caminho=FONTES):
    """Acrescenta a coluna fonte, pelo primeiro nome da assinatura: o tipo que o fontes.csv dá a ele, ou repórter,
    se o nome não está lá. Sem assinatura (a página não foi baixada), a fonte fica vazia."""
    mapa = pl.read_csv(caminho).rename({"nome": "primeiro", "tipo": "fonte"})
    return (tabela.with_columns(pl.col("autores").list.first().alias("primeiro"))
            .join(mapa, on="primeiro", how="left")
            .with_columns(pl.when(pl.col("primeiro").is_not_null()).then(pl.col("fonte").fill_null("repórter")))
            .drop("primeiro"))


def main():
    linhas = []
    for noticia in ler_noticias():
        arquivo = arquivo_da(noticia)
        if arquivo.exists() and arquivo.stat().st_size:
            linhas.append({"link": noticia["link"], "autores": autores(arquivo.read_text(encoding="utf-8"))})
    tabela = fontes(pl.DataFrame(linhas, schema={"link": pl.String, "autores": pl.List(pl.String)}))
    registro.info("%s páginas lidas", tabela.height)
    contagem = tabela.group_by("fonte").len().sort("len", descending=True)
    for fonte, n in contagem.iter_rows():
        registro.info("  %-12s %s", fonte, n)
    reporteres = tabela.filter(pl.col("fonte") == "repórter")["autores"].list.first().unique().sort().to_list()
    registro.info("contados como repórter (confira se algum é agência): %s", ", ".join(reporteres))


if __name__ == "__main__":
    main()
