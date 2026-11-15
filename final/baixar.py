"""Pede o feed de Tecnologia do G1 e guarda a resposta em disco, do jeito que veio.

Se o feed não mudou desde o último pedido, o servidor responde 304 e nada é baixado."""

import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

USER_AGENT = os.getenv("G1_USER_AGENT")
if not USER_AGENT:
    raise SystemExit("Falta G1_USER_AGENT no arquivo .env. Copie o .env.example para .env e preencha.")
if "seu-usuario" in USER_AGENT:
    raise SystemExit("O G1_USER_AGENT do .env ainda tem o contato do exemplo (seu-usuario). Troque pelo seu e-mail ou pelo endereço do seu repositório.")

FEED = "https://g1.globo.com/rss/g1/tecnologia/"
CABECALHOS = {"User-Agent": USER_AGENT}
PAUSA = 2.0  # segundos de espera depois de cada pedido
ESTADO = Path("dados/estado.json")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S")
logging.getLogger("httpx").setLevel(logging.WARNING)  # o httpx também registra cada pedido; aqui basta o nosso registro
registro = logging.getLogger("g1")


def agora():
    """O instante atual em UTC, sem os milissegundos. Em UTC, duas coletas se comparam em qualquer computador."""
    return datetime.now(timezone.utc).replace(microsecond=0)


def ler_estado():
    """O que o programa lembra de uma rodada para a outra. Na primeira rodada, nada."""
    if ESTADO.exists():
        return json.loads(ESTADO.read_text(encoding="utf-8"))
    return {}


def gravar_estado(estado):
    ESTADO.parent.mkdir(parents=True, exist_ok=True)
    ESTADO.write_text(json.dumps(estado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def pedir(url, extras=None):
    """Faz um pedido, espera a pausa e devolve a resposta. Para em qualquer status que não seja 200, 304 ou 404."""
    resposta = httpx.get(url, headers={**CABECALHOS, **(extras or {})}, timeout=30)
    time.sleep(PAUSA)
    if resposta.status_code not in (200, 304, 404):
        raise RuntimeError(f"{url} respondeu {resposta.status_code}. Pare e leia a resposta antes de tentar de novo.")
    return resposta


def baixar_feed():
    """Pede o feed. Devolve o caminho do arquivo novo, ou None se o feed não mudou."""
    estado = ler_estado()
    extras = {"If-None-Match": estado["etag"]} if estado.get("etag") else None
    resposta = pedir(FEED, extras)
    if resposta.status_code == 304:
        registro.info("o feed não mudou desde %s, nada para baixar", estado.get("baixado_em"))
        return None
    if resposta.status_code == 404:
        raise RuntimeError(f"o feed não existe mais em {FEED}")
    instante = agora()
    destino = Path("dados/bronze/feed") / f"{instante:%Y-%m-%d}" / f"{instante:%H-%M-%S}.xml"  # bronze: como veio, com a data da coleta em UTC
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(resposta.content)
    gravar_estado({**estado, "etag": resposta.headers.get("etag"), "baixado_em": instante.isoformat()})
    registro.info("baixei o feed: %s bytes em %s", len(resposta.content), destino)
    return destino


if __name__ == "__main__":
    baixar_feed()
