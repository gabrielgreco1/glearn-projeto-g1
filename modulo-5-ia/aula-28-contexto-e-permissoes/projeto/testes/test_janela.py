"""Testes do buraco entre duas janelas do feed. Usam notícias escritas à mão: rodam sem internet."""

from datetime import date, datetime, timezone

from janela import buraco, quando


def noticia(publicado):
    return {"publicado": publicado}


FEED = [noticia("Sun, 15 Nov 2026 12:06:34 -0000"), noticia("Wed, 04 Nov 2026 13:33:08 -0000")]


def test_o_feed_escreve_utc_e_o_instante_sai_com_o_fuso():
    assert quando(FEED[1]) == datetime(2026, 11, 4, 13, 33, 8, tzinfo=timezone.utc)


def test_janelas_que_se_encostam_nao_tem_buraco():
    ultima = datetime(2026, 11, 10, 9, 0, tzinfo=timezone.utc)  # o feed de agora ainda mostra notícias antes dela
    assert buraco(FEED, ultima) == []


def test_buraco_vai_do_dia_da_ultima_vista_ao_dia_da_mais_antiga_do_feed():
    ultima = datetime(2026, 11, 1, 12, 0, tzinfo=timezone.utc)
    assert buraco(FEED, ultima) == [date(2026, 11, 1), date(2026, 11, 2), date(2026, 11, 3), date(2026, 11, 4)]


def test_o_dia_e_o_de_brasilia():
    ultima = datetime(2026, 11, 2, 1, 0, tzinfo=timezone.utc)  # 22h de 1º/11 em Brasília
    assert buraco(FEED, ultima)[0] == date(2026, 11, 1)


def test_primeira_rodada_nao_tem_com_o_que_comparar():
    assert buraco(FEED, None) == []
