"""O projeto G1 como um flow do Prefect: as seis etapas do rodar.py, uma task cada, na ordem. As tasks que pedem ao G1
(o feed e as páginas) são tentadas de novo quando a rede falha; uma recusa do site para sem nova tentativa.
Se a execução termina mal, fica um aviso em avisos.log."""

from datetime import datetime

from prefect import flow, task

import acumular
import carregar as carga
import conferir
import materias
import tabela
import transformar as transformacao
from baixar import baixar_feed
from ler import feed_mais_novo, ler_feed


@task(retries=3, retry_delay_seconds=10, timeout_seconds=60)
def feed():
    """Pede o feed ao G1, com o etag da última vez: se ele não mudou, o G1 responde 304 e nada é baixado."""
    baixar_feed()


@task
def guardar():
    """Lê o feed mais novo guardado, mesmo depois de um 304, como no rodar.py: as notícias já guardadas não entram de novo."""
    acumular.acumular(ler_feed(feed_mais_novo().read_bytes()), "feed")


paginas = task(materias.baixar_materias, name="paginas", retries=3, retry_delay_seconds=10, timeout_seconds=300)


@task
def tabela_e_conferencia():
    tabela.gravar_csv(tabela.montar())
    conferir.conferir()


transformar = task(transformacao.main, name="transformar")
carregar = task(carga.main, name="carregar")


def avisar(flow, flow_run, state):
    """O Prefect chama esta função quando a execução termina em Failed ou Crashed. O aviso diz o que olhar primeiro."""
    aviso = f"AVISO: {flow.name}, execução {flow_run.name}, terminou em {state.name}: {state.message}"
    print(aviso)
    with open("avisos.log", "a", encoding="utf-8") as arquivo:
        arquivo.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} {aviso} (o que fazer: runbook.md)\n")


@flow(log_prints=True, on_failure=[avisar], on_crashed=[avisar])
def projeto_g1():
    feed()
    guardar()
    paginas()
    tabela_e_conferencia()
    transformar()
    carregar()


if __name__ == "__main__":
    projeto_g1()
