# Exercícios de verificação — Launch Files

Dez exercícios progressivos, todos no **turtlesim** e compatíveis com o **Foxy**.
Cada um tem: objetivo, conceitos cobrados, especificação e critério de aprovação.
Regra do jogo: só abra as dicas se travar por mais de 15 minutos.

!!! warning "Duas armadilhas conhecidas antes de começar"
    **1. Teleop dentro de launch não recebe teclado.** Processos lançados pelo
    `ros2 launch` não ganham um terminal (TTY). Para o `turtle_teleop_key`
    funcionar, dê a ele um terminal próprio:
    ```python
    Node(package='turtlesim', executable='turtle_teleop_key',
         prefix='xterm -e', output='screen')
    ```
    (instale antes: `apt install xterm`)

    **2. `ForLoop`/`ForEach` NÃO existem no Foxy.** Para repetir N vezes,
    use um `for` de Python gerando a lista de actions, ou `OpaqueFunction`
    quando o N vier de um argumento (Exercício 6).

---

## Exercício 1 — Decolagem 🟢

**Objetivo:** substituir os dois terminais por um único comando.

**Conceitos:** `Node`, `output`, `prefix`, estrutura mínima de um launch.

**Especificação:** um único `ex01.launch.py` que sobe o `turtlesim_node`
e o `turtle_teleop_key` (em xterm). Nada de argumentos ainda.

**✅ Aprovado se:** `ros2 launch seu_pacote ex01.launch.py` abre a janela do
simulador **e** um xterm; as teclas no xterm movem a tartaruga.

??? tip "Dica"
    O `output='screen'` no turtlesim deixa você ver os logs de
    "Rotation goal..." no terminal do launch — útil para os próximos exercícios.

---

## Exercício 2 — Painel de controle 🟢

**Objetivo:** parametrizar o Exercício 1 sem editar código.

**Conceitos:** `DeclareLaunchArgument`, `LaunchConfiguration`, `parameters`,
`--show-args`.

**Especificação:** adicione os argumentos `cor_r`, `cor_g`, `cor_b`
(defaults à sua escolha) aplicados como *parameters* do turtlesim, e um
argumento `nome_sim` que vira o `name=` do nó.

**✅ Aprovado se:** `--show-args` lista os 4 argumentos com defaults; rodar com
`cor_r:=255 cor_g:=0 cor_b:=0` abre a janela vermelha; `ros2 node list`
mostra o nome que você passou.

---

## Exercício 3 — Piloto automático 🟢

**Objetivo:** desenhar sem teclado, só com o launch.

**Conceitos:** `ExecuteProcess` (colagem de `cmd=[[...]]`), `TimerAction`,
serviço `/spawn`, tópico `cmd_vel`.

**Especificação:** o launch sobe o turtlesim, cria a `turtle2` via
`ros2 service call .../spawn`, e faz a `turtle1` desenhar um **quadrado**
usando comandos `ros2 topic pub --once ...` disparados por `TimerAction`
em instantes crescentes (t = 1s, 2s, 3s...). Sem teleop neste exercício.

**✅ Aprovado se:** você roda o launch, não toca em nada, e um quadrado
(ou algo honestamente parecido) aparece na tela.

??? tip "Dica"
    Alternar "anda reto" e "gira 90°":
    ```bash
    ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 2.0}}"
    ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist "{angular: {z: 1.5708}}"
    ```

---

## Exercício 4 — Ordem por eventos, não por relógio 🟡

**Objetivo:** refazer o Exercício 3 **sem nenhum `TimerAction`**.

**Conceitos:** `RegisterEventHandler`, `OnProcessExit`/`OnExecutionComplete`,
encadeamento.

**Especificação:** cada comando do desenho só dispara quando o anterior
**terminar** (evento), não quando o relógio achar que sim.

**✅ Aprovado se:** o desenho sai igual ao do Ex. 3 **e**, como prova de
robustez, se você trocar um dos passos por
`bash -c 'sleep 3; ros2 topic pub --once ...'` a sequência continua correta
(com timers, ela quebraria).

---

## Exercício 5 — Pai e filhos 🟡

**Objetivo:** dividir o sistema em arquivos reutilizáveis.

**Conceitos:** `IncludeLaunchDescription`, `launch_arguments` (`.items()`),
encaminhamento de argumento, `IfCondition`.

