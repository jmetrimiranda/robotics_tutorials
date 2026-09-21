# `obstacles_avoid` — desvio de obstáculos

*Andar deixando o robô decidir como não bater.*

| | |
|---|---|
| **Pasta** | `unitree_sdk2py/go2/obstacles_avoid/` |
| **Classe** | `ObstaclesAvoidClient` |
| **Importação** | `from unitree_sdk2py.go2.obstacles_avoid.obstacles_avoid_client import ObstaclesAvoidClient` |
| **Serviço no robô** | `"obstacles_avoid"` |
| **Versão** | `1.0.0.2` ← a mais nova dos cinco módulos |
| **Tamanho** | 79 linhas |

---

## O que este módulo faz

Existe um programa dentro do robô que lê o lidar e o mantém longe de paredes,
móveis e pessoas. Este módulo é o **interruptor e o volante** desse programa:

- **Interruptor** — `SwitchSet` / `SwitchGet` ligam e desligam o desvio.
- **Volante** — `Move` e suas variantes mandam o robô para algum lugar, e o
  programa do robô resolve *como* chegar lá sem bater.

A diferença para o [módulo `sport`](02-sport.md) é essa: no `sport` você diz
exatamente como o robô deve se mover, e ele obedece mesmo que vá bater numa
parede. Aqui, você diz **onde quer chegar** e o robô tem permissão de desviar do
caminho.

---

## Os quatro comandos

| Método | Nº | O que faz |
|---|---|---|
| `SwitchSet(on)` | 1001 | Liga (`True`) ou desliga (`False`) o desvio. |
| `SwitchGet()` | 1002 | Pergunta se está ligado. Devolve `(code, True/False)`. |
| `Move(vx, vy, vyaw)` | 1003 | Anda com velocidade, desviando. |
| `UseRemoteCommandFromApi(bool)` | 1004 | **Transfere o comando do controle remoto para o seu código.** |

E mais dois métodos que reaproveitam o número 1003 com um campo diferente:

| Método | Nº | O que faz |
|---|---|---|
| `MoveToIncrementPosition(x, y, yaw)` | 1003 | Vá **para um ponto relativo** a onde você está agora. |
| `MoveToAbsolutePosition(x, y, yaw)` | 1003 | Vá **para um ponto fixo** no mapa do robô. |

---

## O campo escondido: `mode`

Os três métodos de movimento chamam **o mesmo comando 1003**. O que os
diferencia é um campo chamado `mode`, que o SDK preenche sozinho e não
documenta em lugar nenhum:

```python
# obstacles_avoid_client.py:44
def Move(self, vx, vy, vyaw):
    p["x"] = vx; p["y"] = vy; p["yaw"] = vyaw
    p["mode"] = 0                      # ◄── modo VELOCIDADE
    code = self._CallNoReply(OBSTACLES_AVOID_API_ID_MOVE, json.dumps(p))

# obstacles_avoid_client.py:72
def MoveToIncrementPosition(self, vx, vy, vyaw):
    p["x"] = vx; p["y"] = vy; p["yaw"] = vyaw
    p["mode"] = 1                      # ◄── modo POSIÇÃO RELATIVA

# obstacles_avoid_client.py:62
def MoveToAbsolutePosition(self, vx, vy, vyaw):
    p["x"] = vx; p["y"] = vy; p["yaw"] = vyaw
    p["mode"] = 2                      # ◄── modo POSIÇÃO ABSOLUTA
```

Traduzindo os três modos:

| `mode` | Método | Os três números significam | Analogia |
|---|---|---|---|
| **0** | `Move` | **velocidades** — quão rápido ir | "ande para frente a 0,5 m/s" |
| **1** | `MoveToIncrementPosition` | **distâncias** a partir daqui | "ande 2 metros para frente" |
| **2** | `MoveToAbsolutePosition` | **coordenadas** fixas | "vá para o ponto (3, 1) do mapa" |

!!! warning "Os nomes dos parâmetros estão errados nos modos 1 e 2"
    Olhe a assinatura:

    ```python
    def MoveToAbsolutePosition(self, vx: float, vy: float, vyaw: float):
    ```

    O `v` em `vx` significa *velocidade*. Mas neste método os valores **não são
    velocidades** — são posições, em metros e radianos. O nome foi copiado do
    `Move` e nunca ajustado.

    Leia como se fosse `MoveToAbsolutePosition(x, y, yaw)`. Se você passar
    `0.3` achando que é "devagar", vai mandar o robô para o ponto a 30
    centímetros da origem.

