# Anatomia de um client

*Entenda um, entendeu os cinco.*

Os cinco módulos de `unitree_sdk2py/go2/` são **o mesmo código** com nomes
diferentes. Esta página disseca esse código uma vez, em detalhe, para que as
páginas seguintes possam falar só do que é específico de cada módulo.

---

## A ideia central: você manda um pedido, o robô responde

Dentro do Go2 rodam vários programinhas independentes. Um cuida de andar, outro
da câmera, outro do led. Cada um desses programinhas é chamado de **serviço**.

Seu código em Python não "controla" o robô diretamente. Ele **pede** alguma
coisa a um desses serviços e espera a resposta — igual a pedir num balcão:

```
     SEU PC                                    DENTRO DO ROBÔ
  ┌───────────┐                            ┌──────────────────┐
  │           │   "comando 1004, sem       │                  │
  │  Python   │────  parâmetros"──────────►│ serviço "sport"  │
  │           │                            │                  │
  │           │◄─── "code = 0" ────────────│ (e o robô        │
  └───────────┘      (deu certo)           │  levanta)        │
                                           └──────────────────┘
```

Cada comando tem um **número**. `1004` é "levante". `1005` é "deite". A classe
`SportClient` existe só para você poder escrever `StandUp()` em vez de decorar
que levantar é 1004.

!!! note "O nome disso"
    Esse jeito de trabalhar — chamar uma função que na verdade roda em outra
    máquina — tem o nome técnico de **RPC** (*Remote Procedure Call*, chamada de
    procedimento remoto). Você vai ver a pasta `unitree_sdk2py/rpc/` no
    repositório; é onde mora esse encanamento. Não precisa entender a pasta para
    usar o SDK, mas é bom saber por que ela existe.

---

## As quatro linhas que todo programa repete

Abra qualquer exemplo do repositório. Todos começam igual:

```python
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.sport.sport_client import SportClient

ChannelFactoryInitialize(0, "enp2s0")   # 1. abre a comunicação
client = SportClient()                  # 2. cria o cliente
client.SetTimeout(3.0)                  # 3. define a paciência
client.Init()                           # 4. registra os comandos
```

Vamos uma por uma, porque cada uma tem uma armadilha.

### 1. `ChannelFactoryInitialize(0, "enp2s0")`

Liga o "rádio". Prepara toda a infraestrutura de rede que o SDK usa para
conversar com o robô.

```python
# assinatura real, de unitree_sdk2py/core/channel.py:298
def ChannelFactoryInitialize(id: int = 0, networkInterface: str = None):
```

- **`id`** — sempre `0`. É um número que separa robôs diferentes na mesma rede
  (o nome técnico é *domínio*). Se você tem um robô só, é 0.
- **`networkInterface`** — o nome da placa de rede do **seu computador** que
  está ligada ao robô. Não é o IP do robô: é o nome da interface, tipo
  `enp2s0`, `eth0` ou `enx00e04c68...`.

Para descobrir o nome da sua:

```bash
ip addr
# procure a interface que tem um IP na faixa 192.168.123.x
```

!!! warning "Chame uma vez só, e antes de tudo"
    `ChannelFactoryInitialize` é global. Chame **uma vez** no início do
    programa. Se você criar um cliente antes de chamá-la, o cliente não vai
    funcionar. Se chamar duas vezes, ela levanta uma exceção
    (`Exception: channel factory init error.`).

!!! tip "Rodando dentro do próprio robô"
    Se o seu código roda no computador de bordo do Go2 (ou no Jetson Orin
    acoplado), você pode omitir a interface: `ChannelFactoryInitialize(0)`.
    É por isso que todos os exemplos têm aquele `if len(sys.argv) > 1`.

### 2. `client = SportClient()`

Cria o objeto. Aqui ainda não aconteceu nada de rede.

Repare no construtor real:

```python
# unitree_sdk2py/go2/sport/sport_client.py:29
class SportClient(Client):
    def __init__(self, enableLease: bool = False):
        super().__init__(SPORT_SERVICE_NAME, enableLease)
        #               └─ "sport", o endereço do serviço dentro do robô
```

Todos os cinco clientes fazem exatamente isso: passam o nome do seu serviço para
a classe-mãe `Client`. A diferença entre eles é só o nome.

