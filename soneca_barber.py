"""
Trabalho de Sistemas Distribuídos - Soneca Barber
Grupo: ()

Objetivo:
    Simular o funcionamento de uma barbearia usando troca de mensagens
    entre processos. O barbeiro dorme quando não tem cliente e é acordado
    quando alguém chega. Se todas as cadeiras de espera estiverem ocupadas,
    o cliente vai embora.

Abordagem:
    Usamos a biblioteca multiprocessing do Python.
    A comunicação entre processos é feita via Queue (fila de mensagens),
    o que representa a troca de mensagens do modelo distribuído.

    Processos:
        - barbeiro_process: processo do barbeiro, fica esperando mensagens
        - cliente_process: cada cliente é um processo separado

    Estrutura da barbearia:
        - 1 cadeira de barbeiro
        - 3 cadeiras de espera (MAX_ESPERA = 3)

    Mensagens trocadas:
        - Cliente -> Barbeiro: "ACORDA" (quando barbeiro tá dormindo)
        - Cliente -> Fila de espera: "AGUARDANDO" (senta na cadeira de espera)
        - Barbeiro -> Cliente: "PROXIMO" (chama o próximo da fila)
        - Cliente -> Barbeiro: "TCHAU" (vai embora por falta de cadeira)
"""

import multiprocessing
import time
import random


# --------------------------------------------------------------------------
# Constantes
# --------------------------------------------------------------------------
MAX_ESPERA = 3          # número de cadeiras de espera
TEMPO_CORTE = 1.5       # segundos simulando o tempo de um corte
TEMPO_CHEGADA = 0.8     # intervalo base entre chegadas de clientes


# --------------------------------------------------------------------------
# Processo do Barbeiro
# --------------------------------------------------------------------------
def barbeiro_process(fila_espera, lock, cadeiras_ocupadas, barbeiro_dormindo,
                     barbeiro_ocupado, log_queue):
    """
    Processo principal do barbeiro.

    Fica em loop aguardando mensagens na fila de espera.
    Se não tiver ninguém, dorme (sinaliza barbeiro_dormindo = True).
    Quando chega uma mensagem, acorda e atende o cliente.

    Parâmetros:
        fila_espera      -- Queue compartilhada com IDs dos clientes esperando
        lock             -- Lock para acesso exclusivo às variáveis compartilhadas
        cadeiras_ocupadas-- Value compartilhado: quantas cadeiras de espera estão em uso
        barbeiro_dormindo-- Value compartilhado: flag se o barbeiro tá dormindo
        barbeiro_ocupado -- Value compartilhado: flag se o barbeiro tá atendendo alguém
        log_queue        -- Queue para mandar mensagens de log pro processo principal
    """

    log_queue.put("[BARBEARIA] Abrindo... Barbeiro sentou na cadeira e dormiu. 💤")
    barbeiro_dormindo.value = True

    while True:
        # tenta pegar um cliente da fila de espera
        try:
            cliente_id = fila_espera.get(timeout=5)
        except Exception:
            # se ninguém aparecer em 5s, encerra o dia
            log_queue.put("[BARBEIRO] Fim do dia, fechando a barbearia.")
            break

        # acorda se tava dormindo
        with lock:
            if barbeiro_dormindo.value:
                log_queue.put(
                    f"[BARBEIRO] *esfregando os olhos* Ugh... acordei porque o "
                    f"Cliente {cliente_id} gritou ACORDA!"
                )
                barbeiro_dormindo.value = False

            # libera uma cadeira de espera (o cliente saiu dela pra sentar no barbeiro)
            if cadeiras_ocupadas.value > 0:
                cadeiras_ocupadas.value -= 1

            barbeiro_ocupado.value = True

        log_queue.put(
            f"[BARBEIRO] Atendendo o Cliente {cliente_id}... "
            f"(cadeiras de espera livres: {MAX_ESPERA - cadeiras_ocupadas.value})"
        )

        # simula o tempo do corte
        time.sleep(TEMPO_CORTE)

        log_queue.put(f"[BARBEIRO] Terminou o corte do Cliente {cliente_id}. PRÓXIMO!")

        with lock:
            barbeiro_ocupado.value = False

            # se a fila tiver vazia, vai dormir de novo
            if fila_espera.empty():
                barbeiro_dormindo.value = True
                log_queue.put("[BARBEIRO] Fila vazia... voltando a dormir. 💤")


