# Criando um launch file

*Um comando no lugar de cinco terminais.*

---

## O que o sistema de launch faz

Ele descreve a configuração do seu sistema e a executa: quais programas rodar,
onde, com quais argumentos. Também monitora o que subiu — e é isso que permite
disparar ações em resposta a eventos, com os
[event handlers](08-launch-event-handlers.md).

## O arquivo mínimo

```python
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='turtlesim',
            namespace='turtlesim1',
            executable='turtlesim_node',
            name='sim'
        ),
        Node(
            package='turtlesim',
            namespace='turtlesim2',
            executable='turtlesim_node',
            name='sim'
        ),
        Node(
            package='turtlesim',
            executable='mimic',
            name='mimic',
            remappings=[
                ('/input/pose', '/turtlesim1/turtle1/pose'),
                ('/output/cmd_vel', '/turtlesim2/turtle1/cmd_vel'),
            ]
        )
    ])
```

Três coisas a notar:

1. `LaunchDescription` vem de `launch`; `Node` vem de `launch_ros.actions`.
   Confundir os dois é o erro de import mais comum.
2. A função **precisa** se chamar `generate_launch_description` — é o nome que o
   `ros2 launch` procura.
3. Os dois primeiros nós são idênticos: só o `namespace` muda. É isso que
   permite subir dois simuladores sem conflito.

## Rodando

```bash
ros2 launch turtlesim_mimic_launch.py           # arquivo solto
ros2 launch <pacote> <arquivo>                  # instalado num pacote
```

```
[INFO] [launch]: Default logging verbosity is set to INFO
[INFO] [turtlesim_node-1]: process started with pid [11714]
[INFO] [turtlesim_node-2]: process started with pid [11715]
[INFO] [mimic-3]: process started with pid [11716]
```

Para ver o sistema em ação:

```bash
ros2 topic pub -r 1 /turtlesim1/turtle1/cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: -1.8}}"
```

As duas tartarugas se movem juntas.

## Depurando com rqt_graph

```bash
rqt_graph
```

Lembre: retângulo é tópico, círculo é nó. Seta do nó para o tópico = publica;
do tópico para o nó = está inscrito.

O que acontece no exemplo acima:

1. alguém publica um `Twist` em `/turtlesim1/turtle1/cmd_vel`;
2. o `turtlesim_node` do namespace `turtlesim1` está inscrito nesse tópico —
   ao receber, dispara o callback que movimenta a tartaruga;
3. esse mesmo nó publica a posição resultante em `/turtlesim1/turtle1/pose`;
4. o nó `mimic` está inscrito nesse `pose` (remapeado como `/input/pose`),
   aproveita a parte de velocidade e publica em `/output/cmd_vel`, que foi
   remapeado para `/turtlesim2/turtle1/cmd_vel`.

O `mimic` não sabe nada sobre turtlesim: ele fala com `/input/pose` e
`/output/cmd_vel`. Quem decide o que isso significa é o remapping no launch.
Essa é a ideia inteira.

!!! warning "Teleop dentro de launch não recebe teclado"
    Processos lançados pelo `ros2 launch` não ganham um terminal (TTY). Para o
    `turtle_teleop_key` funcionar, dê a ele um terminal próprio:

    ```python
    Node(package='turtlesim', executable='turtle_teleop_key',
         prefix='xterm -e', output='screen')
    ```

    Instale antes: `sudo apt install xterm`.

---

Continua em [Launch em pacotes](06-launch-em-pacotes.md), e os exercícios de
launch estão todos em [Exercícios de launch](10-launch-exercicios.md).
