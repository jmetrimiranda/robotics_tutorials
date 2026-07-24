# CLI Tools

*Tudo que dá para fazer sem escrever uma linha de código.*

---

## 1. Configurando o ambiente

O lugar onde você desenvolve com ROS 2 se chama **workspace**. Na prática você
terá vários workspaces ativos ao mesmo tempo.

### Fazer o source

Todo terminal novo precisa carregar o ambiente:

```bash
source /opt/ros/foxy/setup.bash
```

Para não repetir isso a vida inteira:

```bash
echo "source /opt/ros/foxy/setup.bash" >> ~/.bashrc
```

A linha vai para o fim do `~/.bashrc`, que é executado a cada shell interativo.

### Conferir as variáveis

```bash
printenv | grep -i ROS
```

```
ROS_VERSION=2
ROS_PYTHON_VERSION=3
ROS_DISTRO=foxy
```

### `ROS_DOMAIN_ID`

Só nós com o **mesmo** domain ID se descobrem e conversam. É o que isola o seu
grafo do grafo do colega na mesma rede.

```bash
export ROS_DOMAIN_ID=42
echo "export ROS_DOMAIN_ID=42" >> ~/.bashrc   # persistente
```

!!! tip
    Use valores entre 0 e 101 — são seguros em qualquer plataforma.

### `ROS_LOCALHOST_ONLY`

Limita toda a comunicação à própria máquina:

```bash
export ROS_LOCALHOST_ONLY=1
```

---

## 2. turtlesim, ros2 e rqt

O **turtlesim** é um simulador leve para aprender ROS 2. Ele mostra, no nível
mais básico, o que você vai fazer depois com um robô de verdade.

O **rqt** é a interface gráfica do ROS 2. Tudo que se faz nele também se faz
pela linha de comando.

```bash
sudo apt update
sudo apt install ros-foxy-turtlesim
```

Conferindo a instalação:

```bash
ros2 pkg executables turtlesim
```

```
turtlesim draw_square
turtlesim mimic
turtlesim turtle_teleop_key
turtlesim turtlesim_node
```

Subindo o simulador e o teleop, em dois terminais:

```bash
ros2 run turtlesim turtlesim_node
```

```bash
ros2 run turtlesim turtle_teleop_key
```

Com o sistema no ar, os quatro `list` mostram o grafo inteiro:

```bash
ros2 node list
ros2 topic list
ros2 service list
ros2 action list
```

### rqt

```bash
sudo apt update
sudo apt install ~nros-foxy-rqt*
rqt
```

!!! warning "O `~n` não é enfeite"
    `~nros-foxy-rqt*` é um padrão do apt que casa por **nome** de pacote. Sem o
    `~n`, o glob não expande e o apt reclama.

Na primeira execução o rqt abre em branco. Vá em
**Plugins → Services → Service Caller**, escolha `/spawn`, preencha e clique em
**Call** para criar uma segunda tartaruga.

---

## 3. Nós

O **ROS graph** é a rede de elementos ROS 2 processando dados ao mesmo tempo.

Cada nó deve ter **um** propósito, modular: controlar as rodas do motor, ou
publicar o dado de um sensor. Nós trocam dados entre si por tópicos, serviços,
actions e parâmetros. Um sistema robótico completo é a soma de vários nós
trabalhando juntos.

```bash
ros2 run <package_name> <executable_name>
ros2 node list
ros2 node info /turtlesim
```

O `node info` devolve os **Subscribers**, **Publishers**, **Service Servers**,
**Service Clients**, **Action Servers** e **Action Clients** daquele nó.

### Remapping

Permite reatribuir propriedades padrão do nó — nome do nó, nomes de tópicos e
serviços — para valores customizados:

```bash
ros2 run turtlesim turtlesim_node --ros-args --remap __node:=my_turtle
```

Tudo que vem depois de `--ros-args` é argumento do ROS, não do executável.

---

## 4. Tópicos

Tópico é o barramento por onde os nós trocam informação. Não é uma conexão
exclusiva: um tópico pode ter vários publishers e vários subscribers ao mesmo
tempo, e ninguém sabe quem está do outro lado.