# --------------------------------------------------------------------------
# Processo de cada Cliente
# --------------------------------------------------------------------------
def cliente_process(cliente_id, fila_espera, lock, cadeiras_ocupadas,
                    barbeiro_dormindo, barbeiro_ocupado, log_queue):
    """
    Processo de um cliente chegando na barbearia.

    Verifica se tem cadeira de espera disponível:
        - Se sim: ocupa a cadeira e entra na fila de mensagens do barbeiro.
          Se o barbeiro tiver dormindo, manda a mensagem "ACORDA".
        - Se não: manda mensagem de log dizendo que foi embora.

    Parâmetros:
        cliente_id       -- identificador único do cliente
        fila_espera      -- Queue compartilhada com o barbeiro
        lock             -- Lock para acesso exclusivo
        cadeiras_ocupadas-- Value compartilhado: quantas cadeiras estão ocupadas
        barbeiro_dormindo-- Value compartilhado: flag do sono do barbeiro
        barbeiro_ocupado -- Value compartilhado: flag se barbeiro tá ocupado
        log_queue        -- Queue de log
    """

    with lock:
        # verifica se tem espaço
        # se o barbeiro tiver livre e não dormindo, não precisa nem de cadeira de espera
        if not barbeiro_ocupado.value and not barbeiro_dormindo.value:
            # barbeiro livre e acordado — vai direto
            log_queue.put(
                f"[CLIENTE {cliente_id}] Entrei e o barbeiro tá livre, sentei na cadeira!"
            )
            fila_espera.put(cliente_id)
            return

        if cadeiras_ocupadas.value < MAX_ESPERA:
            # tem vaga na espera
            cadeiras_ocupadas.value += 1
            ocupadas_agora = cadeiras_ocupadas.value

            if barbeiro_dormindo.value:
                log_queue.put(
                    f"[CLIENTE {cliente_id}] Cheguei e o barbeiro tava dormindo. "
                    f"ACORDA! Hora de trabalhar seu dorminhoco! 😤"
                )
            else:
                log_queue.put(
                    f"[CLIENTE {cliente_id}] Cheguei, barbeiro ocupado. "
                    f"Sentei na cadeira de espera. "
                    f"({ocupadas_agora}/{MAX_ESPERA} cadeiras ocupadas)"
                )

            # coloca na fila pra ser atendido
            fila_espera.put(cliente_id)

        else:
            # sem cadeira de espera disponível — vai embora
            log_queue.put(
                f"[CLIENTE {cliente_id}] Cheguei mas todas as {MAX_ESPERA} cadeiras "
                f"de espera estão ocupadas. Vou embora! 😒"
            )


