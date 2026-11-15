"""Depois da carga, olha no banco o que nenhuma task acusa: o feed sem notícia nova há mais de um dia, as páginas mais
novas sem texto ou sem assinatura (o G1 pode ter mudado a página) e a fila de páginas que não anda. Não para nada:
devolve os avisos, e cada aviso diz o que olhar.

Uso: uv run python vigiar.py"""

from datetime import timedelta

from baixar import registro
from banco import conectar

SILENCIO = timedelta(hours=24)  # o maior intervalo entre duas notícias, medido no feed na PGO-02, foi de 18 h 39 min
RECENTES = 10  # quantas páginas, das notícias mais novas, a vigia olha
ESTRANHAS = 5  # metade delas sem texto ou sem assinatura já não é acaso
FILA = 40  # notícias esperando a página: duas rodadas de 20

# Há quanto tempo saiu a notícia mais nova do banco. A do mapa do site sem página não tem hora, e o max a ignora.
SILENCIO_SQL = "SELECT now() - max(publicado_em) FROM noticias"
# Das páginas das notícias mais novas, quantas vieram sem texto ou sem ninguém na assinatura.
PAGINAS = f"""
SELECT count(*),
       count(*) FILTER (WHERE n.palavras = 0 OR NOT EXISTS (SELECT 1 FROM assinaturas s WHERE s.noticia_id = n.id))
FROM (SELECT id, palavras FROM noticias WHERE palavras IS NOT NULL ORDER BY publicado_em DESC LIMIT {RECENTES}) n
"""
SEM_PAGINA = "SELECT count(*) FROM noticias WHERE palavras IS NULL"


def horas(tempo):
    """Um timedelta em horas inteiras: '30 h'."""
    return f"{tempo // timedelta(hours=1)} h"


def avisos_dos_numeros(silencio, recentes, estranhas, fila):
    """As regras da vigia, sobre os números do banco. Devolve uma lista de textos, vazia se está tudo como sempre."""
    avisos = []
    if silencio is not None and silencio > SILENCIO:
        avisos.append(f"a notícia mais nova do banco saiu há {horas(silencio)}, mais do que o maior silêncio medido no "
                      "feed. O feed parou? Abra https://g1.globo.com/rss/g1/tecnologia/ no navegador e veja a data do "
                      "primeiro item.")
    if recentes >= RECENTES and estranhas >= ESTRANHAS:
        avisos.append(f"{estranhas} das {recentes} páginas mais novas vieram sem texto ou sem assinatura. O G1 pode ter "
                      "mudado a página: abra uma delas no navegador e procure o itemprop=\"articleBody\" que o texto.py usa.")
    if fila > FILA:
        avisos.append(f"{fila} notícias esperam a página, e o materias.py baixa 20 por rodada. Veja no log da task paginas "
                      "se as páginas estão vindo; depois de um buraco, a fila desce sozinha em poucas rodadas.")
    return avisos


def avisos():
    """Lê os números no banco e devolve os avisos."""
    with conectar() as conexao:
        silencio = conexao.execute(SILENCIO_SQL).fetchone()[0]
        recentes, estranhas = conexao.execute(PAGINAS).fetchone()
        fila = conexao.execute(SEM_PAGINA).fetchone()[0]
    lista = avisos_dos_numeros(silencio, recentes, estranhas, fila)
    registro.info("vigia: a notícia mais nova saiu há %s; %s das %s páginas mais novas sem texto ou sem assinatura; "
                  "%s notícias sem página; %s avisos", horas(silencio) if silencio else "?", estranhas, recentes, fila,
                  len(lista))
    return lista


if __name__ == "__main__":
    for aviso in avisos():
        print(aviso)
