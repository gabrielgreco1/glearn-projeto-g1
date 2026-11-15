"""Pede os feeds de Tecnologia e de Economia do G1 e guarda cada resposta em disco, na pasta do seu feed, do jeito que veio.

Se um feed não mudou desde o último pedido dele, o servidor responde 304 e nada é baixado."""

import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

FEEDS = {  # o nome é o da pasta em dados/bronze/feed e o da chave em dados/estado.json
    "tecnologia": "https://g1.globo.com/rss/g1/tecnologia/",
    "economia": "https://g1.globo.com/rss/g1/economia/",
}
FEED = FEEDS["tecnologia"]
PAUSA = 2.0  # segundos de espera depois de cada pedido
ESTADO = Path("dados/estado.json")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S")
logging.getLogger("httpx").setLevel(logging.WARNING)  # o httpx também registra cada pedido; aqui basta o nosso registro
registro = logging.getLogger("g1")
registro.setLevel(logging.INFO)  # o nível fica no nosso registro: o Prefect troca o do logging inteiro para WARNING


def agora():
    """O instante atual em UTC, sem os milissegundos. Em UTC, duas coletas se comparam em qualquer computador."""
    return datetime.now(timezone.utc).replace(microsecond=0)


def cabecalhos():
    """O User-Agent, lido do .env na hora do pedido, e não no import: quem só importa este arquivo, como os testes no
    GitHub, não precisa do .env."""
    contato = os.getenv("G1_USER_AGENT")
    if not contato:
        raise SystemExit("Falta G1_USER_AGENT no arquivo .env. Copie o .env.example para .env e preencha.")
    if "seu-usuario" in contato:
        raise SystemExit("O G1_USER_AGENT do .env ainda tem o contato do exemplo (seu-usuario). Troque pelo seu e-mail ou pelo endereço do seu repositório.")
    return {"User-Agent": contato}


def ler_estado():
    """O que o programa lembra de uma rodada para a outra. Na primeira rodada, nada."""
    if ESTADO.exists():
        return json.loads(ESTADO.read_text(encoding="utf-8"))
    return {}


def gravar_estado(estado):
    ESTADO.parent.mkdir(parents=True, exist_ok=True)
    ESTADO.write_text(json.dumps(estado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def pedir(url, extras=None):
    """Faz um pedido, espera a pausa e devolve a resposta. Um 5xx sobe como erro comum, para ser tentado de novo;
    qualquer outro status que não seja 200, 304 ou 404 para o programa."""
    resposta = httpx.get(url, headers={**cabecalhos(), **(extras or {})}, timeout=30, follow_redirects=True)
    time.sleep(PAUSA)
    if resposta.status_code >= 500:
        # 500, 502, 503: um problema do site, que passa. Um erro comum, e o orquestrador tenta de novo.
        raise RuntimeError(f"{url} respondeu {resposta.status_code}: erro do site, vale tentar de novo")
    if resposta.status_code not in (200, 304, 404):
        # 403, 429: o site disse não. O programa para aqui, sem nova tentativa.
        raise SystemExit(f"{url} respondeu {resposta.status_code}. Pare e leia a resposta antes de tentar de novo.")
    return resposta


def estado_do_feed(feed):
    """O que o programa lembra de um feed só: o etag, quando baixou, a notícia mais nova que viu. Cada feed tem o seu."""
    return ler_estado().get("feeds", {}).get(feed, {})


def gravar_estado_do_feed(feed, **campos):
    """Muda só os campos dados do estado de um feed. O estado dos outros feeds e o resto do arquivo ficam como estão."""
    estado = ler_estado()
    feeds = estado.get("feeds", {})
    gravar_estado({**estado, "feeds": {**feeds, feed: {**feeds.get(feed, {}), **campos}}})


def baixar_feed(feed="tecnologia"):
    """Pede um feed. Devolve o caminho do arquivo novo, ou None se o feed não mudou."""
    url = FEEDS[feed]
    anterior = estado_do_feed(feed)
    extras = {"If-None-Match": anterior["etag"]} if anterior.get("etag") else None
    resposta = pedir(url, extras)
    if resposta.status_code == 304:
        registro.info("o feed de %s não mudou desde %s, nada para baixar", feed, anterior.get("baixado_em"))
        return None
    if resposta.status_code == 404:
        raise RuntimeError(f"o feed de {feed} não existe mais em {url}")
    instante = agora()
    destino = Path("dados/bronze/feed") / feed / f"{instante:%Y-%m-%d}" / f"{instante:%H-%M-%S}.xml"  # bronze: como veio, com a data da coleta em UTC
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(resposta.content)
    gravar_estado_do_feed(feed, etag=resposta.headers.get("etag"), baixado_em=instante.isoformat())
    registro.info("baixei o feed de %s: %s bytes em %s", feed, len(resposta.content), destino)
    return destino


def baixar_feeds():
    """Pede os feeds, um depois do outro (cada pedido já espera a pausa). O estado de cada um é gravado assim que ele
    chega: se um feed falha, o outro não é pedido de novo na próxima tentativa, que ele responde 304."""
    return {feed: baixar_feed(feed) for feed in FEEDS}


if __name__ == "__main__":
    baixar_feeds()