O `enableLease` é explicado [mais abaixo](#o-lease-a-trava-de-exclusividade).
Só o `SportClient` oferece essa opção; os outros quatro passam `False` fixo.

### 3. `client.SetTimeout(3.0)`

Quantos segundos esperar por uma resposta antes de desistir. Se o robô não
responder em 3 segundos, o método devolve o código `3104` em vez de travar seu
programa para sempre.

Três segundos é o valor usado em todos os exemplos oficiais. É um bom padrão.

### 4. `client.Init()` — **a linha que todo mundo esquece**

Esta é a armadilha número um do SDK. Sem `Init()`, **nenhum comando funciona**,
e a mensagem de erro não ajuda em nada.

O que `Init()` faz é montar uma lista interna de comandos permitidos:

```python
# unitree_sdk2py/go2/sport/sport_client.py:34
def Init(self):
    self._SetApiVerson(SPORT_API_VERSION)        # anota a versão: "1.0.0.1"

    self._RegistApi(SPORT_API_ID_DAMP, 0)        # "1001 é permitido"
    self._RegistApi(SPORT_API_ID_BALANCESTAND, 0)# "1002 é permitido"
    self._RegistApi(SPORT_API_ID_STOPMOVE, 0)    # "1003 é permitido"
    # ... mais 35 linhas iguais
```

E `_RegistApi` é literalmente uma linha, anotando num dicionário:

```python
# unitree_sdk2py/rpc/client.py:95
def _RegistApi(self, apiId: int, proirity: int):
    self.__apiMapping[apiId] = proirity
```

(Sim, está escrito `proirity`. O erro de digitação está no código original.)

Depois, toda vez que você chama um método, ele confere essa lista:

```python
# unitree_sdk2py/rpc/client.py:98 (simplificado)
def __CheckApi(self, apiId):
    proirity = self.__apiMapping.get(apiId)
    if proirity is None:
        return RPC_ERR_CLIENT_API_NOT_REG, ...   # ◄── 3103
```

**Se você esquecer o `Init()`, o dicionário está vazio, e todo comando devolve
`3103` sem nem tentar falar com o robô.** Nada é enviado pela rede. O robô nem
fica sabendo. Você fica olhando para um número achando que é problema de cabo.

---

## O corpo de um método: sempre as mesmas cinco linhas

Peguei o método mais simples do SDK inteiro, o `StandUp`:

```python
# unitree_sdk2py/go2/sport/sport_client.py:100
# 1004
def StandUp(self):
    p = {}                                    # 1. dicionário de parâmetros
    parameter = json.dumps(p)                 # 2. vira texto: "{}"
    code, data = self._Call(SPORT_API_ID_STANDUP, parameter)   # 3. envia
    return code                               # 4. devolve só o código
```

E um que tem parâmetros, o `Euler` (inclinar o corpo parado):

```python
# unitree_sdk2py/go2/sport/sport_client.py:121
# 1007
def Euler(self, roll: float, pitch: float, yaw: float):
    p = {}
    p["x"] = roll     # ◄── ATENÇÃO: o nome que vai na mensagem é "x",
    p["y"] = pitch    #     não "roll". O robô espera x/y/z.
    p["z"] = yaw
    parameter = json.dumps(p)   # vira: '{"x": 0.1, "y": 0.0, "z": 0.0}'
    code, data = self._Call(SPORT_API_ID_EULER, parameter)
    return code
```

É isso. **Todo** método do módulo `go2/` é uma variação dessas cinco linhas:
monta um dicionário, converte para texto, envia, devolve o código.

!!! tip "Por que isso é uma boa notícia"
    Como o padrão nunca muda, ler o código-fonte é rápido e confiável. Quando
    você quiser saber o que um método faz de verdade, abra o arquivo: em cinco
    linhas você vê exatamente qual número é enviado e quais campos vão junto.
    É mais rápido do que procurar na página de suporte.

---

## As três formas de enviar

Olhando os cinco módulos, só três funções de envio são usadas.

### `_Call` — envia e **espera** resposta

```python
code, data = self._Call(API_ID, parameter)
```

Devolve **dois** valores: o código e os dados de resposta (em texto). A maioria
dos métodos ignora o `data` e devolve só o `code`. Quando o método precisa da
resposta, ele desempacota:

```python
# unitree_sdk2py/go2/vui/vui_client.py:36
def GetSwitch(self):
    code, data = self._Call(VUI_API_ID_GETSWITCH, parameter)
    if code == 0:                      # só desempacota se deu certo
        d = json.loads(data)           # texto → dicionário
        return code, d["enable"]       # devolve o valor de dentro
    else:
        return code, None              # deu erro: devolve None no lugar
```

Esse `if code == 0 ... else return code, None` é o motivo de você ver
`code, valor = client.AlgumaCoisa()` espalhado pelos exemplos. **Sempre confira
o `code` antes de usar o valor**, senão você vai usar um `None`.

### `_CallNoReply` — envia e **não espera**

```python
code = self._CallNoReply(API_ID, parameter)
```

Devolve **um** valor só. Dispara e esquece. É usado exatamente nos comandos de
movimento contínuo, onde esperar resposta atrasaria tudo:

| Método | Arquivo |
|---|---|
| `SportClient.Move` | `sport/sport_client.py:138` |
| `ObstaclesAvoidClient.Move` | `obstacles_avoid/obstacles_avoid_client.py:52` |
| `ObstaclesAvoidClient.MoveToAbsolutePosition` | `obstacles_avoid/obstacles_avoid_client.py:69` |
| `ObstaclesAvoidClient.MoveToIncrementPosition` | `obstacles_avoid/obstacles_avoid_client.py:79` |

!!! warning "`code == 0` aqui significa menos do que você pensa"
    Num `_CallNoReply`, o `0` quer dizer apenas **"consegui colocar a mensagem
    na rede"**. Não quer dizer que o robô recebeu, entendeu ou obedeceu. Se o
    robô estiver deitado, o `Move` devolve 0 e nada acontece.

### `_CallBinary` — envia e recebe **bytes crus**

Usado por um método só em todo o `go2/`: o da câmera.

```python
# unitree_sdk2py/go2/video/video_client.py:21
def GetImageSample(self):
    return self._CallBinary(VIDEO_API_ID_GETIMAGESAMPLE, [])
```

Existe porque uma foto não cabe em texto. Detalhes na
[página do `video`](03-video.md).

---

## A tabela de códigos de erro

**Esta tabela não existe no repositório.** Montei juntando três arquivos de
constantes espalhados. É a peça de documentação mais útil deste capítulo inteiro.

### Erros gerais — valem para todos os módulos

De `unitree_sdk2py/rpc/internal.py`:

| Código | Nome no código | O que significa, em português |
|---|---|---|
| **0** | `RPC_OK` | Deu certo. |
| 3001 | `RPC_ERR_UNKNOWN` | Erro não identificado. |
| 3102 | `RPC_ERR_CLIENT_SEND` | Não conseguiu nem enviar a mensagem. Rede caiu. |
| **3103** | `RPC_ERR_CLIENT_API_NOT_REG` | **Você esqueceu o `Init()`.** É o erro mais comum. |
| **3104** | `RPC_ERR_CLIENT_API_TIMEOUT` | O robô não respondeu no tempo do `SetTimeout`. |
| 3105 | `RPC_ERR_CLIENT_API_NOT_MATCH` | A resposta que chegou não é da pergunta que você fez. |
| 3106 | `RPC_ERR_CLIENT_API_DATA` | A resposta veio corrompida. |
| 3107 | `RPC_ERR_CLIENT_LEASE_INVALID` | Sua "trava de exclusividade" expirou. |
| 3201 | `RPC_ERR_SERVER_SEND` | O robô não conseguiu te responder. |
| 3202 | `RPC_ERR_SERVER_INTERNAL` | Deu erro dentro do robô. |
| 3203 | `RPC_ERR_SERVER_API_NOT_IMPL` | Esse comando não existe nessa versão do robô. |
| 3204 | `RPC_ERR_SERVER_API_PARAMETER` | Você mandou um parâmetro inválido. |
| 3205 | `RPC_ERR_SERVER_LEASE_DENIED` | Outro programa já tem o controle. |
| 3206 | `RPC_ERR_SERVER_LEASE_NOT_EXIST` | Você pediu uma trava que não existe. |
| 3207 | `RPC_ERR_SERVER_LEASE_EXIST` | Já existe uma trava ativa. |

### Erros específicos de módulo

| Código | Módulo | Nome | Significado |
|---|---|---|---|
| 4101 | `sport` | `SPORT_ERR_CLIENT_POINT_PATH` | Trajetória inválida. *(nunca é disparado no Go2 — veja [`PathPoint`](02-sport.md#pathpoint-codigo-morto))* |
| 4201 | `sport` | `SPORT_ERR_SERVER_OVERTIME` | O serviço de movimento demorou demais. |
| 4202 | `sport` | `SPORT_ERR_SERVER_NOT_INIT` | O serviço de movimento não está ligado no robô. |
| 5201 | `robot_state` | `ROBOT_STATE_ERR_SERVICE_SWITCH` | Não conseguiu ligar/desligar o serviço. |
| 5202 | `robot_state` | `ROBOT_STATE_ERR_SERVICE_PROTECTED` | Esse serviço é protegido e não pode ser desligado. |

### Como ler um código na prática

```python
code = client.StandUp()

if code == 0:
    print("Levantou.")
elif code == 3103:
    print("Você esqueceu de chamar client.Init()")
elif code == 3104:
    print("Sem resposta. Confira o nome da placa de rede e o cabo.")
elif code == 4202:
    print("O serviço 'sport' está desligado dentro do robô.")
    print("Ligue com o RobotStateClient ou pelo app.")
else:
    print("Erro:", code)
```

!!! tip "Um ajudante que vale copiar"
    O SDK não tem uma função que traduz código em texto. Faça a sua:

    ```python
    ERROS = {
        0:    "OK",
        3102: "falha ao enviar (rede)",
        3103: "faltou chamar Init()",
        3104: "tempo esgotado — sem resposta do robô",
        3203: "comando não existe nesta versão do robô",
        3204: "parâmetro inválido",
        3205: "outro programa está com o controle",
        4201: "serviço de movimento demorou demais",
        4202: "serviço de movimento não está ligado",
        5202: "serviço protegido — não pode ser desligado",
    }

    def explicar(code):
        return ERROS.get(code, f"erro desconhecido ({code})")

    # uso:
    code = client.StandUp()
    if code != 0:
        print("StandUp falhou:", explicar(code))
    ```

---

## O *lease*: a trava de exclusividade

O `SportClient` é o único que aceita `enableLease=True`:

```python
client = SportClient(enableLease=True)
```

**O que é:** uma reserva de uso. Enquanto você tem a trava, nenhum outro
programa consegue mandar comandos de movimento — nem o controle remoto, nem o
aplicativo do celular. Serve para evitar que dois comandos conflitantes cheguem
ao mesmo tempo e o robô faça algo imprevisível.

**Como funciona por dentro:** ao criar o cliente com `enableLease=True`, o SDK
sobe uma thread que pede a trava ao robô e depois fica **renovando** de tempos
em tempos. O prazo padrão é de 1 segundo:

```python
# unitree_sdk2py/rpc/internal.py:12
RPC_LEASE_TERM = 1.0
```

Se o seu programa morrer, a renovação para, a trava expira em cerca de 1 segundo
e o robô volta a aceitar comandos de outras fontes. É um mecanismo de segurança:
a trava nunca fica presa.

**Como usar:**

```python
client = SportClient(enableLease=True)
client.SetTimeout(3.0)
client.Init()

client.WaitLeaseApplied()    # ◄── bloqueia até a trava ser concedida

print("Trava obtida, id =", client.GetLeaseId())
client.StandUp()             # agora só você comanda
```

!!! warning "Na dúvida, não use"
    Todos os exemplos oficiais do Go2 usam `SportClient()` sem trava. Com a
    trava ligada, **o controle remoto para de funcionar** enquanto seu programa
    roda — e se ele travar num laço infinito, você perde o botão de parada de
    emergência mais prático que tem. Use apenas quando um segundo programa
    concorrente for um risco real, e sempre com um `try/finally` que encerra.

---

## O esqueleto que vale decorar

Este é o modelo seguro para qualquer programa com qualquer um dos cinco módulos:

```python
import sys
import time

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.sport.sport_client import SportClient


def main():
    # --- 1. Rede -----------------------------------------------------
    interface = sys.argv[1] if len(sys.argv) > 1 else None
    ChannelFactoryInitialize(0, interface)

    # --- 2. Cliente --------------------------------------------------
    client = SportClient()
    client.SetTimeout(3.0)
    client.Init()                 # nunca esqueça

    # --- 3. Teste de vida --------------------------------------------
    # Pergunta a versão do serviço. É a forma mais barata de confirmar
    # que existe alguém do outro lado antes de mandar o robô se mexer.
    code, versao = client.GetServerApiVersion()
    if code != 0:
        print("Robô não respondeu. code =", code)
        return
    print("Conectado. Versão do serviço no robô:", versao)

    # --- 4. Trabalho de verdade --------------------------------------
    try:
        client.StandUp()
        time.sleep(3)
        client.StandDown()
        time.sleep(3)
    finally:
        # --- 5. Encerramento seguro ----------------------------------
        # Roda mesmo se der Ctrl+C ou exceção no meio.
        # Damp desliga a força dos motores: o robô relaxa e senta.
        client.StopMove()
        client.Damp()
        print("Encerrado com segurança.")


if __name__ == "__main__":
    main()
```

O `GetServerApiVersion()` vem de graça da classe-mãe `Client` e funciona em
todos os cinco módulos. É um bom teste de conectividade porque não move nada.

!!! danger "O `finally` não é enfeite"
    Um `Ctrl+C` no meio de um `Move` deixa o robô andando, porque `Move` é
    disparado e esquecido — ninguém cancela sozinho. Sempre termine com
    `StopMove()` e, se for o caso, `Damp()`.

---

## Próximos passos

Agora que o mecanismo está claro, cada página seguinte só precisa te contar o
que é específico daquele módulo:

- [`sport` — movimento](02-sport.md)
- [`video` — câmera frontal](03-video.md)
- [`obstacles_avoid` — desvio de obstáculos](04-obstacles-avoid.md)
- [`vui` — luz e som](05-vui.md)
- [`robot_state` — serviços do robô](06-robot-state.md)
