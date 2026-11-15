"""A janela do feed: o feed só mostra as últimas 100 notícias. Se o programa fica parado mais tempo do que a janela
cobre, as notícias do meio saem do feed sem passar por ele, e fica um buraco. O buraco é tapado pelo mapa do site dos
dias dele, como o sitemap.py faz com um dia.

Uso: uv run python janela.py   mede a janela do feed mais novo guardado"""

from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

from acumular import acumular
from baixar import FEEDS, estado_do_feed, gravar_estado_do_feed, registro
from ler import feed_mais_novo, ler_feed
from sitemap import ler_mapa, partes_do_dia

BRASILIA = timezone(timedelta(hours=-3))  # o dia do mapa do site é o dia em Brasília, sem horário de verão desde 2019


def quando(noticia):
    """O instante em que a notícia saiu, do jeito que o feed escreve: 'Fri, 13 Nov 2026 20:28:07 -0000'. O -0000 quer
    dizer UTC, mas o Python lê a data sem fuso: o fuso é posto aqui, para comparar com outros instantes."""
    instante = parsedate_to_datetime(noticia["publicado"])
    return instante.replace(tzinfo=timezone.utc) if instante.tzinfo is None else instante


def duracao(tempo):
    """Um timedelta em dias e horas, ou em horas e minutos: '10 dias e 22 h', '18 h 39 min'."""
    horas, minutos = tempo.seconds // 3600, tempo.seconds % 3600 // 60
    return f"{tempo.days} dias e {horas} h" if tempo.days else f"{horas} h {minutos} min"


def em_brasilia(instante):
    """'04/11 10:33', no horário de Brasília."""
    return f"{instante.astimezone(BRASILIA):%d/%m %H:%M}"


def buraco(noticias, ultima):
    """Os dias que o mapa do site precisa cobrir. ultima é o instante da notícia mais nova que o programa já viu no
    feed. Se a mais antiga do feed de agora é mais nova que ela, as duas janelas não se encostam: as notícias do meio
    podem ter saído do feed sem passar pelo programa. Devolve os dias, de um instante ao outro, em Brasília."""
    if ultima is None or not noticias:
        return []  # a primeira rodada não tem com o que comparar
    mais_antiga = min(quando(noticia) for noticia in noticias)
    if mais_antiga <= ultima:
        return []
    primeiro = ultima.astimezone(BRASILIA).date()
    ultimo = mais_antiga.astimezone(BRASILIA).date()
    return [primeiro + timedelta(days=n) for n in range((ultimo - primeiro).days + 1)]


def guardar_feed(noticias, feed="tecnologia"):
    """Guarda as notícias de um feed. Antes, se houver buraco, guarda as do mapa do site dos dias dele, só da editoria
    do feed. No fim, anota em dados/estado.json o instante da notícia mais nova vista nesse feed, para a próxima rodada
    comparar: cada feed tem a sua janela, e o de um não esconde o buraco do outro."""
    anotada = estado_do_feed(feed).get("mais_nova")
    ultima = datetime.fromisoformat(anotada) if anotada else None
    dias = buraco(noticias, ultima)
    if dias:
        registro.warning("buraco no feed de %s: a notícia mais antiga do feed é de %s, e a mais nova que o programa já "
                         "tinha visto nele é de %s. Vou ao mapa do site de %s dia(s), de %s a %s", feed,
                         em_brasilia(min(map(quando, noticias))), em_brasilia(ultima), len(dias), dias[0], dias[-1])
        for dia in dias:
            arquivos = partes_do_dia(dia)
            if not arquivos:  # todo dia do G1 tem notícia no mapa: sem nenhuma parte, o buraco não foi tapado
                raise RuntimeError(f"o mapa do site de {dia} veio sem endereço nenhum: o buraco não foi tapado")
            for arquivo in arquivos:
                acumular(ler_mapa(arquivo.read_bytes(), feed), "sitemap")
    acumular(noticias, "feed")
    if noticias:
        mais_nova = max([quando(noticia) for noticia in noticias] + ([ultima] if ultima else []))
        gravar_estado_do_feed(feed, mais_nova=mais_nova.isoformat())


def guardar_feeds():
    """Lê o arquivo mais novo de cada feed, mesmo depois de um 304, e guarda as notícias dele."""
    for feed in FEEDS:
        guardar_feed(ler_feed(feed_mais_novo(feed).read_bytes(), feed), feed)


def medir(noticias):
    """A janela do feed em números: de quando a quando, quantas notícias por dia e o maior intervalo sem notícia."""
    instantes = sorted(quando(noticia) for noticia in noticias)
    janela = instantes[-1] - instantes[0]
    intervalos = [depois - antes for antes, depois in zip(instantes, instantes[1:])]
    registro.info("o feed tem %s notícias, de %s a %s, em Brasília", len(instantes), em_brasilia(instantes[0]),
                  em_brasilia(instantes[-1]))
    registro.info("janela de %s; %.1f notícias por dia; o maior intervalo sem notícia nova: %s",
                  duracao(janela), len(instantes) / (janela / timedelta(days=1)), duracao(max(intervalos)))


if __name__ == "__main__":
    for feed in FEEDS:
        registro.info("feed de %s", feed)
        medir(ler_feed(feed_mais_novo(feed).read_bytes(), feed))
