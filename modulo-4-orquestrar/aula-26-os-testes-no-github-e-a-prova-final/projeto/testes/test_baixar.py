"""O pedido ao G1 sem o contato do .env, como nos testes do GitHub: importar o baixar.py funciona, e o pedido para com
a mensagem que diz o que falta. Também a recusa do site, que para sem nova tentativa, e o 5xx, que é tentado de novo."""

import httpx
import pytest

import baixar


def test_sem_contato_o_pedido_para_com_a_mensagem(monkeypatch):
    monkeypatch.delenv("G1_USER_AGENT", raising=False)  # tira o contato só durante este teste
    with pytest.raises(SystemExit, match="G1_USER_AGENT"):
        baixar.pedir(baixar.FEED)


def responde(monkeypatch, status):
    """Troca o httpx.get por um que devolve o status pedido, sem rede, e tira a pausa."""
    monkeypatch.setenv("G1_USER_AGENT", "teste/0.1 (https://exemplo.invalid)")
    monkeypatch.setattr(baixar.httpx, "get", lambda url, **kw: httpx.Response(status, request=httpx.Request("GET", url)))
    monkeypatch.setattr(baixar, "PAUSA", 0)


def test_recusa_para_o_programa(monkeypatch):
    responde(monkeypatch, 429)
    with pytest.raises(SystemExit, match="respondeu 429"):
        baixar.pedir(baixar.FEED)


def test_erro_do_site_sobe_para_ser_tentado_de_novo(monkeypatch):
    responde(monkeypatch, 503)
    with pytest.raises(RuntimeError, match="vale tentar de novo"):
        baixar.pedir(baixar.FEED)
