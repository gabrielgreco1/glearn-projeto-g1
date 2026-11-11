"""Peças usadas por todas as etapas: configuração, robots.txt, pedido ao site e gravação em bronze."""

import hashlib
import json
import logging
import os
import time
import urllib.robotparser
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "dados"
SITE = "https://g1.globo.com"
USER_AGENT = os.getenv("G1_USER_AGENT", "projeto-de-estudo/0.1 (preencha o .env)")
PAUSA = max(1.0, float(os.getenv("G1_PAUSA", "1")))  # nunca menos de 1 segundo entre pedidos
TENTATIVAS_EXTRAS = 3  # em 429 ou 5xx: espera e tenta de novo no máximo 3 vezes
ESPERA_INICIAL = 2  # segundos; dobra a cada nova tentativa

# Caminhos que o robots.txt do G1 proíbe e que este projeto nunca toca.
# Lista copiada do robots.txt em 2026-11-11 (ver README). Serve de segunda barreira.
PROIBIDOS = (
    "/jornalismo/g1/",
    "/_ssi/",
    "/beta/",
    "/componentes/",
    "/busca/",
    "/zeta/",
    "/content-aggregator/",
    "/jogos-app/",
    "/espiar/",
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
registro = logging.getLogger("g1")

_sessao = requests.Session()
_sessao.headers["User-Agent"] = USER_AGENT


class Bloqueio(RuntimeError):
    """Resposta 403 ou página de bloqueio. Quem recebe deve parar a coleta inteira."""


def pedir(url: str) -> requests.Response | None:
    """Faz um GET com pausa de PAUSA segundos depois de cada pedido.

    Em 429 ou 5xx espera (dobrando) e tenta de novo, no máximo TENTATIVAS_EXTRAS vezes.
    Depois disso devolve None e registra. Em 403 ou página de bloqueio levanta Bloqueio.
    """
    espera = ESPERA_INICIAL
    for tentativa in range(TENTATIVAS_EXTRAS + 1):
        try:
            resposta = _sessao.get(url, timeout=30)
        except requests.RequestException as erro:
            registro.warning("falha de rede em %s: %s", url, erro)
            time.sleep(PAUSA)
            return None
        time.sleep(PAUSA)
        if resposta.status_code == 403 or _e_pagina_de_bloqueio(resposta):
            raise Bloqueio(f"bloqueio em {url} (status {resposta.status_code}). Parando a coleta.")
        if resposta.status_code == 429 or resposta.status_code >= 500:
            if tentativa == TENTATIVAS_EXTRAS:
                registro.warning("desisti de %s depois de %s tentativas", url, tentativa + 1)
                return None
            registro.warning("status %s em %s; espero %s s", resposta.status_code, url, espera)
            time.sleep(espera)
            espera *= 2
            continue
        return resposta
    return None


def _e_pagina_de_bloqueio(resposta: requests.Response) -> bool:
    """Olha só o título da página. Página de desafio ou de acesso negado conta como bloqueio."""
    inicio = resposta.text[:3000].lower() if resposta.ok else ""
    return any(marca in inicio for marca in ("access denied", "acesso negado", "just a moment"))


def pasta_bronze(dia: str | None = None) -> Path:
    """Pasta do bronze de um dia de coleta. Sem dia, usa a data de hoje (UTC)."""
    dia = dia or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return DADOS / "bronze" / f"coleta={dia}"


def ultimo_bronze() -> Path:
    """A pasta de bronze mais recente que existe no disco."""
    pastas = sorted((DADOS / "bronze").glob("coleta=*"))
    if not pastas:
        raise FileNotFoundError("Não há bronze. Rode antes: uv run python src/coletar.py")
    return pastas[-1]


def gravar_bronze(resposta: requests.Response, nome: str, pasta: Path) -> Path:
    """Grava os bytes da resposta sem mexer em nada, e ao lado um arquivo com a origem."""
    pasta.mkdir(parents=True, exist_ok=True)
    arquivo = pasta / nome
    arquivo.write_bytes(resposta.content)
    origem = {
        "url": resposta.url,
        "status": resposta.status_code,
        "tipo": resposta.headers.get("Content-Type"),
        "instante": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sha256": hashlib.sha256(resposta.content).hexdigest(),
        "bytes": len(resposta.content),
    }
    (pasta / f"{nome}.origem.json").write_text(
        json.dumps(origem, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return arquivo


def nome_estavel(url: str) -> str:
    """Nome de arquivo que não muda para a mesma URL: 'materia-' + 16 caracteres do hash da URL."""
    digesto = hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]
    return f"materia-{digesto}.html"


def carregar_permissoes(pasta: Path) -> urllib.robotparser.RobotFileParser:
    """Lê o robots.txt do G1. Se ele não estiver em bronze ainda, baixa uma vez e guarda."""
    arquivo = pasta / "robots.txt"
    if not arquivo.exists():
        resposta = pedir(f"{SITE}/robots.txt")
        if resposta is None or resposta.status_code != 200:
            raise RuntimeError("Não consegui ler o robots.txt do G1. Não sigo sem ele.")
        gravar_bronze(resposta, "robots.txt", pasta)
    permissoes = urllib.robotparser.RobotFileParser()
    permissoes.parse(arquivo.read_text(encoding="utf-8").splitlines())
    return permissoes


def pode_baixar(permissoes: urllib.robotparser.RobotFileParser, url: str) -> bool:
    """Confere o robots.txt e a lista de caminhos proibidos antes de qualquer pedido."""
    caminho = url.replace(SITE, "", 1)
    if any(caminho.startswith(proibido) for proibido in PROIBIDOS):
        return False
    return permissoes.can_fetch(USER_AGENT, url)
