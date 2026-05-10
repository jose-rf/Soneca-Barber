# 💈 Soneca Barber — Simulação com Processos Distribuídos

Trabalho da disciplina de **Sistemas Distribuídos** — UEMG, Sistemas de Informação  
Implementação do problema clássico do **Barbeiro Dorminhoco** usando troca de mensagens entre processos.

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
- `multiprocessing` — criação de processos e comunicação via `Queue`
- Sem dependências externas

---

## 🏗️ Arquitetura

A comunicação entre processos é feita exclusivamente por **troca de mensagens** através de uma `Queue` compartilhada, seguindo o modelo de sistemas distribuídos.

```
Cliente 1 ──┐
Cliente 2 ──┼──► Queue (fila de espera) ──► Processo Barbeiro
Cliente N ──┘
                        ▲
                   Lock (exclusão mútua nas variáveis de estado)
```

### Processos

- **`barbeiro_process`** — fica aguardando mensagens na fila; dorme quando está vazia
- **`cliente_process`** — cada cliente é um processo independente; verifica vagas antes de entrar
- **`log_process`** — processo auxiliar que centraliza os prints para evitar sobreposição de saída

### Variáveis compartilhadas

| Variável | Tipo | Descrição |
|----------|------|-----------|
| `fila_espera` | `Queue` | Canal de mensagens entre clientes e barbeiro |
| `cadeiras_ocupadas` | `Value('i')` | Contador de cadeiras de espera em uso |
| `barbeiro_dormindo` | `Value('b')` | Flag de estado do barbeiro |
| `barbeiro_ocupado` | `Value('b')` | Flag se barbeiro está atendendo |
| `lock` | `Lock` | Garante exclusão mútua no acesso às variáveis |

---

## ▶️ Como executar

**Pré-requisito:** Python 3.x instalado

```bash
python soneca_barber.py
```

### Saída esperada

```
============================================================
       SONECA BARBER - Simulação Sistemas Distribuídos
============================================================

>>> SITUAÇÃO 1: Abrindo a barbearia

[BARBEARIA] Abrindo... Barbeiro sentou na cadeira e dormiu. 💤

>>> SITUAÇÃO 2: Clientes chegando em sequência rápida

[CLIENTE 1] Cheguei e o barbeiro tava dormindo. ACORDA! Hora de trabalhar seu dorminhoco! 😤
[BARBEIRO] *esfregando os olhos* Ugh... acordei porque o Cliente 1 gritou ACORDA!
[BARBEIRO] Atendendo o Cliente 1... (cadeiras de espera livres: 3)
[CLIENTE 2] Cheguei, barbeiro ocupado. Sentei na cadeira de espera. (1/3 cadeiras ocupadas)
[CLIENTE 3] Cheguei, barbeiro ocupado. Sentei na cadeira de espera. (2/3 cadeiras ocupadas)
[CLIENTE 4] Cheguei, barbeiro ocupado. Sentei na cadeira de espera. (3/3 cadeiras ocupadas)

>>> SITUAÇÃO 3: Cliente tentando entrar com barbearia cheia

[CLIENTE 99] Cheguei mas todas as 3 cadeiras de espera estão ocupadas. Vou embora! 😒
...
[BARBEIRO] Fila vazia... voltando a dormir. 💤
```

---

## ⚙️ Configurações

As constantes no início do arquivo permitem ajustar o comportamento da simulação:

```python
MAX_ESPERA   = 3    # número de cadeiras de espera
TEMPO_CORTE  = 1.5  # segundos simulando a duração de um corte
TEMPO_CHEGADA = 0.8 # intervalo base entre chegadas de clientes
```

---

## 👥 Grupo



**Disciplina:** Sistemas Distribuídos  
**Instituição:** UEMG — Universidade do Estado de Minas Gerais  
**Entrega:** 29/06/2026