# --------------------------------------------------------------------------
# Processo de log (centraliza prints pra não misturar saída)
# --------------------------------------------------------------------------
def log_process(log_queue, encerrar):
    """
    Processo auxiliar que consome a fila de log e imprime no terminal.
    Evita que prints de processos diferentes se sobreponham.

    Parâmetros:
        log_queue -- Queue com as mensagens de log
        encerrar  -- Event sinalizando que pode encerrar
    """
    while not encerrar.is_set() or not log_queue.empty():
        try:
            msg = log_queue.get(timeout=0.3)
            print(msg)
        except Exception:
            pass


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
if __name__ == "__main__":
    """
    Coordena a simulação inteira.

    Cria os processos compartilhados e dispara os clientes em sequência,
    demonstrando as 3 situações pedidas no enunciado:
        1. Abertura: barbearia vazia, barbeiro dormindo
        2. Clientes chegam, barbeiro atende, cadeiras de espera lotam
        3. Cliente chega com todas as cadeiras ocupadas e vai embora
    """

    print("=" * 60)
    print("       SONECA BARBER - Simulação Sistemas Distribuídos")
    print("=" * 60)
    print()

    # estruturas de comunicação/sincronização entre processos
    fila_espera       = multiprocessing.Queue()          # fila de mensagens: clientes -> barbeiro
    lock              = multiprocessing.Lock()           # exclusão mútua nas variáveis
    cadeiras_ocupadas = multiprocessing.Value('i', 0)   # int compartilhado: cadeiras em uso
    barbeiro_dormindo = multiprocessing.Value('b', False)
    barbeiro_ocupado  = multiprocessing.Value('b', False)
    log_queue         = multiprocessing.Queue()
    encerrar_log      = multiprocessing.Event()

    # inicia o processo de log centralizado
    p_log = multiprocessing.Process(
        target=log_process,
        args=(log_queue, encerrar_log),
        daemon=True
    )
    p_log.start()

    # -----------------------------------------------------------------------
    # Situação 1: abertura da barbearia — barbeiro dormindo, ninguém lá
    # -----------------------------------------------------------------------
    print(">>> SITUAÇÃO 1: Abrindo a barbearia\n")
    time.sleep(0.5)

    # inicia o barbeiro em processo separado
    p_barbeiro = multiprocessing.Process(
        target=barbeiro_process,
        args=(fila_espera, lock, cadeiras_ocupadas, barbeiro_dormindo,
              barbeiro_ocupado, log_queue),
        daemon=True
    )
    p_barbeiro.start()
    time.sleep(1)  # deixa o barbeiro "dormir" por um segundo antes dos clientes chegarem

    # -----------------------------------------------------------------------
    # Situação 2: clientes chegam, barbeiro atende, cadeiras lotam
    # O barbeiro demora TEMPO_CORTE por cliente, então se mandarmos 4 clientes
    # rápido: 1 acorda o barbeiro + 3 sentam na espera = cadeiras lotadas
    # -----------------------------------------------------------------------
    print("\n>>> SITUAÇÃO 2: Clientes chegando em sequência rápida\n")
    time.sleep(0.3)

    processos_clientes = []
    # manda 4 clientes quase ao mesmo tempo (antes do barbeiro terminar o 1º)
    for i in range(1, 5):
        p = multiprocessing.Process(
            target=cliente_process,
            args=(i, fila_espera, lock, cadeiras_ocupadas,
                  barbeiro_dormindo, barbeiro_ocupado, log_queue),
            daemon=True
        )
        p.start()
        processos_clientes.append(p)
        time.sleep(0.2)  # pequeno delay entre chegadas

    # aguarda os clientes chegarem e as cadeiras encherem
    # (tempo menor que TEMPO_CORTE pra garantir que o barbeiro ainda tá atendendo)
    time.sleep(0.5)

    # -----------------------------------------------------------------------
    # Situação 3: cliente chega com todas as cadeiras de espera ocupadas
    # Nesse ponto: barbeiro ocupado com cliente 1, clientes 2/3/4 nas cadeiras de espera
    # -----------------------------------------------------------------------
    print("\n>>> SITUAÇÃO 3: Cliente tentando entrar com barbearia cheia\n")
    time.sleep(0.1)

    # manda mais um cliente quando as 3 cadeiras de espera já tão ocupadas
    p_extra = multiprocessing.Process(
        target=cliente_process,
        args=(99, fila_espera, lock, cadeiras_ocupadas,
              barbeiro_dormindo, barbeiro_ocupado, log_queue),
        daemon=True
    )
    p_extra.start()
    p_extra.join()

    # aguarda todos os clientes serem atendidos / barbeiro encerrar
    for p in processos_clientes:
        p.join(timeout=20)

    p_barbeiro.join(timeout=15)

    # encerra o log
    time.sleep(1)
    encerrar_log.set()
    p_log.join(timeout=3)

    print()
    print("=" * 60)
    print("         Simulação encerrada.")
    print("=" * 60)