!!! note "Sobre o modo 2 (posição absoluta)"
    "Absoluta" em relação a quê? O robô mantém uma noção interna de onde está,
    construída desde que ligou. Essa referência **não sobrevive a um
    reinício** e acumula erro com o tempo. Não trate como coordenada de mapa
    confiável. Para navegação séria, use uma stack com SLAM, como a
    [da CMU](../01-links.md#stack-de-autonomia-da-cmu).

---

## `UseRemoteCommandFromApi` — a chave que quase todo mundo esquece

Este é o método menos óbvio do SDK inteiro, e sem ele os `Move` deste módulo
não funcionam.

```python
# obstacles_avoid_client.py:55
def UseRemoteCommandFromApi(self, isRemoteCommandsFromApi: bool):
    p["is_remote_commands_from_api"] = isRemoteCommandsFromApi
    code, data = self._Call(OBSTACLES_AVOID_API_ID_USE_REMOTE_COMMAND_FROM_API, ...)
```

**O que faz, em português:** o serviço de desvio normalmente obedece ao controle
remoto físico. Chamar `UseRemoteCommandFromApi(True)` diz a ele: *"a partir de
agora, ignore o controle remoto e obedeça aos comandos que chegam pelo
programa"*.

Pense num carro com piloto automático: `True` é apertar o botão que transfere o
volante para o computador. `False` devolve para o motorista.

A ordem correta, extraída do exemplo oficial
(`example/obstacles_avoid/obstacles_avoid_move.py`):

```python
client.SwitchSet(True)               # 1. liga o desvio
client.UseRemoteCommandFromApi(True) # 2. pega o volante
time.sleep(0.5)                      # 3. dá meio segundo para assentar
client.Move(0.5, 0.0, 0.0)           # 4. agora os comandos funcionam
# ...
client.Move(0.0, 0.0, 0.0)           # 5. para
client.UseRemoteCommandFromApi(False)# 6. DEVOLVE o volante
```

!!! danger "Sempre devolva o volante"
    Se o seu programa terminar sem chamar `UseRemoteCommandFromApi(False)`, o
    robô pode ficar ignorando o controle remoto. Você perde o jeito mais rápido
    de pará-lo manualmente. Coloque essa chamada num bloco `finally`, sempre.

---

## Os dois `Move` do SDK

Existem dois métodos chamados `Move` em módulos diferentes, e eles **não são a
mesma coisa**. Confundi-los é uma fonte real de bugs.

| | `SportClient.Move` | `ObstaclesAvoidClient.Move` |
|---|---|---|
| Arquivo | `sport/sport_client.py:132` | `obstacles_avoid/..._client.py:45` |
| Comando | 1008, serviço `"sport"` | 1003, serviço `"obstacles_avoid"` |
| Campos enviados | `{"x", "y", "z"}` | `{"x", "y", "yaw", "mode"}` |
| Desvia de obstáculos? | **Não.** Vai bater. | Sim. |
| Precisa de `BalanceStand()` antes? | Sim | Não |
| Precisa de `UseRemoteCommandFromApi`? | Não | **Sim** |

Repare inclusive que o terceiro campo tem nome diferente: `"z"` num, `"yaw"` no
outro. São dois serviços distintos dentro do robô, com protocolos distintos.

!!! tip "Qual usar?"
    - **`sport.Move`** — quando você quer controle preciso e já está cuidando
      dos obstáculos por conta própria (com sua própria stack de navegação, por
      exemplo).
    - **`obstacles_avoid.Move`** — quando você quer o robô andando com
      segurança sem escrever lógica de desvio. É o modo "à prova de tropeço".

---

## Exemplo 1 — ligar o desvio e confirmar

O mais seguro: **o robô não sai do lugar**. Só liga o serviço e confirma.
Comece por aqui.

```python
"""
Liga o desvio de obstáculos e confirma que ligou.
O robô NÃO se move.
Uso: python3 liga_desvio.py enp2s0
"""
import sys
import time

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.obstacles_avoid.obstacles_avoid_client import (
    ObstaclesAvoidClient,
)


def estado_do_desvio(client):
    """Devolve True, False ou None (se não conseguiu perguntar)."""
    code, ligado = client.SwitchGet()
    if code != 0:
        print(f"  não consegui perguntar. code = {code}")
        return None
    return ligado


def main():
    ChannelFactoryInitialize(0, sys.argv[1] if len(sys.argv) > 1 else None)

    client = ObstaclesAvoidClient()
    client.SetTimeout(3.0)
    client.Init()

    print("Estado atual do desvio:", estado_do_desvio(client))

    print("\nLigando...")
    code = client.SwitchSet(True)
    print("  SwitchSet(True) devolveu code =", code)

    # O serviço demora um instante para de fato mudar de estado.
    # Perguntar imediatamente pode devolver o valor antigo.
    # Por isso tentamos algumas vezes, em vez de confiar numa só.
    for tentativa in range(10):
        time.sleep(0.2)
        if estado_do_desvio(client) is True:
            print(f"  confirmado ligado (após {tentativa + 1} tentativas)")
            break
    else:
        # 'else' de um 'for' roda quando o laço termina SEM break.
        print("  não confirmou depois de 10 tentativas.")
        return

    time.sleep(2)

    print("\nDesligando de volta...")
    client.SwitchSet(False)
    time.sleep(1)
    print("Estado final:", estado_do_desvio(client))


if __name__ == "__main__":
    main()
```

!!! note "O laço de confirmação não é paranoia"
    O exemplo oficial faz a mesma coisa, de forma mais agressiva:

    ```python
    while not client.SwitchGet()[1]:     # enquanto não estiver ligado
        client.SwitchSet(True)           # insiste
        time.sleep(0.1)
    ```

    Esse laço do original tem um risco: se `SwitchGet` falhar, ele devolve
    `(code, None)`, `not None` é `True`, e o laço gira para sempre. A versão
    acima tem um limite de tentativas.

---

## Exemplo 2 — andar com o desvio ativo

Agora o robô se move. Ele vai andar para frente, e se houver um obstáculo no
caminho, deve desviar ou parar sozinho.

```python
"""
Anda para frente por alguns segundos com o desvio de obstáculos ligado.
Uso: python3 anda_com_desvio.py enp2s0
"""
import sys
import time

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.obstacles_avoid.obstacles_avoid_client import (
    ObstaclesAvoidClient,
)

VELOCIDADE = 0.4     # devagar
DURACAO = 5.0        # segundos andando


def main():
    print("O robô vai ANDAR PARA FRENTE com desvio de obstáculos ligado.")
    print("Deixe pelo menos 4 metros livres à frente.")
    print("O robô deve desviar de obstáculos — mas NÃO confie nisso cegamente.")
    input("Enter para continuar, Ctrl+C para cancelar...")

    ChannelFactoryInitialize(0, sys.argv[1] if len(sys.argv) > 1 else None)

    client = ObstaclesAvoidClient()
    client.SetTimeout(3.0)
    client.Init()

    try:
        # --- 1. Liga o desvio ------------------------------------------
        print("Ligando o desvio...")
        client.SwitchSet(True)

        for _ in range(20):
            time.sleep(0.1)
            code, ligado = client.SwitchGet()
            if code == 0 and ligado:
                break
        else:
            print("Desvio não ligou. Abortando por segurança.")
            return
        print("  desvio ativo.")

        # --- 2. Assume o controle --------------------------------------
        # Sem esta linha, os Move abaixo não têm efeito.
        print("Assumindo o comando (o controle remoto fica inativo)...")
        client.UseRemoteCommandFromApi(True)
        time.sleep(0.5)

        # --- 3. Anda ----------------------------------------------------
        print(f"Andando a {VELOCIDADE} por {DURACAO}s...")
        client.Move(VELOCIDADE, 0.0, 0.0)
        time.sleep(DURACAO)

        # --- 4. Para ----------------------------------------------------
        print("Parando.")
        client.Move(0.0, 0.0, 0.0)
        time.sleep(1.0)

    except KeyboardInterrupt:
        print("\nInterrompido.")

    finally:
        # Este bloco é a parte mais importante do programa.
        # Roda mesmo com Ctrl+C, mesmo com exceção.
        print("Encerrando com segurança...")
        client.Move(0.0, 0.0, 0.0)             # zera a velocidade
        client.UseRemoteCommandFromApi(False)  # DEVOLVE o controle remoto
        print("Controle remoto reativado.")


if __name__ == "__main__":
    main()
```

!!! danger "O desvio não é infalível"
    O lidar embutido tem pontos cegos e dificuldade com obstáculos baixos,
    finos (pés de cadeira), transparentes (vidro) e muito escuros. A
    [stack da CMU](../01-links.md#stack-de-autonomia-da-cmu) chega a documentar
    que obstáculos precisam ter mais de ~0,3 m de altura para serem detectados
    com confiança pelo lidar L1.

    Mantenha sempre o controle remoto ao alcance da mão e uma pessoa pronta
    para desligar. Nunca teste com pessoas ou animais na trajetória.

---

## Exemplo 3 — ir até um ponto (posição relativa)

Mostra o `mode = 1`: em vez de dizer "ande a tantos metros por segundo", você
diz "ande 2 metros para frente" e o robô resolve o resto.

```python
"""
Manda o robô percorrer um caminho em L, usando posições relativas.
Uso: python3 caminho_em_l.py enp2s0
"""
import sys
import time
import math

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.obstacles_avoid.obstacles_avoid_client import (
    ObstaclesAvoidClient,
)

# Cada passo: (x_metros, y_metros, yaw_radianos, descrição, segundos_de_espera)
# ATENÇÃO: aqui os números são DISTÂNCIAS, não velocidades — apesar do
# nome dos parâmetros do método ser vx, vy, vyaw.
CAMINHO = [
    (1.5,  0.0, 0.0,            "1,5 m para frente",      12),
    (0.0,  0.0, math.pi / 2,    "girar 90° à esquerda",    8),
    (1.0,  0.0, 0.0,            "1,0 m para frente",      10),
]


def main():
    print("O robô vai percorrer um caminho em L de ~2,5 m.")
    print("Precisa de uma área livre de uns 4x4 metros.")
    input("Enter para continuar...")

    ChannelFactoryInitialize(0, sys.argv[1] if len(sys.argv) > 1 else None)

    client = ObstaclesAvoidClient()
    client.SetTimeout(3.0)
    client.Init()

    try:
        client.SwitchSet(True)
        time.sleep(1.0)

        code, ligado = client.SwitchGet()
        if code != 0 or not ligado:
            print("Desvio não ligou. Abortando.")
            return

        client.UseRemoteCommandFromApi(True)
        time.sleep(0.5)

        for x, y, yaw, descricao, espera in CAMINHO:
            print(f"→ {descricao}")

            # mode = 1: "mova-se ESTA distância a partir de onde você está"
            client.MoveToIncrementPosition(x, y, yaw)

            # Não há como perguntar "já chegou?". O SDK não oferece isso.
            # Esperamos um tempo generoso e seguimos.
            time.sleep(espera)

        print("Caminho concluído.")

    except KeyboardInterrupt:
        print("\nInterrompido.")

    finally:
        client.Move(0.0, 0.0, 0.0)
        client.UseRemoteCommandFromApi(False)
        print("Encerrado. Controle remoto reativado.")


if __name__ == "__main__":
    main()
```

!!! warning "Não existe 'já cheguei?'"
    Esta é a maior limitação do módulo. `MoveToIncrementPosition` usa
    `_CallNoReply` — dispara e esquece. Não há retorno de progresso, não há
    evento de conclusão, não há como perguntar a distância restante.

    Os `time.sleep()` acima são chutes calibrados na mão. Se o robô desviar de
    um obstáculo no caminho, vai demorar mais e o próximo comando chegará no
    meio do percurso anterior, cancelando-o.

    **Para saber onde o robô realmente está**, você precisa assinar o tópico de
    estado `SportModeState_` — que fica fora do módulo `go2/`, em
    `unitree_sdk2py/idl/`. É outro assunto, e é o ponto em que vale considerar
    migrar para ROS 2 e uma stack de navegação de verdade.

---

## Resumo prático

```python
client = ObstaclesAvoidClient()
client.SetTimeout(3.0)
client.Init()

client.SwitchSet(True)                  # 1. liga o desvio
time.sleep(1)
client.UseRemoteCommandFromApi(True)    # 2. assume o controle  ◄── não esqueça
time.sleep(0.5)

client.Move(0.4, 0.0, 0.0)              # 3. anda (mode 0: velocidade)
time.sleep(5)
client.Move(0.0, 0.0, 0.0)              # 4. para

client.UseRemoteCommandFromApi(False)   # 5. devolve o controle ◄── no finally!
```

| Armadilha | Sintoma |
|---|---|
| Esquecer `UseRemoteCommandFromApi(True)` | `Move` devolve 0 e o robô não anda |
| Esquecer `UseRemoteCommandFromApi(False)` | Controle remoto fica inerte depois |
| Usar `MoveToAbsolutePosition(0.3, 0, 0)` achando que é devagar | O robô vai para o ponto a 30 cm da origem |
| Confundir com `sport.Move` | Protocolo diferente; não desvia de nada |

---

**Próximo:** [`vui` — luz e som](05-vui.md) · [voltar ao índice](index.md)
