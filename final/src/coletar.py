"""Etapa 1: baixa a lista de notícias da editoria Tecnologia e cada matéria, e guarda tudo em bronze, como veio.

Uso:
    uv run python src/coletar.py

Limites: no máximo 3 páginas de lista e 30 matérias no total (ver README).
Rodar de novo no mesmo dia não baixa o que já está em bronze.
"""

import sys

from comum import (
    SITE,
    Bloqueio,
    carregar_permissoes,
    gravar_bronze,
    nome_estavel,
    pasta_bronze,
    pedir,
    pode_baixar,
    registro,
)
from extrair import ler_lista

SECAO = f"{SITE}/tecnologia/"
MAXIMO_PAGINAS = 3
MAXIMO_MATERIAS = 30


def url_da_pagina_de_lista(numero: int) -> str:
    """A página 1 é a própria editoria. As seguintes vêm do feed: .../index/feed/pagina-N.ghtml."""
    if numero == 1:
        return SECAO
    return f"{SECAO}index/feed/pagina-{numero}.ghtml"


def coletar_listas(pasta, permissoes) -> list:
    """Baixa até MAXIMO_PAGINAS páginas de lista. Devolve os caminhos dos arquivos em bronze."""
    arquivos = []
    for numero in range(1, MAXIMO_PAGINAS + 1):
        url = url_da_pagina_de_lista(numero)
        nome = f"lista-pagina-{numero}.html"
        destino = pasta / nome
        if destino.exists():
            registro.info("%s já está em bronze, não baixo de novo", nome)
            arquivos.append(destino)
            continue
        if not pode_baixar(permissoes, url):
            registro.warning("robots.txt proíbe %s; paro a lista aqui", url)
            break
        resposta = pedir(url)
        if resposta is None or resposta.status_code != 200:
            registro.warning("não consegui a página %s; paro a lista aqui", numero)
            break
        arquivos.append(gravar_bronze(resposta, nome, pasta))
        registro.info("%s baixado (%s bytes)", nome, len(resposta.content))
    return arquivos


def juntar_links(arquivos_de_lista) -> list[str]:
    """Junta os links das matérias de todas as listas, sem repetir, e corta em MAXIMO_MATERIAS."""
    vistos, links = set(), []
    for arquivo in arquivos_de_lista:
        for link in ler_lista(arquivo.read_text(encoding="utf-8")):
            if link not in vistos:
                vistos.add(link)
                links.append(link)
    return links[:MAXIMO_MATERIAS]


def coletar_materias(pasta, links, permissoes) -> None:
    """Baixa cada matéria que ainda não está em bronze. O nome do arquivo sai da URL."""
    baixadas, ja_existiam = 0, 0
    for link in links:
        nome = nome_estavel(link)
        if (pasta / nome).exists():
            ja_existiam += 1
            continue
        if not pode_baixar(permissoes, link):
            registro.warning("robots.txt ou lista de proibidos bloqueia %s; pulo", link)
            continue
        resposta = pedir(link)
        if resposta is None or resposta.status_code != 200:
            registro.warning("matéria não baixada: %s", link)
            continue
        gravar_bronze(resposta, nome, pasta)
        baixadas += 1
        registro.info("matéria %s/%s gravada: %s", baixadas + ja_existiam, len(links), nome)
    registro.info("matérias novas: %s; já existiam: %s", baixadas, ja_existiam)


def main():
    pasta = pasta_bronze()
    try:
        permissoes = carregar_permissoes(pasta)
        listas = coletar_listas(pasta, permissoes)
        links = juntar_links(listas)
        registro.info("%s páginas de lista e %s links de matérias encontrados", len(listas), len(links))
        coletar_materias(pasta, links, permissoes)
    except Bloqueio as erro:
        registro.error("%s", erro)
        sys.exit(1)


if __name__ == "__main__":
    main()
