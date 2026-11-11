"""Testes da leitura da lista de matérias e da leitura de uma matéria, com as amostras escritas à mão."""

from pathlib import Path

from extrair import ler_lista, ler_materia

AMOSTRAS = Path(__file__).parent / "amostras"


def test_leitura_da_lista_acha_so_as_materias():
    html = (AMOSTRAS / "lista-tecnologia.html").read_text(encoding="utf-8")
    links = ler_lista(html)
    assert links == [
        "https://g1.globo.com/tecnologia/noticia/2026/11/11/exemplo-uma-noticia.ghtml",
        "https://g1.globo.com/tecnologia/noticia/2026/11/10/exemplo-duas-noticias.ghtml",
    ]


def test_leitura_de_uma_materia_traz_todos_os_campos():
    html = (AMOSTRAS / "materia-tecnologia.html").read_text(encoding="utf-8")
    url = "https://g1.globo.com/tecnologia/noticia/2026/11/11/exemplo-uma-noticia.ghtml"
    assert ler_materia(html, url) == {
        "url": url,
        "titulo": "Notícia fictícia de teste",
        "subtitulo": "Subtítulo inventado para o teste.",
        "publicado_em": "2026-11-11T11:40:07-03:00",
        "autor": "Autora Exemplo",
        "editoria": "Tecnologia",
        "n_palavras": 18,
    }


def test_materia_sem_autor_deixa_autor_vazio():
    html = (AMOSTRAS / "materia-sem-autor.html").read_text(encoding="utf-8")
    materia = ler_materia(html, "https://g1.globo.com/tecnologia/noticia/2026/11/11/x.ghtml")
    assert materia["autor"] == ""
    assert materia["titulo"] == "Notícia sem autor"
    assert materia["publicado_em"] == "2026-11-11T11:40:07-03:00"