**Especificação:** crie `sim.launch.py` (turtlesim parametrizado por cor e
namespace) e `teleop.launch.py` (o xterm). Um `principal.launch.py` inclui os
dois, encaminhando um argumento `cor_r` do pai para o filho, e o teleop só é
incluído se `com_teleop:=true` (default `false`).

**✅ Aprovado se:** `principal.launch.py cor_r:=200` muda a cor **do filho**;
sem `com_teleop:=true` o xterm não abre; com ele, abre.

---

## Exercício 6 — O laço que o Foxy não tem 🟡

**Objetivo:** repetir uma coreografia N vezes, com N vindo da linha de comando.

**Conceitos:** `OpaqueFunction`, `.perform(context)`, `for` de Python gerando
actions, a diferença entre tempo de construção e tempo de execução.

**Especificação:** argumento `voltas` (default `3`). A `turtle2` (spawnada)
repete um movimento `voltas` vezes. Como o valor só existe na execução, use
`OpaqueFunction` para ler `LaunchConfiguration('voltas').perform(context)` e
gerar a lista de actions num `for`.

**✅ Aprovado se:** `voltas:=5` gera visivelmente mais repetições que
`voltas:=2`, sem editar o arquivo.

??? tip "Dica — esqueleto do OpaqueFunction"
    ```python
    def gerar_coreografia(context):
        n = int(LaunchConfiguration('voltas').perform(context))
        acoes = []
        for i in range(n):
            acoes.append(TimerAction(period=2.0*i, actions=[...]))
        return acoes

    # na LaunchDescription:
    OpaqueFunction(function=gerar_coreografia)
    ```

---

## Exercício 7 — O show antes do teclado 🟠

**Objetivo:** o exercício que você imaginou: coreografia primeiro, teclado depois.

**Conceitos:** tudo dos Ex. 4–6 combinado; eventos entre coreografia e teleop.

**Especificação:** as duas tartarugas fazem a coreografia (a `turtle2` começa
quando a `turtle1` inicia o dela — evento, não timer) e **só quando o último
movimento terminar** o xterm do teleop abre.

**✅ Aprovado se:** o xterm literalmente não existe na tela durante a animação
e aparece sozinho ao final dela.

---

## Exercício 8 — Dois mundos com carimbo 🟠

**Objetivo:** multi-robô com namespaces sem repetir código.

**Conceitos:** `GroupAction`, `PushRosNamespace`, escopo, `remappings`.

**Especificação:** o principal inclui o **mesmo** `sim.launch.py` duas vezes,
embrulhado em namespaces `robo1` e `robo2`. Adicione o nó `mimic` remapeado
para que a tartaruga do `robo2` imite a do `robo1`.

**✅ Aprovado se:** `ros2 node list` mostra `/robo1/sim` e `/robo2/sim`;
dirigindo o `robo1` pelo teleop (remapeado!), o `robo2` copia os movimentos.

---

## Exercício 9 — Cores por YAML com curinga 🟠

**Objetivo:** tirar a configuração de dentro do código.

**Conceitos:** `parameters=[arquivo]`, YAML com `/**:`, `data_files` do
`setup.py`, diferença src/ vs install/.

**Especificação:** um `config/cores.yaml` com o curinga `/**:` define as cores
dos **dois** mundos do Ex. 8. Um argumento `arquivo_config` permite apontar
outro YAML pela linha de comando.

**✅ Aprovado se:** editar o YAML + rebuild muda as duas janelas de uma vez;
passar outro YAML pela CLI muda sem rebuild do launch.

---

## Exercício 10 — Sistema completo com RViz e desligamento digno 🔴

**Objetivo:** o exame final: reconstruir de memória um "projeto grande".

**Conceitos:** todos os anteriores + `rviz2 -d`, broadcasters do
`turtle_tf2_py`, `EmitEvent(Shutdown)`, `OnShutdown`, `LocalSubstitution`.

**Especificação:** principal que inclui: os dois mundos (Ex. 8), as cores por
YAML (Ex. 9), os broadcasters/listener do `turtle_tf2_py`, o RViz com um
arquivo de configuração, a coreografia + teleop no final (Ex. 7), **e**:
fechar a janela do mundo 1 emite `Shutdown` derrubando tudo, com um
`OnShutdown` logando o motivo.

**✅ Aprovado se:** um único comando sobe o sistema inteiro; o RViz mostra os
frames; fechar a janela principal encerra tudo com sua mensagem de despedida
no log. Parabéns — você domina o capítulo. 🎓
