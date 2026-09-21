# `sport` — movimento

*O módulo grande: 38 comandos para fazer o robô se mexer.*

| | |
|---|---|
| **Pasta** | `unitree_sdk2py/go2/sport/` |
| **Classe** | `SportClient` |
| **Importação** | `from unitree_sdk2py.go2.sport.sport_client import SportClient` |
| **Serviço no robô** | `"sport"` |
| **Versão** | `1.0.0.1` |
| **Tamanho** | 363 linhas (o maior do `go2/`) |

Se você leu a [Anatomia](01-anatomia-de-um-client.md), já sabe o formato de
todo método aqui. Esta página é sobre **o que cada comando faz** e **em que
ordem chamá-los**.

---

## O conceito que evita 90% dos problemas: o estado do robô

O Go2 não aceita qualquer comando a qualquer momento. Ele está sempre em algum
**estado**, e os comandos disponíveis dependem dele. Mandar `Move()` num robô
deitado devolve `0` (sucesso!) e não acontece absolutamente nada.

Este é o mapa mental que você precisa:

```
        ┌──────────────┐
        │    DAMP      │   Motores soltos. O robô desaba no chão.
        │  (relaxado)  │   É o estado de repouso e de emergência.
        └──────┬───────┘
               │  StandUp()
               ▼
        ┌──────────────┐
        │   STANDING   │   De pé, pernas travadas. Rígido.
        │  (em pé)     │   NÃO anda neste estado.
        └──────┬───────┘
               │  BalanceStand()
               ▼
        ┌──────────────┐
        │   BALANCE    │   De pé se equilibrando ativamente.
        │  (ativo)     │   ◄── É AQUI que Move() funciona.
        └──────┬───────┘
               │  StandDown()  →  volta a deitar
               ▼
        ┌──────────────┐
        │  LYING DOWN  │   Deitado, mas com motores ligados.
        └──────────────┘
```

!!! tip "A receita: sempre `StandUp` → `BalanceStand` antes de andar"
    ```python
    client.StandUp()        # sai do chão
    time.sleep(1)
    client.BalanceStand()   # entra no modo que aceita movimento
    time.sleep(1)
    client.Move(0.3, 0, 0)  # agora sim
    ```
    Pular o `BalanceStand()` é o motivo mais comum de "mandei andar e ele não
    andou, mas não deu erro".

---

## Os comandos, por categoria

### Postura e estado — comece por aqui

| Método | Nº | O que faz | Cuidado |
|---|---|---|---|
| `Damp()` | 1001 | Solta os motores. O robô **desaba**. | É o freio de emergência. Segure o robô ou garanta que ele está baixo. |
| `StandUp()` | 1004 | Levanta e trava as pernas. | Precisa de espaço em volta. |
| `StandDown()` | 1005 | Deita devagar, controlado. | O jeito educado de terminar. |
| `BalanceStand()` | 1002 | Fica em pé se equilibrando. | **Obrigatório antes de andar.** |
| `RecoveryStand()` | 1006 | Se levanta depois de cair. | Funciona com o robô de lado ou de barriga para cima. |
| `Sit()` | 1009 | Senta, como um cachorro. | |
| `RiseSit()` | 1010 | Desfaz o `Sit()`. | |
| `StopMove()` | 1003 | Para o movimento imediatamente. | Não deita, só para. |

### Movimento

| Método | Nº | Assinatura |
|---|---|---|
| `Move(vx, vy, vyaw)` | 1008 | Anda com velocidade contínua. |
| `Euler(roll, pitch, yaw)` | 1007 | Inclina o corpo parado. |
| `SpeedLevel(level)` | 1015 | Ajusta a velocidade geral. |

### Marchas — o jeito de caminhar