```bash
rqt_graph
```

No grafo: **círculo** é nó, **retângulo** é tópico. Seta do círculo para o
retângulo = o nó publica. Seta do retângulo para o círculo = o nó está inscrito.

### Descobrindo o que existe

```bash
ros2 topic list
ros2 topic list -t     # com o tipo de mensagem
```

```
/parameter_events [rcl_interfaces/msg/ParameterEvent]
/rosout [rcl_interfaces/msg/Log]
/turtle1/cmd_vel [geometry_msgs/msg/Twist]
/turtle1/color_sensor [turtlesim/msg/Color]
/turtle1/pose [turtlesim/msg/Pose]
```

### Vendo os dados

```bash
ros2 topic echo /turtle1/cmd_vel
```

O `echo` cria um nó subscriber temporário — ele aparece no `rqt_graph` enquanto
está rodando.

### Entendendo a mensagem

Publisher e subscriber precisam usar o **mesmo tipo** para se comunicar.

```bash
ros2 interface show geometry_msgs/msg/Twist
```

```
Vector3 linear
Vector3 angular
```

!!! warning "Errata do cheat sheet"
    É `geometry_msgs`, com **s**. `geometry_msg` não existe e o comando falha.

### Publicando

```bash
ros2 topic pub <topic_name> <msg_type> '<args>'
```

Os argumentos vão em YAML:

```bash
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 1.8}}"
```

| Flag | Efeito |
|---|---|
| `--once` | publica uma mensagem e sai |
| `-r 1` | publica continuamente a 1 Hz |

### Medindo

```bash
ros2 topic hz /turtle1/pose
ros2 topic bw /turtle1/pose
ros2 topic info /turtle1/cmd_vel
```

```
average rate: 59.354
  min: 0.004s max: 0.027s std dev: 0.00284s window: 58
```

---

## 5. Serviços

Tópico entrega mensagem para quem estiver inscrito, sempre, independente de
alguém querer. Serviço é **request/response**: só devolve dado quando alguém
pede.

```bash
ros2 service list
ros2 service list -t                     # com os tipos
ros2 service type /clear                 # tipo de um serviço
ros2 service find std_srvs/srv/Empty     # todos os serviços de um tipo
```

### Estrutura do request/response

```bash
ros2 interface show turtlesim/srv/Spawn
```

```
float32 x
float32 y
float32 theta
string name   # Optional
---
string name
```

Acima do `---` é o **request**, abaixo é a **response**.

!!! warning "Errata do cheat sheet"
    O comando é `ros2 interface show <tipo>` — a extensão é `.srv`, nunca
    `.src`, e no Foxy você passa o tipo sem extensão nenhuma.

### Chamando

```bash
ros2 service call <service_name> <service_type> <arguments>
```

```bash
ros2 service call /spawn turtlesim/srv/Spawn \
  "{x: 6.0, y: 6.0, theta: 1.0, name: 'jorge'}"
```

```
requester: making request: turtlesim.srv.Spawn_Request(x=6.0, y=6.0, theta=1.0, name='jorge')

response:
turtlesim.srv.Spawn_Response(name='jorge')
```

!!! warning "Errata do cheat sheet"
    É `/spawn`, com barra. Sem a barra o nome não é resolvido e o comando fica
    pendurado em `waiting for service to become available...`.

---

## 6. Parâmetros

Parâmetro é valor de configuração de um nó — pense neles como as "preferências"
daquele nó. Podem ser `integer`, `float`, `boolean`, `string` e listas.

```bash
ros2 param list
ros2 param get /turtlesim background_g
ros2 param set /turtlesim background_r 150
ros2 param describe /minimal_param_node my_parameter
```

O `set` muda em tempo de execução e some quando o nó reinicia. Para persistir:

```bash
ros2 param dump /turtlesim            # gera ./turtlesim.yaml
ros2 param load /turtlesim ./turtlesim.yaml
```

Ou já subindo o nó com a configuração:

```bash
ros2 run turtlesim turtlesim_node --ros-args --params-file ./turtlesim.yaml
```

