"""Junta as notícias de cada rodada num arquivo só, sem repetir nenhuma."""

import json
from pathlib import Path

from baixar import agora, registro
from ler import feed_mais_novo, ler_feed

ARQUIVO = Path("dados/noticias.jsonl")


def ler_noticias():
    """Todas as notícias já guardadas, na ordem em que foram guardadas."""
    if not ARQUIVO.exists():
        return []
    with ARQUIVO.open(encoding="utf-8") as arquivo:
        return [json.loads(linha) for linha in arquivo if linha.strip()]


def acumular(noticias, origem):
    """Acrescenta ao arquivo só as notícias que ainda não estão nele. Devolve as que entraram."""
    vistas = {noticia["id"] for noticia in ler_noticias()}
    novas = [noticia for noticia in noticias if noticia["id"] not in vistas]
    novas.reverse()  # o feed vem da mais nova para a mais antiga; cada rodada entra na ordem do tempo
    visto_em = agora().isoformat()
    ARQUIVO.parent.mkdir(parents=True, exist_ok=True)
    with ARQUIVO.open("a", encoding="utf-8") as arquivo:
        for noticia in novas:
            arquivo.write(json.dumps({**noticia, "origem": origem, "visto_em": visto_em}, ensure_ascii=False) + "\n")
    registro.info("%s: %s notícias lidas, %s novas, %s já estavam guardadas. Total: %s",
                  origem, len(noticias), len(novas), len(noticias) - len(novas), len(vistas) + len(novas))
    return novas


if __name__ == "__main__":
    acumular(ler_feed(feed_mais_novo().read_bytes()), "feed")
