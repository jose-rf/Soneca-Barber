# 💈 Soneca Barber — Simulação com Processos Distribuídos

Trabalho da disciplina de **Sistemas Distribuídos** — UEMG, Sistemas de Informação  
Implementação do problema clássico do **Barbeiro Dorminhoco** usando comunicação entre programas via **sockets TCP**.

## 👥 Grupo

Alunos: José Rodrigues, Julia Alves e Maria Fernanda Mariano

---

## 📋 Descrição do Problema

A barbearia **Soneca Barber** tem um barbeiro que adora dormir. Quando não há clientes, ele dorme na cadeira. Ao chegar um cliente, este o acorda aos gritos. Se as **3 cadeiras de espera** estiverem ocupadas, o cliente vai embora.

### Situações demonstradas

| # | Situação |
|---|----------|
| 1 | Abertura da barbearia: todas as cadeiras vazias e o barbeiro dormindo |
| 2 | Clientes chegam, barbeiro acorda e atende; cadeiras de espera são ocupadas |
| 3 | Cliente chega com todas as cadeiras de espera ocupadas e vai embora |

---

## 🛠️ Tecnologias

- **Python 3.x**
- `socket` — comunicação entre programas via TCP
- `threading` — gerenciamento de múltiplas conexões no servidor
- Sem dependências externas

---

## 🏗️ Arquitetura

A solução é composta por **dois programas independentes** que se comunicam exclusivamente via **troca de mensagens por sockets TCP**, sem nenhuma memória compartilhada entre eles — seguindo o modelo real de sistemas distribuídos.

```
[ cliente.py 1 ] ──┐
[ cliente.py 2 ] ──┼──► socket TCP (porta 65432) ──► [ barbeiro.py ]
[ cliente.py N ] ──┘
```

### Programas

- **`barbeiro.py`** — servidor TCP; aguarda conexões de clientes, gerencia a fila de espera e simula o atendimento
- **`cliente.py`** — cliente TCP; cada instância é um programa separado que se conecta ao barbeiro e aguarda resposta

### Protocolo de mensagens

| Quem envia | Mensagem | Significado |
|---|---|---|
| Cliente → Barbeiro | `CHEGOU:<id>` | cliente chegou na barbearia |
| Barbeiro → Cliente | `SENTE` | tem vaga, pode sentar e esperar |
| Barbeiro → Cliente | `CHEIO` | sem vagas, vai embora |
| Barbeiro → Cliente | `ATENDENDO` | é a sua vez na cadeira |
| Barbeiro → Cliente | `PRONTO` | corte finalizado, pode ir |

---

## ▶️ Como executar

**Pré-requisito:** Python 3.x instalado

**Terminal 1 — inicia o barbeiro (servidor):**
```bash
python barbeiro.py
```

**Terminais 2, 3, 4... — cada cliente em um terminal separado:**
```bash
python cliente.py 1
python cliente.py 2
python cliente.py 3
python cliente.py 4
python cliente.py 5
```

> Para demonstrar a situação 3 (barbearia cheia), abra os 5 terminais rapidamente antes do barbeiro terminar o primeiro corte.

### Saída esperada

**barbeiro.py:**
```
============================================================
       SONECA BARBER - Servidor do Barbeiro
       Escutando em 127.0.0.1:65432
       Cadeiras de espera: 3
============================================================

[BARBEIRO] Barbearia aberta. Barbeiro dormindo... 💤
[SERVIDOR] Aguardando clientes...

[BARBEIRO] Mensagem recebida: 'CHEGOU:1' de ('127.0.0.1', 64575)
[BARBEIRO] Cliente 1 entrou na fila de espera. (1/3 cadeiras ocupadas)
[BARBEIRO] Chamando Cliente 1. PRÓXIMO!
[BARBEIRO] Cortando o cabelo do Cliente 1...
[BARBEIRO] Cliente 2 entrou na fila de espera. (1/3 cadeiras ocupadas)
[BARBEIRO] Cliente 3 entrou na fila de espera. (2/3 cadeiras ocupadas)
[BARBEIRO] Cliente 4 entrou na fila de espera. (3/3 cadeiras ocupadas)
[BARBEIRO] Sem vagas! Mandando Cliente 5 embora.
[BARBEIRO] Pronto! Cliente 1 atendido.
...
[BARBEIRO] Fila vazia. Voltando a dormir... 💤
```

**cliente.py 5 (barbearia cheia):**
```
[CLIENTE 5] Chegando na barbearia...
[CLIENTE 5] Mensagem enviada: 'CHEGOU:5'
[CLIENTE 5] Resposta recebida: 'CHEIO'
[CLIENTE 5] Todas as cadeiras ocupadas. Vou embora! 😒
```

---

## ⚙️ Configurações

As constantes no início de `barbeiro.py` permitem ajustar o comportamento:

```python
MAX_ESPERA  = 3    # número de cadeiras de espera
TEMPO_CORTE = 10   # segundos simulando a duração de um corte
PORT        = 65432
```

---

**Disciplina:** Sistemas Distribuídos  
**Instituição:** UEMG — Universidade do Estado de Minas Gerais  
**Entrega:** 28/06/2026
