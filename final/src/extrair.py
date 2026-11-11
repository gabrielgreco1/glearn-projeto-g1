"""Etapa 2: lê o bronze e gera a tabela de matérias em CSV, na camada silver.

Uso:
    uv run python src/extrair.py

Ordem de preferência para cada campo:
1. dados estruturados da página: metatags og:, article:section, microdados itemprop e JSON-LD;
2. seletores de HTML (h1, h2 de subtítulo, texto do corpo), só quando o estruturado não existe.
Campo que a página não tem fica vazio. Nada é inventado.
O CSV não guarda o texto da matéria, só a quantidade de palavras.
"""

import csv
import json
import re
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from comum import DADOS, SITE, registro, ultimo_bronze

COLUNAS = ["url", "titulo", "subtitulo", "publicado_em", "autor", "editoria", "n_palavras"]
# Matéria do G1 tem /noticia/AAAA/MM/DD/ no caminho. Páginas institucionais e vídeos não têm.
PADRAO_MATERIA = re.compile(r"^https://g1\.globo\.com/[a-z0-9/-]+/noticia/\d{4}/\d{2}/\d{2}/[^/]+\.ghtml$")


def texto(elemento) -> str:
    """O texto de um elemento, com espaços limpos. Elemento vazio vira ''."""
    if elemento is None:
        return ""
    return elemento.get_text(" ", strip=True)


def ler_lista(html: str) -> list[str]:
    """Acha, na página de lista, os links das matérias. Sem repetir, na ordem em que aparecem."""
    sopa = BeautifulSoup(html, "html.parser")
    links = []
    for ancora in sopa.select("a[href]"):
        endereco = urljoin(SITE, ancora["href"]).split("#")[0].split("?")[0]
        if PADRAO_MATERIA.match(endereco) and endereco not in links:
            links.append(endereco)
    return links


def _dados_ld_json(sopa) -> list[dict]:
    """Todos os blocos JSON-LD da página, já lidos. Bloco quebrado é ignorado."""
    dados = []
    for bloco in sopa.find_all("script", type="application/ld+json"):
        try:
            conteudo = json.loads(bloco.string or bloco.get_text())
        except json.JSONDecodeError:
            continue
        dados.extend(conteudo if isinstance(conteudo, list) else [conteudo])
    return [d for d in dados if isinstance(d, dict)]


def _titulo(sopa) -> str:
    og = sopa.find("meta", attrs={"property": "og:title"})
    if og and og.get("content"):
        return re.sub(r"\s*\|\s*G1\s*$", "", og["content"]).strip()
    return texto(sopa.find("h1", attrs={"itemprop": "headline"}) or sopa.find("h1"))


def _publicado_em(sopa) -> str:
    """Data no formato ISO 8601 com fuso. Sem fuso na página, devolve vazio."""
    marca = sopa.find("meta", attrs={"itemprop": "datePublished"})
    valor = marca.get("content") if marca else None
    if not valor:
        tempo = sopa.find("time", attrs={"itemprop": "datePublished"})
        valor = tempo.get("datetime") if tempo else None
    if not valor:
        return ""
    try:
        momento = datetime.fromisoformat(valor)
    except ValueError:
        return ""
    if momento.tzinfo is None:
        return ""
    return momento.isoformat(timespec="seconds")


def _autor(sopa) -> str:
    bloco = sopa.find(attrs={"itemprop": "author"})
    if bloco is None:
        return ""
    nome = bloco.find("meta", attrs={"itemprop": "name"})
    if nome is not None:
        return (nome.get("content") or "").strip()
    return texto(bloco)


def _editoria(sopa, ld: list[dict]) -> str:
    """A última seção da lista: em ['G1', 'Tecnologia'] o valor é 'Tecnologia'."""
    for dado in ld:
        secao = dado.get("articleSection")
        if isinstance(secao, list) and secao:
            return str(secao[-1])
        if isinstance(secao, str) and secao:
            return secao
    secoes = [m.get("content") for m in sopa.find_all("meta", attrs={"property": "article:section"})]
    return secoes[-1] if secoes and secoes[-1] else ""


def ler_materia(html: str, url: str) -> dict:
    """Lê uma matéria e devolve uma linha com os campos da tabela. Campo ausente fica vazio."""
    sopa = BeautifulSoup(html, "html.parser")
    ld = _dados_ld_json(sopa)
    corpo = sopa.find(attrs={"itemprop": "articleBody"})
    subtitulo = sopa.find("h2", attrs={"itemprop": "alternativeHeadline"})
    return {
        "url": url,
        "titulo": _titulo(sopa),
        "subtitulo": texto(subtitulo),
        "publicado_em": _publicado_em(sopa),
        "autor": _autor(sopa),
        "editoria": _editoria(sopa, ld),
        "n_palavras": len(texto(corpo).split()) if corpo is not None else "",
    }


def main():
    pasta = ultimo_bronze()
    linhas = []
    for arquivo in sorted(pasta.glob("materia-*.html")):
        origem = json.loads((pasta / f"{arquivo.name}.origem.json").read_text(encoding="utf-8"))
        if origem["status"] != 200:
            continue
        html = arquivo.read_text(encoding="utf-8")
        linhas.append(ler_materia(html, origem["url"]))
    destino = DADOS / "silver" / "noticias.csv"
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=COLUNAS)
        escritor.writeheader()
        escritor.writerows(linhas)
    registro.info("%s matérias gravadas em %s (bronze: %s)", len(linhas), destino, pasta.name)


if __name__ == "__main__":
    main()
