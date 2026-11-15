"""As regras da vigia, com números escritos à mão. Não falam com o banco."""

from datetime import timedelta

from vigiar import avisos_dos_numeros


def test_dia_como_sempre_nao_avisa():
    assert avisos_dos_numeros(timedelta(hours=2), 10, 0, 0) == []


def test_feed_parado_mais_que_um_dia():
    avisos = avisos_dos_numeros(timedelta(hours=30, minutes=5), 10, 0, 0)
    assert len(avisos) == 1
    assert avisos[0].startswith("a notícia mais nova do banco saiu há 30 h")


def test_noite_sem_noticia_nao_e_feed_parado():
    assert avisos_dos_numeros(timedelta(hours=18, minutes=39), 10, 0, 0) == []


def test_metade_das_paginas_novas_sem_texto():
    avisos = avisos_dos_numeros(timedelta(hours=2), 10, 5, 0)
    assert avisos[0].startswith("5 das 10 páginas mais novas vieram sem texto ou sem assinatura")


def test_uma_pagina_sem_texto_e_acaso():
    assert avisos_dos_numeros(timedelta(hours=2), 10, 1, 0) == []


def test_fila_de_paginas():
    assert avisos_dos_numeros(timedelta(hours=2), 10, 0, 41)[0].startswith("41 notícias esperam a página")
    assert avisos_dos_numeros(timedelta(hours=2), 10, 0, 28) == []
