"""
Trabalho de Sistemas Distribuídos - Soneca Barber
Grupo: ()

Arquivo: barbeiro.py
    Servidor do barbeiro. Roda em um terminal separado.
    Aguarda conexões de clientes via socket TCP.
    Implementa o problema do Barbeiro Dorminhoco sem memória compartilhada:
    toda comunicação é feita por troca de mensagens entre programas distintos.

Como rodar:
    Terminal 1:  python barbeiro.py
    Terminal 2:  python cliente.py 1
    Terminal 3:  python cliente.py 2
    ...

Mensagens do protocolo:
    Cliente -> Barbeiro:  "CHEGOU:<id>"
    Barbeiro -> Cliente:  "SENTE"       (tem vaga, pode esperar)
    Barbeiro -> Cliente:  "CHEIO"       (sem vaga, vai embora)
    Barbeiro -> Cliente:  "ATENDENDO"   (sua vez na cadeira)
    Barbeiro -> Cliente:  "PRONTO"      (corte finalizado, pode ir)
"""

import socket
import threading
import time

# --------------------------------------------------------------------------
# Configurações
# --------------------------------------------------------------------------
HOST        = "127.0.0.1"
PORT        = 65432
MAX_ESPERA  = 3       # cadeiras de espera
TEMPO_CORTE = 15       # segundos simulando o corte


# --------------------------------------------------------------------------
# Estado interno do barbeiro (local, não compartilhado com ninguém)
# --------------------------------------------------------------------------
fila_espera    = []           # lista de (conn, cliente_id) aguardando
lock_fila      = threading.Lock()
barbeiro_livre = threading.Event()
barbeiro_livre.set()          # começa livre (dormindo = livre sem cliente)


def log(msg):
    print(msg, flush=True)


# --------------------------------------------------------------------------
# Thread que gerencia o atendimento (o "barbeiro" de fato)
# --------------------------------------------------------------------------
def loop_barbeiro():
    log("[BARBEIRO] Barbearia aberta. Barbeiro dormindo...")

    while True:
        # espera ter alguém na fila
        while True:
            with lock_fila:
                if fila_espera:
                    conn, cliente_id = fila_espera.pop(0)
                    break
            time.sleep(0.3)   # polling leve enquanto fila vazia

        log(f"[BARBEIRO] Chamando Cliente {cliente_id}. PRÓXIMO!")

        # avisa o cliente que é a vez dele
        try:
            conn.sendall("ATENDENDO".encode())
        except Exception:
            log(f"[BARBEIRO] Cliente {cliente_id} caiu antes de ser atendido.")
            continue

        log(f"[BARBEIRO] Cortando o cabelo do Cliente {cliente_id}...")
        time.sleep(TEMPO_CORTE)

        # avisa que terminou
        try:
            conn.sendall("PRONTO".encode())
        except Exception:
            pass

        log(f"[BARBEIRO] Pronto! Cliente {cliente_id} atendido.")

        with lock_fila:
            if not fila_espera:
                log("[BARBEIRO] Fila vazia. Voltando a dormir...")

        conn.close()


# --------------------------------------------------------------------------
# Thread para cada conexão de cliente recebida
# --------------------------------------------------------------------------
def handle_cliente(conn, addr):
    try:
        dados = conn.recv(1024).decode().strip()   # espera "CHEGOU:<id>"

        if not dados.startswith("CHEGOU:"):
            conn.close()
            return

        cliente_id = dados.split(":")[1]
        log(f"[BARBEIRO] Mensagem recebida: '{dados}' de {addr}")

        with lock_fila:
            vagas = MAX_ESPERA - len(fila_espera)

            if vagas > 0:
                fila_espera.append((conn, cliente_id))
                ocupadas = len(fila_espera)
                log(
                    f"[BARBEIRO] Cliente {cliente_id} entrou na fila de espera. "
                    f"({ocupadas}/{MAX_ESPERA} cadeiras ocupadas)"
                )
                conn.sendall("SENTE".encode())
                # não fecha a conexão — vai ser fechada após o atendimento
            else:
                log(
                    f"[BARBEIRO] Sem vagas! Mandando Cliente {cliente_id} embora."
                )
                conn.sendall("CHEIO".encode())
                conn.close()

    except Exception as e:
        log(f"[BARBEIRO] Erro com cliente {addr}: {e}")
        conn.close()


# --------------------------------------------------------------------------
# Main — sobe o servidor
# --------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("       SONECA BARBER - Servidor do Barbeiro")
    print(f"       Escutando em {HOST}:{PORT}")
    print(f"       Cadeiras de espera: {MAX_ESPERA}")
    print("=" * 60)
    print()

    # thread do barbeiro rodando em paralelo
    t_barbeiro = threading.Thread(target=loop_barbeiro, daemon=True)
    t_barbeiro.start()

    # socket servidor
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((HOST, PORT))
        servidor.listen()

        log(f"[SERVIDOR] Aguardando clientes...\n")

        while True:
            conn, addr = servidor.accept()
            t = threading.Thread(target=handle_cliente, args=(conn, addr), daemon=True)
            t.start()