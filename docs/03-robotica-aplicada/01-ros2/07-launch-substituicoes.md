# Substituições

*Argumentos que só existem na hora da execução.*

---

## Antes: o que é uma "action" de launch

Um launch file devolve uma `LaunchDescription`, e o primeiro argumento dela é
uma **lista de entidades** — cada uma é uma *action*. Entender launch é, em boa
medida, saber quais actions existem e o que cada uma faz.

Quando você roda `ros2 launch`, acontece isto:

1. a função `generate_launch_description()` é chamada e devolve o objeto;
2. cada action da lista é executada;
3. cada action faz o que sabe fazer.

### O catálogo

| Action | O que faz |
|---|---|
| `Node` | inicia um nó de um pacote ROS 2 |
| `DeclareLaunchArgument` | declara um argumento configurável pela linha de comando |
| `ExecuteProcess` | executa qualquer processo do sistema operacional |
| `IncludeLaunchDescription` | inclui outro launch file (Python, XML ou YAML) |
| `GroupAction` | agrupa actions com escopo próprio |
| `TimerAction` | executa uma lista de actions depois de um atraso |
| `RegisterEventHandler` | reage a eventos (`OnProcessStart`, `OnProcessExit`, `OnShutdown`) |
| `EmitEvent` | dispara um evento no sistema de launch |
| `LogInfo`, `LogWarning` | escreve no log do launch |
| `OpaqueFunction` | executa uma função Python com acesso ao `LaunchContext` |
| `Shutdown` | encerra todo o sistema lançado |
| `SetEnvironmentVariable` | define variável de ambiente |

Na prática, seis cobrem quase tudo: `Node`, `DeclareLaunchArgument`,
`IncludeLaunchDescription`, `ExecuteProcess`, `GroupAction` e `TimerAction`.

!!! warning "`ForLoop` / `ForEach` não existem no Foxy"
    Para repetir N vezes, use um `for` de Python gerando a lista de actions —
    ou `OpaqueFunction`, quando o N vier de um argumento.

---

## Declarar e ler argumentos

São duas coisas diferentes, e a confusão entre elas é a maior fonte de erro:

| | Para quê |
|---|---|
| `DeclareLaunchArgument('cor_r', default_value='200')` | **declara** que o argumento existe |
| `LaunchConfiguration('cor_r')` | **lê** o valor, na hora da execução |

`DeclareLaunchArgument` aceita:

- **`name`** (obrigatório) — o nome do argumento;
- **`default_value`** — o valor se o usuário não passar nada;
- **`description`** — texto de ajuda exibido no `--show-args`.

```bash
ros2 launch meu_pacote meu_launch.py --show-args
```

```
Arguments (pass arguments as '<name>:=<value>'):

    'turtlesim_ns':
        no description given
        (default: 'turtlesim1')

    'use_provided_red':
        no description given
        (default: 'False')

    'new_background_r':
        no description given
        (default: '200')
```

```bash
ros2 launch launch_tutorial example_substitutions.launch.py \
  turtlesim_ns:='turtlesim3' use_provided_red:='True' new_background_r:=200
```

É `:=`, não `=`.

---

## Pai e filho

O `IncludeLaunchDescription` existe para rodar vários launch files a partir de
um só. Ele espera duas coisas: o **caminho** do arquivo filho e os
**argumentos** a passar para ele.

```python
def generate_launch_description():
    colors = {'background_r': '200'}

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                PathJoinSubstitution([
                    FindPackageShare('launch_tutorial'),
                    'launch',
                    'example_substitutions.launch.py'
                ])
            ]),
            launch_arguments={
                'turtlesim_ns': 'turtlesim2',
                'use_provided_red': 'True',
                'new_background_r': TextSubstitution(text=str(colors['background_r']))
            }.items()
        )
    ])
```

### Formas de indicar o caminho

