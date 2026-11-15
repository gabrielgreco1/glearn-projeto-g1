"""O projeto G1 como um flow do Prefect: as seis etapas do rodar.py, uma task cada, na ordem. As tasks que pedem ao G1
(o feed e as páginas) são tentadas de novo quando a rede falha; uma recusa do site para sem nova tentativa.
Se a execução termina mal, fica um aviso em avisos.log. Se termina bem, mas a vigia vê algo estranho no banco, também.
Uma execução por vez: a segunda espera a vaga do limite projeto-g1, criado uma vez no servidor do Prefect com
uv run prefect gcl create projeto-g1 --limit 1

Uso: uv run python fluxo.py            roda uma vez, agora
     uv run python fluxo.py agendar    fica ligado e roda de 3 em 3 horas (Ctrl+C para parar)
"""

import sys
from datetime import datetime

from prefect import flow, task
from prefect.concurrency.sync import concurrency
from prefect.schedules import Cron

import carregar as carga
import conferir
import janela
import materias
import tabela
import transformar as transformacao
import vigiar as vigia
from baixar import baixar_feed
from ler import feed_mais_novo, ler_feed


@task(retries=3, retry_delay_seconds=10, timeout_seconds=60)
def feed():
    """Pede o feed ao G1, com o etag da última vez: se ele não mudou, o G1 responde 304 e nada é baixado."""
    baixar_feed()


@task(retries=3, retry_delay_seconds=10, timeout_seconds=300)
def guardar():
    """Lê o feed mais novo guardado, mesmo depois de um 304, como no rodar.py: as notícias já guardadas não entram de novo.
    Se o feed já não encosta na rodada anterior, pede antes o mapa do site dos dias do buraco: por isso, as tentativas."""
    janela.guardar_feed(ler_feed(feed_mais_novo().read_bytes()))


paginas = task(materias.baixar_materias, name="paginas", retries=3, retry_delay_seconds=10, timeout_seconds=300)


@task
def tabela_e_conferencia():
    tabela.gravar_csv(tabela.montar())
    conferir.conferir()


transformar = task(transformacao.main, name="transformar")
carregar = task(carga.main, name="carregar")


def anotar(aviso):
    """Mostra o aviso no log e acrescenta uma linha em avisos.log, com a hora."""
    print(aviso)
    with open("avisos.log", "a", encoding="utf-8") as arquivo:
        arquivo.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} {aviso} (o que fazer: runbook.md)\n")


def avisar(flow, flow_run, state):
    """O Prefect chama esta função quando a execução termina em Failed ou Crashed. O aviso diz o que olhar primeiro."""
    anotar(f"AVISO: {flow.name}, execução {flow_run.name}, terminou em {state.name}: {state.message}")


@task
def vigiar():
    """O que nenhuma task acusa: cada aviso da vigia vira uma linha de ATENÇÃO, e a execução continua Completed."""
    for aviso in vigia.avisos():
        anotar(f"ATENÇÃO: {aviso}")


@flow(log_prints=True, on_failure=[avisar], on_crashed=[avisar])
def projeto_g1():
    # Uma execução por vez, do feed à vigia: duas ao mesmo tempo pediriam as mesmas páginas duas vezes ao G1 e
    # escreveriam os mesmos arquivos. strict=True: sem o limite criado no servidor, para aqui, em vez de seguir sem ele.
    with concurrency("projeto-g1", occupy=1, timeout_seconds=900, strict=True):
        feed()
        guardar()
        paginas()
        tabela_e_conferencia()
        transformar()
        carregar()
        vigiar()


if __name__ == "__main__":
    if sys.argv[1:] == ["agendar"]:
        # De 3 em 3 horas, no horário de Brasília: 0h, 3h, 6h ... 21h. O feed cobre uns 11 dias e o G1 guarda a cópia
        # dele por 10 minutos; 8 rodadas por dia dão até 160 páginas, contra umas 10 notícias novas por dia.
        projeto_g1.serve(name="a-cada-3-horas", schedule=Cron("0 */3 * * *", timezone="America/Sao_Paulo"))
    else:
        projeto_g1()