| Método | Nº | Descrição |
|---|---|---|
| `ClassicWalk(flag)` | 2049 | Marcha padrão. |
| `StaticWalk()` | 1061 | Lenta, sempre com três pés no chão. Estável. |
| `TrotRun()` | 1062 | Trote — pares de patas diagonais. Rápida. |
| `FreeWalk()` | 2045 | Marcha livre. |
| `FreeBound(flag)` | 2046 | Saltitante, como um coelho. |
| `FreeJump(flag)` | 2047 | Com saltos. |
| `FreeAvoid(flag)` | 2048 | Anda desviando sozinho de obstáculos. |
| `WalkUpright(flag)` | 2050 | **Anda nas duas patas traseiras.** |
| `CrossStep(flag)` | 2051 | Passo cruzado. |
| `HandStand(flag)` | 2044 | **Fica de ponta-cabeça nas patas dianteiras.** |

### Acrobacias e gestos

| Método | Nº | Descrição |
|---|---|---|
| `Hello()` | 1016 | Acena com uma pata. |
| `Stretch()` | 1017 | Se espreguiça. |
| `Content()` | 1020 | Gesto de contentamento. |
| `Heart()` | 1036 | Faz um coração. |
| `Scrape()` | 1029 | Raspa o chão com a pata. |
| `Dance1()` | 1022 | Dança 1. |
| `Dance2()` | 1023 | Dança 2. |
| `Pose(flag)` | 1028 | Entra/sai do modo de poses. |
| `FrontFlip()` | 1030 | **Mortal para frente.** |
| `FrontJump()` | 1031 | **Salto para frente.** |
| `FrontPounce()` | 1032 | **Bote para frente.** |
| `LeftFlip()` | 2041 | **Mortal para a esquerda.** |
| `BackFlip()` | 2043 | **Mortal para trás.** |

### Configuração

| Método | Nº | Descrição |
|---|---|---|
| `SwitchJoystick(on)` | 1027 | Liga/desliga o controle remoto. |
| `AutoRecoverySet(enabled)` | 2054 | Liga/desliga o "levantar sozinho ao cair". |
| `AutoRecoveryGet()` | 2055 | Pergunta se está ligado. Devolve `(code, valor)`. |
| `SwitchAvoidMode()` | 2058 | Alterna o modo de desvio de obstáculos. |

!!! danger "Sobre as acrobacias"
    `FrontFlip`, `BackFlip`, `LeftFlip`, `HandStand` e `WalkUpright` exigem
    **bateria alta, piso plano e antiderrapante, e vários metros livres em todas
    as direções**. Um mortal com bateria fraca vira uma queda. O robô pesa 15 kg
    — ele machuca gente e quebra sozinho. Teste essas funções pelo aplicativo
    antes de automatizá-las, e nunca com pessoas por perto.

---

## `Move` em detalhe — o comando mais importante

```python
# unitree_sdk2py/go2/sport/sport_client.py:131
# 1008
def Move(self, vx: float, vy: float, vyaw: float):
    p = {}
    p["x"] = vx        # velocidade para frente/trás
    p["y"] = vy        # velocidade para os lados (caranguejo)
    p["z"] = vyaw      # velocidade de giro
    parameter = json.dumps(p)
    code = self._CallNoReply(SPORT_API_ID_MOVE, parameter)   # ◄── sem resposta
    return code
```

Os três eixos, do ponto de vista de quem está montado no robô:

```
                 ▲ +vx   (frente)
                 │
                 │
     +vy ◄───────┼───────► -vy
   (esquerda)    │      (direita)
                 │
                 ▼ -vx   (trás)

      +vyaw = girar no sentido anti-horário (para a esquerda)
      -vyaw = girar no sentido horário (para a direita)
```

!!! warning "As unidades não estão documentadas em lugar nenhum"
    Nem o código, nem o `README.md`, nem os comentários dizem a unidade de `vx`,
    `vy` e `vyaw`. A convenção da Unitree — e o que os exemplos sugerem pelos
    valores usados — é **metros por segundo** para `vx`/`vy` e **radianos por
    segundo** para `vyaw`. Trate isso como convenção, não como fato verificado.

    **Comece com valores pequenos: `0.2` a `0.3`.** Descubra o limite prático do
    seu robô empiricamente, num espaço aberto, aumentando aos poucos.

### O comando **persiste** até você mudá-lo

Esta é a parte que mais confunde. `Move` não é "dê um passo". É "passe a andar a
esta velocidade **e continue**". O robô mantém a última velocidade recebida até
receber outra.

