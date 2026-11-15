"""Baixa a página de cada notícia guardada, poucas por rodada, e lê os dados que o feed não traz. Uma página que a
redação mudou depois de baixada é baixada de novo, pelo mapa do site de hoje e de ontem."""

import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from acumular import ler_noticias
from baixar import pedir, registro
from janela import BRASILIA
from sitemap import NS, partes_do_dia

SITE = "g1.globo.com"  # o programa só pede páginas deste site
PASTA = Path("dados/bronze/materias")
LIMITE = 20  # páginas por rodada, novas ou de novo; o resto fica para a próxima
TOLERANCIA = timedelta(minutes=1)  # o mapa e a página escrevem a mesma mudança com milésimos diferentes


def arquivo_da(noticia):
    """O nome do arquivo sai do caminho do endereço da notícia: a mesma notícia cai sempre no mesmo arquivo.
    'https://g1.globo.com/tecnologia/noticia/2026/11/13/chat-gpt-wallet.ghtml'
    vira 'tecnologia_noticia_2026_11_13_chat-gpt-wallet.html'.
    O endereço vem de fora do programa: no nome só ficam letras, números, hífen e sublinhado."""
    caminho = urlparse(noticia["link"]).path.strip("/").removesuffix(".ghtml").removesuffix(".html")
    nome = re.sub(r"[^A-Za-z0-9_-]", "_", caminho)[:200]  # 200 letras cabem no limite de nome de arquivo dos sistemas
    return PASTA / (nome + ".html")


def mudancas_recentes():
    """A última mudança de cada endereço do mapa do site de hoje e de ontem, em Brasília: {link: lastmod}. Todos os
    endereços, e não só os da editoria: o feed de tecnologia também traz notícias de outras. O mapa de hoje é pedido a
    cada rodada; o de ontem, até ser guardado depois que o dia acabou."""
    hoje = datetime.now(BRASILIA).date()
    lastmod = {}
    for dia in (hoje - timedelta(days=1), hoje):
        for arquivo in partes_do_dia(dia):
            for url in ET.fromstring(arquivo.read_bytes()).findall("sm:url", NS):
                lastmod[url.findtext("sm:loc", namespaces=NS).strip()] = url.findtext("sm:lastmod", default="", namespaces=NS)
    return lastmod


def mudou(noticia, lastmod):
    """A redação mudou a notícia depois que a página foi baixada? Compara o dateModified da página guardada com o
    lastmod do mapa. Notícia fora do mapa, página vazia (a notícia saiu do ar) ou sem dateModified: não."""
    arquivo = arquivo_da(noticia)
    if not lastmod.get(noticia["link"]) or not arquivo.exists() or not arquivo.stat().st_size:
        return False
    guardada = ler_materia(arquivo.read_text(encoding="utf-8"))["atualizado_em"]
    if not guardada:
        return False
    return datetime.fromisoformat(lastmod[noticia["link"]]) - datetime.fromisoformat(guardada) > TOLERANCIA


def gravar(destino, conteudo):
    """Grava num .parcial e só então troca o nome: uma queda no meio não deixa uma página pela metade no lugar da que
    já estava guardada."""
    parcial = destino.with_suffix(".parcial")
    parcial.write_bytes(conteudo)
    parcial.replace(destino)


def baixar_materias():
    """Baixa as páginas que faltam, até o limite da rodada. Se sobra lugar no limite, baixa de novo as que a redação
    mudou depois de baixadas. Devolve quantas baixou."""
    noticias = [noticia for noticia in ler_noticias() if urlparse(noticia["link"]).hostname == SITE]
    faltam = [noticia for noticia in noticias if not arquivo_da(noticia).exists()]
    vez = faltam[-LIMITE:]  # as que entraram por último no arquivo vão primeiro
    if len(vez) < LIMITE:  # com páginas atrasadas, o limite vai todo para elas, e o mapa nem é pedido
        lastmod = mudancas_recentes()
        vez += [noticia for noticia in noticias if mudou(noticia, lastmod)][:LIMITE - len(vez)]
    PASTA.mkdir(parents=True, exist_ok=True)
    baixadas = 0
    for noticia in vez:
        resposta = pedir(noticia["link"])
        if resposta.status_code == 404:
            registro.warning("a notícia saiu do ar: %s", noticia["link"])
            gravar(arquivo_da(noticia), b"")  # arquivo vazio: não pedir de novo
            continue
        gravar(arquivo_da(noticia), resposta.content)
        baixadas += 1
    registro.info("matérias: %s baixadas nesta rodada, %s delas de novo, porque a notícia mudou; %s ficam para a próxima",
                  baixadas, max(0, len(vez) - len(faltam)), max(0, len(faltam) - LIMITE))
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
