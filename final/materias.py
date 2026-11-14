"""Baixa a página de cada notícia guardada, poucas por rodada, e lê os dados que o feed não traz."""

import re
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from acumular import ler_noticias
from baixar import pedir, registro

SITE = "g1.globo.com"  # o programa só pede páginas deste site
PASTA = Path("dados/bronze/materias")
LIMITE = 20  # páginas novas por rodada; o resto fica para a próxima


def arquivo_da(noticia):
    """O nome do arquivo sai do caminho do endereço da notícia: a mesma notícia cai sempre no mesmo arquivo.
    'https://g1.globo.com/tecnologia/noticia/2026/11/13/chat-gpt-wallet.ghtml'
    vira 'tecnologia_noticia_2026_11_13_chat-gpt-wallet.html'.
    O endereço vem de fora do programa: no nome só ficam letras, números, hífen e sublinhado."""
    caminho = urlparse(noticia["link"]).path.strip("/").removesuffix(".ghtml").removesuffix(".html")
    nome = re.sub(r"[^A-Za-z0-9_-]", "_", caminho)[:200]  # 200 letras cabem no limite de nome de arquivo dos sistemas
    return PASTA / (nome + ".html")


def baixar_materias():
    """Baixa as páginas que faltam, até o limite da rodada. Devolve quantas baixou."""
    faltam = [noticia for noticia in ler_noticias()
              if urlparse(noticia["link"]).hostname == SITE and not arquivo_da(noticia).exists()]
    PASTA.mkdir(parents=True, exist_ok=True)
    baixadas = 0
    for noticia in faltam[-LIMITE:]:  # as que entraram por último no arquivo vão primeiro
        resposta = pedir(noticia["link"])
        if resposta.status_code == 404:
            registro.warning("a notícia saiu do ar: %s", noticia["link"])
            arquivo_da(noticia).write_text("", encoding="utf-8")  # arquivo vazio: não pedir de novo
            continue
        arquivo_da(noticia).write_bytes(resposta.content)
        baixadas += 1
    registro.info("matérias: %s baixadas nesta rodada, %s ficam para a próxima", baixadas, max(0, len(faltam) - LIMITE))
    return baixadas


def conteudo(pagina, seletor):
    """O atributo content da primeira marca que casa com o seletor, ou vazio."""
    marca = pagina.select_one(seletor)
    return marca.get("content", "").strip() if marca else ""


def ler_materia(html):
    """Lê da página os dados feitos para programas: título, datas, autor, editoria e o tamanho do texto."""
    pagina = BeautifulSoup(html, "html.parser")
    corpo = pagina.select_one('[itemprop="articleBody"]')
    secoes = [marca.get("content", "") for marca in pagina.select('meta[property="article:section"]')]
    return {
        "titulo_pagina": conteudo(pagina, 'meta[property="og:title"]').removesuffix(" | G1"),
        "publicado_pagina": conteudo(pagina, 'head meta[itemprop="datePublished"]'),  # as dos vídeos ficam no corpo
        "atualizado_em": conteudo(pagina, 'head meta[itemprop="dateModified"]'),
        "autor": conteudo(pagina, '[itemprop="author"] meta[itemprop="name"]'),
        "secao": secoes[-1] if secoes else "",
        "palavras": len(corpo.get_text(" ").split()) if corpo else 0,
    }


if __name__ == "__main__":
    baixar_materias()