A diferença: o `load` aplica num nó que já está no ar; o `--params-file` faz os
valores valerem desde a inicialização.

---

## 7. Actions

Actions servem para tarefas **longas**. São feitas de três partes: **goal**,
**feedback** e **result** — e são construídas em cima de serviços (goal e
result) e tópico (feedback).

Um **action client** manda um goal para um **action server**, que confirma o
recebimento e devolve um fluxo de feedback até terminar com um result.

Com o teleop rodando, as teclas `G|B|V|C|D|E|R|T` giram a tartaruga para
orientações absolutas, e `F` cancela. Isso é uma action:

```
[INFO] [turtlesim]: Rotation goal completed successfully.
[INFO] [turtlesim]: Rotation goal canceled.
```

```bash
ros2 action list
ros2 action list -t
ros2 action info /turtle1/rotate_absolute
```

```
Action: /turtle1/rotate_absolute
Action clients: 1
    /teleop_turtle
Action servers: 1
    /turtlesim
```

### A interface

```bash
ros2 interface show turtlesim/action/RotateAbsolute
```

```
# The desired heading in radians
float32 theta
---
# The angular displacement in radians to the starting position
float32 delta
---
# The remaining rotation in radians
float32 remaining
```

Três blocos separados por **dois** `---`: goal, result, feedback — nessa ordem.

### Enviando um goal

```bash
ros2 action send_goal /turtle1/rotate_absolute \
  turtlesim/action/RotateAbsolute "{theta: 1.57}"
```

```
Goal accepted with ID: f8db8f44410849eaa93d3feb747dd444
Result:
  delta: -1.568000316619873
Goal finished with status: SUCCEEDED
```

Acrescente `--feedback` para ver o progresso enquanto a tarefa acontece.

---

## 8. Logs com rqt_console

```bash
ros2 run rqt_console rqt_console
```

A janela de cima acumula as mensagens; a do meio filtra por nível de
severidade. Dá para salvar e recarregar sessões — é uma ferramenta de depuração.

Para gerar mensagens de aviso, mande a tartaruga bater na parede:

```bash
ros2 topic pub -r 1 /turtle1/cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

Níveis, do mais grave ao menos: `Fatal`, `Error`, `Warn`, `Info`, `Debug`.

---

## 9. Lançando nós

Um launch file sobe e configura vários executáveis de uma vez:

```bash
ros2 launch turtlesim multisim.launch.py
```

```python
# turtlesim/launch/multisim.launch.py
from launch import LaunchDescription
import launch_ros.actions

def generate_launch_description():
    return LaunchDescription([
        launch_ros.actions.Node(
            namespace="turtlesim1", package='turtlesim',
            executable='turtlesim_node', output='screen'),
        launch_ros.actions.Node(
            namespace="turtlesim2", package='turtlesim',
            executable='turtlesim_node', output='screen'),
    ])
```

Dois simuladores, dois namespaces. Para movimentar cada um:

```bash
ros2 topic pub /turtlesim1/turtle1/cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 2.0}, angular: {z: 1.8}}"

