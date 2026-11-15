"""O texto de cada notícia, lido de novo da página guardada, sem pedir nada ao site.

Só os parágrafos do texto entram: legenda de foto, título de vídeo, anúncio e cartão de oferta ficam de fora.
As frases que o G1 repete em muitas páginas (o boilerplate) saem pela lista do boilerplate.txt."""

import re
import unicodedata
from collections import Counter
from pathlib import Path

from bs4 import BeautifulSoup

from acumular import ler_noticias
from baixar import registro
from materias import arquivo_da

BOILERPLATE = Path("boilerplate.txt")
MINIMO = 3  # uma frase que aparece em 3 páginas ou mais vira candidata a boilerplate


def espacos(texto):
    """Um espaço só entre as palavras, nenhum nas pontas nem antes de vírgula e ponto, e os acentos na forma
    composta (NFC). 'Jensen Huang , a vice' vira 'Jensen Huang, a vice'."""
    junto = " ".join(unicodedata.normalize("NFC", texto).split())
    return re.sub(r" ([,.;:!?)])", r"\1", junto)


def paragrafos(html):
    """Os parágrafos do texto da notícia, na ordem da página. Uma página sem texto devolve a lista vazia."""
    pagina = BeautifulSoup(html, "html.parser")
    achados = [espacos(p.get_text(" ")) for p in pagina.select('[itemprop="articleBody"] p.content-text__container')]
    return [p for p in achados if p]


def contar_palavras(corpo):
    """Os pedaços separados por espaço que têm ao menos uma letra ou um número. Emoji e travessão sozinhos não contam."""
    return sum(1 for pedaco in corpo.split() if re.search(r"\w", pedaco))


def chave(paragrafo):
    """A forma de comparar duas frases: sem emoji nem pontuação, em minúsculas, um espaço entre as palavras.
    '🗒️Tem alguma sugestão de reportagem? Mande para o g1' vira 'tem alguma sugestão de reportagem mande para o g1'."""
    return " ".join(re.sub(r"[^\w\s]", " ", unicodedata.normalize("NFKC", paragrafo)).casefold().split())


def ler_boilerplate(caminho=BOILERPLATE):
    """As chaves das frases que você conferiu e decidiu tirar, uma por linha. Sem o arquivo, nenhuma."""
    if not Path(caminho).exists():
        return set()
    linhas = Path(caminho).read_text(encoding="utf-8").splitlines()
    return {chave(linha) for linha in linhas if linha.strip()}


def sem_boilerplate(lista, fixos):
    """Os parágrafos cuja chave não está na lista do boilerplate."""
    return [p for p in lista if chave(p) not in fixos]


def candidatos(paginas, minimo=MINIMO):
    """Conta em quantas páginas cada frase aparece (pela chave) e devolve as que aparecem em `minimo` páginas ou mais,
    da mais frequente para a menos (no empate, em ordem alfabética). Cada página conta uma vez, mesmo que repita a frase."""
    contagem = Counter(c for lista in paginas for c in {chave(p) for p in lista})
    return sorted([(c, n) for c, n in contagem.items() if n >= minimo], key=lambda par: (-par[1], par[0]))


def paginas_guardadas():
    """Os parágrafos de cada página guardada. Página que não foi baixada, ou que saiu do ar, fica de fora."""
    for noticia in ler_noticias():
        arquivo = arquivo_da(noticia)
        if arquivo.exists() and arquivo.stat().st_size:
            yield paragrafos(arquivo.read_text(encoding="utf-8"))


def main():
    paginas = list(paginas_guardadas())
    fixos = ler_boilerplate()
    registro.info("%s páginas lidas; frases em %s páginas ou mais:", len(paginas), MINIMO)
    for frase, n in candidatos(paginas):
        registro.info("  %3s  %s %s", n, "[tira]" if frase in fixos else "[fica]", frase[:80])


if __name__ == "__main__":
    main()
