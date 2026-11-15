"""Os dois feeds, o de Tecnologia e o de Economia: cada um na sua pasta, com o seu etag, e cada notícia com o feed de onde
veio. Sem internet: o httpx.get é trocado por um que responde com a amostra, e tudo é gravado numa pasta temporária."""

import json
from pathlib import Path

import httpx
import pytest

import baixar
from ler import feed_mais_novo, ler_feed
from sitemap import ler_mapa

AMOSTRA = Path(__file__).parent / "amostra_feed.xml"
AMOSTRA_MAPA = Path(__file__).parent / "amostra_mapa.xml"


@pytest.fixture
def pedidos(monkeypatch, tmp_path):
    """Roda dentro de uma pasta temporária, sem pausa, e guarda cada pedido feito: (url, cabeçalhos). O servidor de
    mentira responde 200 com a amostra e um etag próprio de cada feed, ou 304 se o If-None-Match for o etag dele."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("G1_USER_AGENT", "teste/0.1 (https://exemplo.invalid)")
    monkeypatch.setattr(baixar, "PAUSA", 0)
    feitos = []

    def responde(url, headers=None, **kw):
        feitos.append((url, headers))
        etag = f'"etag-{url}"'
        if (headers or {}).get("If-None-Match") == etag:
            return httpx.Response(304, request=httpx.Request("GET", url))
        return httpx.Response(200, content=AMOSTRA.read_bytes(), headers={"etag": etag}, request=httpx.Request("GET", url))

    monkeypatch.setattr(baixar.httpx, "get", responde)
    return feitos


def test_o_projeto_acompanha_tecnologia_e_economia():
    assert baixar.FEEDS == {"tecnologia": "https://g1.globo.com/rss/g1/tecnologia/",
                            "economia": "https://g1.globo.com/rss/g1/economia/"}


def test_baixar_pede_os_dois_feeds_cada_um_na_sua_pasta(pedidos):
    arquivos = baixar.baixar_feeds()
    assert [url for url, _ in pedidos] == list(baixar.FEEDS.values())
    for feed, arquivo in arquivos.items():
        assert arquivo.parts[:4] == ("dados", "bronze", "feed", feed)
        assert arquivo.exists()
    assert arquivos["tecnologia"].parent.parent != arquivos["economia"].parent.parent


def test_primeira_rodada_pede_sem_etag(pedidos):
    baixar.baixar_feeds()
    assert all("If-None-Match" not in cabecalhos for _, cabecalhos in pedidos)


def test_cada_feed_guarda_o_seu_etag_no_estado(pedidos):
    baixar.baixar_feeds()
    estado = json.loads(Path("dados/estado.json").read_text(encoding="utf-8"))
    assert estado["feeds"]["tecnologia"]["etag"] == '"etag-https://g1.globo.com/rss/g1/tecnologia/"'
    assert estado["feeds"]["economia"]["etag"] == '"etag-https://g1.globo.com/rss/g1/economia/"'


def test_segunda_rodada_manda_o_etag_de_cada_feed_e_o_304_nao_baixa_nada(pedidos):
    baixar.baixar_feeds()
    pedidos.clear()
    arquivos = baixar.baixar_feeds()
    assert arquivos == {"tecnologia": None, "economia": None}
    enviados = {url: cabecalhos["If-None-Match"] for url, cabecalhos in pedidos}
    assert enviados == {url: f'"etag-{url}"' for url in baixar.FEEDS.values()}
    assert len(list(Path("dados/bronze/feed").rglob("*.xml"))) == 2  # só os da primeira rodada


def test_um_feed_que_mudou_nao_derruba_o_etag_do_outro(pedidos):
    baixar.baixar_feeds()
    estado = baixar.ler_estado()
    estado["feeds"]["economia"]["etag"] = '"velho"'  # a economia mudou desde a última vez; a tecnologia não
    baixar.gravar_estado(estado)
    arquivos = baixar.baixar_feeds()
    assert arquivos["tecnologia"] is None
    assert arquivos["economia"] is not None
    assert baixar.estado_do_feed("economia")["etag"] == '"etag-https://g1.globo.com/rss/g1/economia/"'


def test_gravar_estado_de_um_feed_nao_mexe_no_resto(pedidos):
    baixar.gravar_estado({"outra_coisa": 1, "feeds": {"tecnologia": {"etag": "a", "mais_nova": "x"}}})
    baixar.gravar_estado_do_feed("economia", etag="b")
    baixar.gravar_estado_do_feed("tecnologia", mais_nova="y")
    assert baixar.ler_estado() == {"outra_coisa": 1, "feeds": {"tecnologia": {"etag": "a", "mais_nova": "y"},
                                                               "economia": {"etag": "b"}}}


def test_feed_mais_novo_olha_so_a_pasta_do_feed(pedidos):
    baixar.baixar_feeds()
    assert feed_mais_novo("economia").parts[3] == "economia"
    assert feed_mais_novo("tecnologia").parts[3] == "tecnologia"


def test_feed_sem_arquivo_para_com_a_mensagem(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit, match="economia"):
        feed_mais_novo("economia")


def test_cada_noticia_guarda_o_feed_de_onde_veio():
    noticias = ler_feed(AMOSTRA.read_bytes(), "economia")
    assert {noticia["feed"] for noticia in noticias} == {"economia"}


def test_o_feed_nao_se_confunde_com_a_editoria_do_endereco():
    """O feed de tecnologia traz notícia cujo endereço é de economia: a editoria é a do endereço, o feed é o de origem."""
    noticias = ler_feed(AMOSTRA.read_bytes(), "tecnologia")
    assert [(noticia["editoria"], noticia["feed"]) for noticia in noticias] == [("tecnologia", "tecnologia"),
                                                                                ("economia", "tecnologia")]


def test_o_mapa_do_site_leva_a_editoria_como_feed():
    assert {noticia["feed"] for noticia in ler_mapa(AMOSTRA_MAPA.read_bytes())} == {"tecnologia"}