A prova está no exemplo oficial (`example/obstacles_avoid/obstacles_avoid_move.py`):

```python
client.Move(0.5, 0.0, 0.0)   # começa a andar para frente
time.sleep(1.0)              # ◄── durante 1 segundo, NENHUM comando é enviado.
                             #     O robô simplesmente continua andando.
client.Move(0.0, 0.0, 0.0)   # velocidade zero = para
```

**Consequência prática:** se o seu programa morrer logo depois de um `Move`, o
robô continua andando. Por isso todo exemplo desta página termina com um
`finally`.

---

## `Euler` — inclinar o corpo sem sair do lugar

```python
# 1007
def Euler(self, roll: float, pitch: float, yaw: float):
    p = {}
    p["x"] = roll    # inclinar para os lados (como um avião fazendo curva)
    p["y"] = pitch   # inclinar para frente/trás (focinho para baixo/cima)
    p["z"] = yaw     # girar o corpo no lugar
```

Os três nomes vêm da aviação:

- **roll** — rolar para o lado, uma pata sobe e a outra desce.
- **pitch** — abaixar ou levantar o focinho.
- **yaw** — virar o corpo para a esquerda ou direita sem mover as patas.

Os valores são **ângulos em radianos** (novamente, por convenção — não está
documentado). Para converter de graus:

```python
import math
graus = 15
radianos = math.radians(graus)   # 0.2618
client.Euler(0.0, radianos, 0.0) # abaixa o focinho 15°
```

!!! note "Funciona melhor depois de `BalanceStand()`"
    Em `StandUp()` puro as pernas estão travadas e a inclinação é limitada.

---

## Exemplo 1 — levantar e deitar com segurança

O programa mínimo. **Rode este primeiro**, antes de qualquer outro.

```python
"""
Levanta o robô, espera, e deita de volta.
Uso: python3 exemplo1.py enp2s0
"""
import sys
import time

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.sport.sport_client import SportClient


def main():
    # Confirmação manual — o robô vai se mexer de verdade.
    print("O robô vai LEVANTAR. Garanta 1 metro livre em volta.")
    input("Enter para continuar, Ctrl+C para cancelar...")

    ChannelFactoryInitialize(0, sys.argv[1] if len(sys.argv) > 1 else None)

    client = SportClient()
    client.SetTimeout(3.0)
    client.Init()

    # Teste de vida: confirma que o serviço "sport" está respondendo,
    # antes de mandar qualquer coisa que mexa o robô.
    code, versao = client.GetServerApiVersion()
    if code != 0:
        print(f"Serviço 'sport' não respondeu (code={code}). Abortando.")
        return
    print("Serviço sport ativo, versão", versao)

    try:
        print("StandUp...")
        code = client.StandUp()
        print("  code =", code)
        time.sleep(3)          # dá tempo do movimento terminar

        print("BalanceStand (modo ativo)...")
        client.BalanceStand()
        time.sleep(3)

        print("StandDown...")
        client.StandDown()
        time.sleep(3)

    finally:
        # Acontece SEMPRE — inclusive com Ctrl+C no meio.
        print("Relaxando os motores...")
        client.StopMove()   # cancela qualquer movimento pendente
        client.Damp()       # solta os motores: o robô assenta no chão
        print("Fim.")


if __name__ == "__main__":
    main()
```

!!! tip "Por que os `time.sleep(3)`"
    Os métodos devolvem `code` assim que o robô **aceita** o comando, não quando
    ele **termina** o movimento. Levantar leva alguns segundos. Sem a pausa, o
    `StandDown()` chegaria no meio do `StandUp()` e o robô faria algo estranho.
    O SDK **não** oferece um jeito de perguntar "já terminou?" — você espera com
    `sleep` e pronto.

---

## Exemplo 2 — andar em quadrado

Mostra o `Move` na prática: como ele persiste, e por que zerar é obrigatório.