ros2 topic pub /turtlesim2/turtle1/cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 2.0}, angular: {z: -1.8}}"
```

O assunto continua em [Criando um launch file](05-launch-criando.md).

---

## 10. Gravando e reproduzindo dados

`ros2 bag` grava o que passa pelos **tópicos** para você reproduzir depois.

```bash
mkdir bag_files && cd bag_files
ros2 bag record /turtle1/cmd_vel
```

`Ctrl+C` encerra. Sem `-o`, o diretório recebe o nome
`rosbag2_ano_mes_dia-hora_minuto_segundo` e contém um `.db3` (sqlite3) mais um
`metadata.yaml`.

Vários tópicos, com nome escolhido:

```bash
ros2 bag record -o subset /turtle1/cmd_vel /turtle1/pose
ros2 bag info subset
ros2 bag play subset
```

!!! tip "Por que o play demora mais que o movimento?"
    Olhe o campo `Count` do `bag info`: o `/turtle1/pose` publica a ~60 Hz e
    continua sendo reproduzido muito depois de a tartaruga parar. Compare com
    `ros2 topic hz /turtle1/pose`.

    Feche o teleop antes do `play`, senão os dois disputam o `cmd_vel`.

---

## Exercícios

!!! warning "Regra do jogo"
    Só abra a dica se travar por mais de 15 minutos.

### Exercício 1 — Reconhecimento 🟢

**Objetivo:** ler o grafo de um sistema que você não escreveu.

**Especificação:** suba `turtlesim_node` e `turtle_teleop_key`. Sem usar o
`rqt_graph`, descubra pela linha de comando: quantos nós existem, qual nó
publica em `/turtle1/cmd_vel`, qual se inscreve, e qual o tipo dessa mensagem.
Depois confira no `rqt_graph`.

**✅ Aprovado se:** você desenhou o grafo no papel antes de abrir o rqt e acertou.

??? tip "Dica"
    `ros2 topic info` dá a contagem de publishers e subscribers; `ros2 node info`
    dá o lado de cada nó.

### Exercício 2 — Tartaruga sem teclado 🟢

**Objetivo:** separar "controlar" de "teclar".

**Especificação:** feche o teleop. Faça a `turtle1` desenhar um quadrado usando
só `ros2 topic pub --once`, alternando andar reto e girar 90°.

**✅ Aprovado se:** apareceu um quadrado (ou algo honestamente parecido).

??? tip "Dica"
    ```bash
    ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 2.0}}"
    ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist "{angular: {z: 1.5708}}"
    ```

### Exercício 3 — Serviço na mão 🟢

**Objetivo:** descobrir como chamar um serviço que você nunca viu.

**Especificação:** partindo só de `ros2 service list`, crie uma tartaruga
chamada `jorge` em (7, 3) e depois **mate** ela. Você não pode consultar esta
página: use `list -t`, `type` e `interface show` para descobrir os argumentos.

**✅ Aprovado se:** a tartaruga apareceu e sumiu, e você descobriu o tipo do
`/kill` sozinho.

### Exercício 4 — Cores que sobrevivem 🟡

**Objetivo:** entender a diferença entre `param set`, `param load` e
`--params-file`.

**Especificação:** deixe o fundo do turtlesim roxo com `param set`. Salve com
`param dump`. Mate o nó e suba de novo — a cor voltou ao padrão. Agora faça a
cor valer **desde a inicialização**, sem tocar em nada depois que o nó subiu.

**✅ Aprovado se:** a janela abre já roxa e você sabe explicar por que o
`param set` sozinho não bastava.

### Exercício 5 — Action até o fim 🟡

**Objetivo:** ver goal, feedback e result como três coisas distintas.

**Especificação:** mande a tartaruga girar para `theta: -1.57` mostrando o
feedback. Anote o goal ID. Depois refaça o mesmo giro pelo teleop e cancele no
meio com `F`, observando o terminal do `/turtlesim`.

**✅ Aprovado se:** você consegue apontar, na saída do terminal, qual linha é
goal, qual é feedback e qual é result — e o que muda quando o goal é cancelado.

### Exercício 6 — Fantasma na garrafa 🟠

**Objetivo:** o `ros2 bag` como instrumento de depuração.

**Especificação:** grave `/turtle1/cmd_vel` **e** `/turtle1/pose` enquanto
dirige a tartaruga por uns 10 segundos. Feche tudo, suba um turtlesim limpo e
reproduza a gravação. Explique, usando `ros2 bag info` e `ros2 topic hz`, por
que o `play` continua rodando muito depois de a tartaruga parar de andar.

**✅ Aprovado se:** a tartaruga refaz o trajeto **e** sua explicação menciona a
diferença de `Count` entre os dois tópicos.

### Exercício 7 — Dois mundos 🟠

**Objetivo:** namespaces antes de aprender launch de verdade.

**Especificação:** com `ros2 launch turtlesim multisim.launch.py`, faça as duas
tartarugas girarem em sentidos opostos ao mesmo tempo. Depois responda: por que
`ros2 topic pub /turtle1/cmd_vel ...` não move nenhuma das duas?

**✅ Aprovado se:** as duas giram simultaneamente e você sabe dizer o nome
completo de cada tópico.