```python
# caminho literal
'/caminho/filho.launch.py'

# relativo ao arquivo atual
PathJoinSubstitution([ThisLaunchFileDir(), 'filho.launch.py'])

# resolvido pelo nome do pacote (o mais robusto)
PathJoinSubstitution([FindPackageShare('meu_pkg'), 'launch', 'filho.launch.py'])

# a forma com os.path, comum nos tutoriais
os.path.join(get_package_share_directory('meu_pkg'), 'launch', '/filho.launch.py')
```

### Formas de passar argumentos

```python
# A — o idioma clássico
launch_arguments={'cor': 'azul'}.items()

# B — lista de tuplas
launch_arguments=[('cor', 'verde'), ('velocidade', '9.9')]

# C — o valor pode ser uma substituição (encaminhando um argumento do pai)
launch_arguments={'cor': LaunchConfiguration('cor_global')}.items()
```

!!! warning "O `.items()` não é opcional"
    `launch_arguments` espera pares, não um dicionário. Esquecer o `.items()`
    dá um erro que não parece ter nada a ver com o problema.

E dá para incluir condicionalmente:

```python
IncludeLaunchDescription(
    caminho_filho,
    launch_arguments={'cor': 'dourado'}.items(),
    condition=IfCondition(LaunchConfiguration('incluir_extra')),
)
```

---

## O launch filho

```python
def generate_launch_description():
    turtlesim_ns = LaunchConfiguration('turtlesim_ns')
    use_provided_red = LaunchConfiguration('use_provided_red')
    new_background_r = LaunchConfiguration('new_background_r')

    turtlesim_ns_launch_arg = DeclareLaunchArgument(
        'turtlesim_ns',
        default_value='turtlesim1'
    )
    use_provided_red_launch_arg = DeclareLaunchArgument(
        'use_provided_red',
        default_value='False'
    )
    new_background_r_launch_arg = DeclareLaunchArgument(
        'new_background_r',
        default_value='200'
    )

    turtlesim_node = Node(
        package='turtlesim',
        namespace=turtlesim_ns,
        executable='turtlesim_node',
        name='sim'
    )

    spawn_turtle = ExecuteProcess(
        cmd=[[
            'ros2 service call ',
            turtlesim_ns,
            '/spawn ',
            'turtlesim/srv/Spawn ',
            '"{x: 2, y: 2, theta: 0.2}"'
        ]],
        shell=True
    )

    change_background_r = ExecuteProcess(
        cmd=[[
            'ros2 param set ',
            turtlesim_ns,
            '/sim background_r ',
            '120'
        ]],
        shell=True
    )

    return LaunchDescription([
        turtlesim_ns_launch_arg,
        use_provided_red_launch_arg,
        new_background_r_launch_arg,
        turtlesim_node,
        spawn_turtle,
        change_background_r,
    ])
```

Repare na lista `cmd=[[...]]`: os pedaços de string são **concatenados**, e no
meio deles entra o `LaunchConfiguration`. É assim que um valor que só existe na
execução vira parte de um comando de shell.

### `ExecuteProcess`

| Argumento | Para quê |
|---|---|
| `cmd` | lista com o executável e seus argumentos |
| `shell` | se `True`, o comando passa pelo shell do sistema |
| `output` | para onde vão stdout e stderr (`'screen'` para ver) |

```python
ExecuteProcess(
    cmd=['ros2', 'service', 'call', '/spawn',
         'turtlesim/srv/Spawn', '"{x: 2, y: 2, theta: 0.2}"'],
    shell=True,
    output='screen'
)
```

---

## Construindo e rodando

```bash
ros2 pkg create launch_tutorial --build-type ament_python
mkdir launch_tutorial/launch
# ... setup.py com data_files (ver capítulo anterior)
colcon build
ros2 launch launch_tutorial example_main.launch.py
```

Os exercícios estão em [Exercícios de launch](10-launch-exercicios.md) —
especialmente o 5 (pai e filhos) e o 6 (`OpaqueFunction`).