```python
"""
Anda um quadrado de aproximadamente 1 m de lado.
Uso: python3 exemplo2.py enp2s0
"""
import sys
import time
import math

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.sport.sport_client import SportClient

VELOCIDADE = 0.3       # ~0,3 m/s. Comece devagar.
LADO_SEGUNDOS = 3.0    # 0,3 m/s × 3 s ≈ 0,9 m
VEL_GIRO = 0.6         # ~0,6 rad/s
GIRO_SEGUNDOS = math.pi / 2 / VEL_GIRO   # tempo para girar 90°


def andar(client, vx, vy, vyaw, segundos):
    """
    Manda uma velocidade e a mantém pelo tempo pedido.

    Importante: NÃO precisamos chamar Move() repetidamente. Um único
    comando já faz o robô manter essa velocidade. O sleep só está
    segurando o programa enquanto o robô faz o trabalho.
    """
    client.Move(vx, vy, vyaw)
    time.sleep(segundos)
    client.Move(0.0, 0.0, 0.0)   # zera: o robô para
    time.sleep(0.5)              # pequena pausa para ele assentar


def main():
    print("O robô vai ANDAR UM QUADRADO de ~1 m de lado.")
    print("Precisa de uma área livre de pelo menos 3x3 metros.")
    input("Enter para continuar...")

    ChannelFactoryInitialize(0, sys.argv[1] if len(sys.argv) > 1 else None)

    client = SportClient()
    client.SetTimeout(3.0)
    client.Init()

    try:
        # Sequência obrigatória antes de andar
        client.StandUp()
        time.sleep(3)
        client.BalanceStand()    # sem isto, o Move não faz nada
        time.sleep(2)

        for lado in range(4):
            print(f"Lado {lado + 1}/4: andando para frente")
            andar(client, VELOCIDADE, 0.0, 0.0, LADO_SEGUNDOS)

            print(f"Lado {lado + 1}/4: girando 90° à esquerda")
            andar(client, 0.0, 0.0, VEL_GIRO, GIRO_SEGUNDOS)

        print("Quadrado completo.")

    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário.")

    finally:
        # Sem isto, um Ctrl+C no meio de um lado deixaria o robô
        # andando até bater em alguma coisa.
        client.Move(0.0, 0.0, 0.0)
        client.StopMove()
        client.StandDown()
        time.sleep(3)
        client.Damp()
        print("Parado com segurança.")


if __name__ == "__main__":
    main()
```

