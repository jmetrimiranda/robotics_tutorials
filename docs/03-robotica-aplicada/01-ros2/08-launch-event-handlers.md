# Event handlers

*"Dado que X aconteceu, faça Y."*

---

O launch file não só lança nós: ele **observa** o que lançou e reage. Essa é a
função do `RegisterEventHandler`.

A ideia é simples de enunciar e muda a qualidade do seu sistema: em vez de
adivinhar com um `TimerAction` que "3 segundos devem bastar", você espera o
evento que realmente importa.

## Os cinco vigias

| Vigia → reação | Dispara quando… | Uso típico |
|---|---|---|
| `OnProcessStart`<br>→ `on_start` | o processo alvo **começa** a rodar | "assim que o simulador abrir, crie o robô" |
| `OnProcessIO`<br>→ `on_stdout`, `on_stderr`, `on_stdin` | o alvo **imprime** algo em um dos 3 canais | reagir ao texto que o processo escreveu (só aceita *lambda*) |
| `OnExecutionComplete`<br>→ `on_completion` | a action alvo **conclui** a execução | encadear o próximo passo após um comando |
| `OnProcessExit`<br>→ `on_exit` | o processo alvo **morre/fecha** | partida em sequência; derrubar tudo se o nó crítico cair |
| `OnShutdown`<br>→ `on_shutdown` | o launch inteiro está **desligando** (sem `target_action`) | limpeza e log final com o motivo do desligamento |

## Na prática

```python
from launch import LaunchDescription
from launch.actions import (ExecuteProcess, RegisterEventHandler,
                            LogInfo, EmitEvent)
from launch.event_handlers import OnProcessStart, OnProcessExit, OnShutdown
from launch.events import Shutdown
from launch.substitutions import LocalSubstitution
from launch_ros.actions import Node


def generate_launch_description():
    turtlesim_node = Node(
        package='turtlesim',
        executable='turtlesim_node',
        name='sim'
    )

    spawn_turtle = ExecuteProcess(
        cmd=['ros2 service call /spawn turtlesim/srv/Spawn "{x: 2, y: 2}"'],
        shell=True
    )

    return LaunchDescription([
        turtlesim_node,

        # assim que o simulador subir, crie a segunda tartaruga
        RegisterEventHandler(
            OnProcessStart(
                target_action=turtlesim_node,
                on_start=[
                    LogInfo(msg='Simulador no ar, criando turtle2'),
                    spawn_turtle
                ]
            )
        ),

        # quando o simulador fechar, derrube o sistema inteiro
        RegisterEventHandler(
            OnProcessExit(
                target_action=turtlesim_node,
                on_exit=[
                    LogInfo(msg='Janela fechada. Encerrando tudo.'),
                    EmitEvent(event=Shutdown(reason='janela fechada'))
                ]
            )
        ),

        # despedida, com o motivo
        RegisterEventHandler(
            OnShutdown(
                on_shutdown=[LogInfo(
                    msg=['Desligando porque: ',
                         LocalSubstitution('event.reason')])]
            )
        ),
    ])
```

Três detalhes que economizam tempo:

- `target_action` recebe **o objeto** da action, não uma string com o nome. Por
  isso o `turtlesim_node` foi guardado numa variável antes de entrar na lista.
- `OnShutdown` é o único sem `target_action` — ele vigia o launch inteiro.
- `LocalSubstitution('event.reason')` é como você lê o motivo do desligamento
  dentro do handler.

!!! tip "Evento vence relógio"
    Um encadeamento por `TimerAction` quebra silenciosamente quando a máquina
    está mais lenta, ou quando um passo demora mais que o previsto. O mesmo
    encadeamento por `OnProcessExit` continua correto. O Exercício 4 de
    [Exercícios de launch](10-launch-exercicios.md) é exatamente esse teste.
