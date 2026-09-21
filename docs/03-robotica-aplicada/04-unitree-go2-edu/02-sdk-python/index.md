# O SDK Python do Go2 — `unitree_sdk2py/go2`

*A documentação que a Unitree não escreveu.*

O repositório [`unitree_sdk2_python`](https://github.com/unitreerobotics/unitree_sdk2_python)
tem duas partes, e a confusão entre elas é a primeira barreira de quem começa:

```
unitree_sdk2_python/
├── example/              ← programas prontos para rodar. São cascas finas.
│   └── go2/
│       ├── front_camera/
│       ├── high_level/
│       └── low_level/
└── unitree_sdk2py/       ← a biblioteca de verdade. É aqui que mora tudo.
    └── go2/              ← ◄── o assunto deste capítulo
        ├── sport/
        ├── video/
        ├── obstacles_avoid/
        ├── vui/
        └── robot_state/
```

Um arquivo de `example/` normalmente faz quatro coisas: liga na rede, cria um
objeto, chama `Init()` e chama métodos. Toda a substância — montar a mensagem,
mandar pro robô, desempacotar a resposta — está em `unitree_sdk2py/go2/`.

**O problema:** esse diretório tem **777 linhas de código e zero documentação**.
Não há um único arquivo de texto dentro de `unitree_sdk2py/`. Os comentários que
parecem documentação são só faixas decorativas acima das classes:

```python
"""
" class SportClient      ← isso não explica nada. É só um separador visual.
"""
class SportClient(Client):
```

Nenhum método diz o que recebe, em que unidade, nem o que devolve. `Move(vx, vy,
vyaw)` — metros por segundo? Centímetros? Qual o limite? Não está escrito em
lugar nenhum do repositório.

Este capítulo é a leitura desse código, módulo por módulo, escrita para quem
quer usar sem adivinhar.

---

## Como ler este capítulo

Comece pela **Anatomia**. Os cinco módulos são o *mesmo* código com nomes
diferentes — entender um cliente é entender os cinco. Depois vá direto para o
módulo que te interessa.

<div class="grid cards" markdown>

- **[Anatomia de um client](01-anatomia-de-um-client.md)**

    ---

    **Leia primeiro.** O padrão que todos os cinco módulos repetem: conectar na
    rede, registrar comandos, mandar um pedido, ler o número de retorno. Explica
    o que é `ChannelFactoryInitialize`, por que existe `Init()`, e a tabela de
    códigos de erro que não existe no repositório.

- **[`sport` — movimento](02-sport.md)**

    ---

    O módulo grande: 38 comandos de locomoção. Levantar, deitar, andar, girar,
    mudar de marcha, dar cambalhota. É o que você usa em 90% dos casos. Inclui a
    tabela completa dos números de cada comando.

- **[`video` — câmera frontal](03-video.md)**

    ---

    Um único comando: pedir uma foto. Devolve os bytes de um JPEG. Explica como
    virar imagem do OpenCV, como gravar em disco e por que isso **não** é um
    stream de vídeo.

- **[`obstacles_avoid` — desvio de obstáculos](04-obstacles-avoid.md)**

    ---

    Andar deixando o robô decidir como não bater. Tem um `Move` **diferente** do
    módulo `sport`, e três modos de deslocamento (velocidade, posição relativa,
    posição absoluta) escondidos em um campo chamado `mode`.

- **[`vui` — luz e som](05-vui.md)**

    ---

    O menor e mais fácil de todos: brilho do led e volume do alto-falante. É o
    módulo ideal para testar se sua conexão com o robô está funcionando, porque
    não move nada.

- **[`robot_state` — serviços do robô](06-robot-state.md)**

    ---

    Listar, ligar e desligar os serviços que rodam dentro do robô. É o módulo
    que você **precisa** entender antes de qualquer controle de baixo nível,
    porque é ele que desliga o `sport_mode`.

</div>

---

## Os cinco módulos em uma tabela

Cada pasta em `unitree_sdk2py/go2/` tem sempre dois arquivos: um `*_api.py`
(a lista de números dos comandos) e um `*_client.py` (a classe que você usa).

| Pasta | Classe | Nome interno do serviço | Comandos | Tamanho |
|---|---|---|---|---|
| [`sport`](02-sport.md) | `SportClient` | `"sport"` | 38 | 363 linhas |
| [`video`](03-video.md) | `VideoClient` | `"videohub"` | 1 | 23 linhas |
| [`obstacles_avoid`](04-obstacles-avoid.md) | `ObstaclesAvoidClient` | `"obstacles_avoid"` | 4 | 79 linhas |
| [`vui`](05-vui.md) | `VuiClient` | `"vui"` | 6 | 85 linhas |
| [`robot_state`](06-robot-state.md) | `RobotStateClient` | `"robot_state"` | 3 | 84 linhas |

!!! note "Por que o nome interno importa"
    O "nome interno do serviço" é o endereço do programa que roda **dentro** do
    robô e vai atender seu pedido. Repare que o da pasta `video` é `"videohub"`,
    e não `"video"` — os nomes não batem, e isso é normal. Você nunca digita
    esse nome, mas ele aparece em mensagens de erro e na lista que o
    [`robot_state`](06-robot-state.md) devolve.

---

## O "hello world": desligando o led

Se você só quer confirmar que consegue falar com o robô, este é o programa mais
seguro possível. Ele não move nada — só apaga e acende a luz da frente.

```python
import sys
import time

# Esta função prepara a comunicação com o robô. Precisa ser chamada
# UMA VEZ, antes de criar qualquer cliente.
from unitree_sdk2py.core.channel import ChannelFactoryInitialize

# O cliente de luz e som. Escolhi ele porque é inofensivo.
from unitree_sdk2py.go2.vui.vui_client import VuiClient

# O nome da sua placa de rede (ex.: "enp2s0"). Descubra com: ip addr
INTERFACE = sys.argv[1] if len(sys.argv) > 1 else None

# Abre a comunicação. O 0 é o "domínio" — deixe 0 sempre.
ChannelFactoryInitialize(0, INTERFACE)

client = VuiClient()      # cria o objeto
client.SetTimeout(3.0)    # desiste depois de 3 segundos sem resposta
client.Init()             # OBRIGATÓRIO: sem isso, todo comando falha

# Pergunta ao robô qual o brilho atual.
# Todo método devolve um "code": 0 = deu certo, qualquer outro = erro.
code, brilho = client.GetBrightness()
print("code:", code, "| brilho atual:", brilho)

if code != 0:
    print("Não consegui falar com o robô. Veja a tabela de erros.")
    sys.exit(1)

client.SetBrightness(0)   # apaga
time.sleep(2)
client.SetBrightness(10)  # acende no máximo
print("Funcionou.")
```

Rodando:

```bash
python3 hello_go2.py enp2s0
```

Se imprimir `code: 0`, sua conexão está boa e todo o resto deste capítulo vai
funcionar. Se imprimir `code: 3104`, é tempo esgotado — quase sempre nome de
placa de rede errado. A [tabela completa de erros](01-anatomia-de-um-client.md#a-tabela-de-codigos-de-erro)
está na página de anatomia.

---

## O que este capítulo descobriu lendo o código

Coisas que não estão escritas em lugar nenhum e que você só descobre abrindo os
arquivos:

- O `Move` do módulo `sport` e o `Move` do módulo `obstacles_avoid` **montam
  mensagens diferentes** e não são intercambiáveis.
  ([detalhes](04-obstacles-avoid.md#os-dois-move-do-sdk))
- Existe um comando `EconomicGait` (marcha econômica, número 1063) **registrado
  mas sem método** no `SportClient` do Go2 — está inacessível.
  ([detalhes](02-sport.md#comandos-que-existem-mas-voce-nao-consegue-chamar))
- A classe `PathPoint` e a constante `SPORT_PATH_POINT_SIZE` existem no arquivo
  do Go2, mas **nenhum método as usa** — são sobra de outro robô (o B2).
  ([detalhes](02-sport.md#pathpoint-codigo-morto))
- O método `SetReportFreq` do `robot_state` tem um **defeito real**: manda a
  variável errada para dentro. ([detalhes](06-robot-state.md#o-defeito-do-setreportfreq))
- O `vui_client.py` tem a faixa `" class VideoClient"` acima de `class
  VuiClient`, e o comentário `# 1006` acima de um comando que é 1004.
  ([detalhes](05-vui.md#os-erros-de-copiar-e-colar))
- Três dos quatro caminhos de exemplo citados no `README.md` oficial **não
  existem mais** no repositório.