!!! warning "O quadrado não vai fechar"
    Este código anda "no tempo", não "na distância". Não há realimentação: o
    robô não sabe onde está. Piso escorregadio, bateria baixa ou o peso de um
    lidar mudam o resultado, e o quadrado sai torto. Para andar até um ponto de
    verdade você precisa de odometria — que vem do tópico `SportModeState_`
    (fora do módulo `go2/`) ou, melhor, de uma stack de navegação como a
    [da CMU](../01-links.md#stack-de-autonomia-da-cmu).

---

## Exemplo 3 — inclinando o corpo (`Euler`)

Movimento seguro e visualmente claro: o robô fica parado e só mexe o tronco.
Bom para testar a comunicação sem risco de o robô sair andando.

```python
"""
Faz o robô inclinar o corpo nos três eixos, um de cada vez.
O robô NÃO sai do lugar. É seguro num espaço pequeno.
Uso: python3 exemplo3.py enp2s0
"""
import sys
import time
import math

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.sport.sport_client import SportClient


def inclinar(client, roll_graus, pitch_graus, yaw_graus, descricao):
    """Converte graus para radianos e envia. Graus são mais fáceis de pensar."""
    print(f"  {descricao}")
    code = client.Euler(
        math.radians(roll_graus),
        math.radians(pitch_graus),
        math.radians(yaw_graus),
    )
    if code != 0:
        print(f"    falhou, code={code}")
    time.sleep(1.5)


def main():
    print("O robô vai INCLINAR O CORPO parado. Não sai do lugar.")
    input("Enter para continuar...")

    ChannelFactoryInitialize(0, sys.argv[1] if len(sys.argv) > 1 else None)

    client = SportClient()
    client.SetTimeout(3.0)
    client.Init()

    try:
        client.StandUp()
        time.sleep(3)
        client.BalanceStand()    # o Euler responde melhor neste modo
        time.sleep(2)

        print("PITCH — focinho para baixo e para cima:")
        inclinar(client, 0, 15, 0, "focinho para baixo 15°")
        inclinar(client, 0, -15, 0, "focinho para cima 15°")
        inclinar(client, 0, 0, 0, "voltando ao neutro")

        print("ROLL — rolando para os lados:")
        inclinar(client, 15, 0, 0, "rolando 15° para um lado")
        inclinar(client, -15, 0, 0, "rolando 15° para o outro")
        inclinar(client, 0, 0, 0, "voltando ao neutro")

        print("YAW — girando o tronco sem mover as patas:")
        inclinar(client, 0, 0, 15, "tronco 15° à esquerda")
        inclinar(client, 0, 0, -15, "tronco 15° à direita")
        inclinar(client, 0, 0, 0, "voltando ao neutro")

    finally:
        client.Euler(0.0, 0.0, 0.0)   # sempre volte ao neutro
        time.sleep(1)
        client.StandDown()
        time.sleep(3)
        client.Damp()


if __name__ == "__main__":
    main()
```

!!! tip "Ângulos pequenos primeiro"
    15° é conservador e seguro. O robô limita internamente o que não consegue
    fazer, mas ângulos grandes combinados (roll **e** pitch altos ao mesmo
    tempo) podem desequilibrá-lo. Aumente de 5 em 5 graus se precisar.

---

## Exemplo 4 — comparando marchas

Cada marcha é um jeito diferente de mexer as patas. Este programa deixa você
sentir a diferença andando a mesma distância com cada uma.

```python
"""
Anda para frente usando cada marcha disponível, para comparação.
Uso: python3 exemplo4.py enp2s0
"""
import sys
import time

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.sport.sport_client import SportClient

# (nome amigável, função que ativa a marcha, explicação)
MARCHAS = [
    ("Classic Walk",
     lambda c: c.ClassicWalk(True),
     "marcha padrão, equilibrada"),

    ("Static Walk",
     lambda c: c.StaticWalk(),
     "lenta, sempre 3 patas no chão — a mais estável"),

    ("Trot Run",
     lambda c: c.TrotRun(),
     "trote: patas diagonais em pares — a mais rápida"),

    ("Free Walk",
     lambda c: c.FreeWalk(),
     "marcha livre, o robô escolhe"),
]


def testar_marcha(client, nome, ativar, explicacao):
    print(f"\n--- {nome}: {explicacao}")

    code = ativar(client)
    if code != 0:
        # Nem toda marcha existe em toda versão de firmware.
        # 3203 = o robô não implementa este comando.
        print(f"    não disponível (code={code}), pulando")
        return

    time.sleep(2)                      # deixa a marcha assentar
    client.Move(0.3, 0.0, 0.0)         # anda para frente
    time.sleep(4)
    client.Move(0.0, 0.0, 0.0)         # para
    time.sleep(2)


def main():
    print("O robô vai ANDAR ~1,2 m com cada uma de 4 marchas.")
    print("Precisa de uns 3 metros livres à frente.")
    input("Enter para continuar...")

    ChannelFactoryInitialize(0, sys.argv[1] if len(sys.argv) > 1 else None)

    client = SportClient()
    client.SetTimeout(3.0)
    client.Init()

    try:
        client.StandUp()
        time.sleep(3)
        client.BalanceStand()
        time.sleep(2)

        for nome, ativar, explicacao in MARCHAS:
            testar_marcha(client, nome, ativar, explicacao)

        # Volta para a marcha padrão antes de encerrar, para não
        # deixar o robô numa marcha esquisita para o próximo usuário.
        print("\nVoltando para ClassicWalk")
        client.ClassicWalk(True)
        time.sleep(2)

    except KeyboardInterrupt:
        print("\nInterrompido.")

    finally:
        client.Move(0.0, 0.0, 0.0)
        client.StopMove()
        client.StandDown()
        time.sleep(3)
        client.Damp()


if __name__ == "__main__":
    main()
```

!!! note "Por que uns métodos têm `flag` e outros não"
    Repare na inconsistência: `ClassicWalk(True)` recebe um valor, `TrotRun()`
    não recebe nada. Olhando o código, os métodos com `flag` enviam
    `{"data": true}` e os sem `flag` enviam `{}`. Não há explicação no
    repositório para o critério. Na prática, `True` significa "ative esta
    marcha".

---

## Detalhes que só aparecem lendo o código

### Comandos que existem mas você não consegue chamar

O `Init()` registra o comando `1063` — marcha econômica:

```python
# sport_client.py:64
self._RegistApi(SPORT_API_ID_ECONOMICGAIT, 0)          # EconomicGait
```

Mas **não existe nenhum método `EconomicGait`** na classe. O número está
registrado e o comando é aceito, mas não há função que o chame. Verifiquei
comparando todos os `_RegistApi` com todos os `_Call` do arquivo: é o único
caso.

Se você quiser usá-lo, pode chamar direto:

```python
import json
from unitree_sdk2py.go2.sport.sport_api import SPORT_API_ID_ECONOMICGAIT

# _Call é "privado" (o underscore sinaliza isso), mas funciona.
# O comando já está registrado pelo Init(), então isto não dá 3103.
code, data = client._Call(SPORT_API_ID_ECONOMICGAIT, json.dumps({}))
print("EconomicGait code:", code)
```

!!! warning
    Isso é uma gambiarra deliberada. Como não há documentação, não sei se o
    comando espera parâmetros. Se devolver `3204` (parâmetro inválido), ele
    precisa de algo que não sabemos. Teste com cuidado.

### `PathPoint`: código morto

No topo do `sport_client.py` do Go2 existem uma constante e uma classe:

```python
SPORT_PATH_POINT_SIZE = 30

class PathPoint:
    def __init__(self, timeFromStart, x, y, yaw, vx, vy, vyaw):
        ...
```

Elas dão a entender que dá para mandar uma trajetória completa para o robô
seguir. **Não dá — não no Go2.** Procurei em todo o arquivo: nenhum método usa
`PathPoint`. O método que a usaria, `TrajectoryFollow`, existe no cliente de
**outro robô** (`unitree_sdk2py/b2/sport/sport_client.py:127`), não no do Go2.

O exemplo oficial `example/go2/high_level/go2_sport_client.py` chega a importar
as duas e nunca as utiliza:

```python
from unitree_sdk2py.go2.sport.sport_client import (
    SportClient,
    PathPoint,             # ◄── importado e nunca usado
    SPORT_PATH_POINT_SIZE, # ◄── idem
)
```

O código de erro `SPORT_ERR_CLIENT_POINT_PATH = 4101` ("trajetória inválida")
existe pelo mesmo motivo e nunca é disparado no Go2.

**Conclusão:** para seguir uma trajetória no Go2, você monta o laço de `Move`
você mesmo, ou usa uma stack de navegação.

### `Move` é o único método de movimento sem confirmação

Já visto na [Anatomia](01-anatomia-de-um-client.md#_callnoreply-envia-e-nao-espera),
mas vale repetir aqui: `Move` usa `_CallNoReply`. Ele devolve `0` mesmo se o
robô estiver deitado, desligado ou com o serviço parado. **`Move` não é um teste
de conectividade.** Use `GetServerApiVersion()` para isso.

---

## Resumo prático

```python
# 1. Ligar
ChannelFactoryInitialize(0, "enp2s0")
client = SportClient(); client.SetTimeout(3.0); client.Init()

# 2. Conferir
code, v = client.GetServerApiVersion()      # 0 = tudo bem

# 3. Preparar para andar (nesta ordem!)
client.StandUp();      time.sleep(3)
client.BalanceStand(); time.sleep(2)

# 4. Andar (persiste até você zerar)
client.Move(0.3, 0.0, 0.0); time.sleep(2)
client.Move(0.0, 0.0, 0.0)

# 5. Encerrar (sempre num finally)
client.StopMove()
client.StandDown(); time.sleep(3)
client.Damp()
```

---

**Próximo:** [`video` — câmera frontal](03-video.md) ·
[voltar ao índice](index.md)
