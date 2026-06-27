"""
Trabalho de Sistemas Distribuídos - Soneca Barber
Grupo: ()

Arquivo: cliente.py
    Programa do cliente. Cada instância representa um cliente diferente.
    Conecta no servidor do barbeiro via socket TCP e aguarda resposta.

Como rodar:
    python cliente.py <id_do_cliente>

    Exemplo:
        python cliente.py 1
        python cliente.py 2
        python cliente.py 99

Mensagens do protocolo:
    Cliente -> Barbeiro:  "CHEGOU:<id>"
    Barbeiro -> Cliente:  "SENTE"       (tem vaga, pode esperar)
    Barbeiro -> Cliente:  "CHEIO"       (sem vaga, vai embora)
    Barbeiro -> Cliente:  "ATENDENDO"   (sua vez na cadeira)
    Barbeiro -> Cliente:  "PRONTO"      (corte finalizado, pode ir)
"""

import socket
import sys

# --------------------------------------------------------------------------
# Configurações (devem bater com barbeiro.py)
# --------------------------------------------------------------------------
HOST = "127.0.0.1"
PORT = 65432


def log(msg):
    print(msg, flush=True)


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python cliente.py <id_do_cliente>")
        sys.exit(1)

    cliente_id = sys.argv[1]

    log(f"[CLIENTE {cliente_id}] Chegando na barbearia...")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))

            # manda mensagem de chegada
            mensagem = f"CHEGOU:{cliente_id}"
            s.sendall(mensagem.encode())
            log(f"[CLIENTE {cliente_id}] Mensagem enviada: '{mensagem}'")

            # aguarda resposta do barbeiro
            resposta = s.recv(1024).decode().strip()
            log(f"[CLIENTE {cliente_id}] Resposta recebida: '{resposta}'")

            if resposta == "CHEIO":
                log(
                    f"[CLIENTE {cliente_id}] Todas as cadeiras ocupadas. "
                    f"Vou embora!"
                )

            elif resposta == "SENTE":
                log(
                    f"[CLIENTE {cliente_id}] Sentei na cadeira de espera... "
                    f"aguardando minha vez."
                )

                # fica esperando até o barbeiro chamar
                while True:
                    msg = s.recv(1024).decode().strip()

                    if not msg:
                        break

                    log(f"[CLIENTE {cliente_id}] Mensagem recebida: '{msg}'")

                    if msg == "ATENDENDO":
                        log(
                            f"[CLIENTE {cliente_id}] É a minha vez! "
                            f"Sentei na cadeira do barbeiro."
                        )

                    elif msg == "PRONTO":
                        log(
                            f"[CLIENTE {cliente_id}] Corte finalizado! "
                            f"Valeu barbeiro!"
                        )
                        break

            else:
                log(f"[CLIENTE {cliente_id}] Mensagem inesperada: '{resposta}'")

    except ConnectionRefusedError:
        log(
            f"[CLIENTE {cliente_id}] Não consegui conectar na barbearia. "
            f"Servidor está rodando?"
        )
    except Exception as e:
        log(f"[CLIENTE {cliente_id}] Erro: {e}")