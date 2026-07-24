# Projetos grandes

*Como organizar launch files quando o sistema para de caber em um arquivo.*

---

## A hierarquia

A solução se divide em dois níveis:

- o **top-level**, que não lança quase nada sozinho: ele inclui os outros launch
  files e passa os argumentos;
- os **filhos**, cada um responsável por uma parte do sistema.

```python
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    launch_1 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('launch_tutorial'), 'launch'),
            '/turtlesim_world_1.launch.py'])
    )
    launch_2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('launch_tutorial'), 'launch'),
            '/turtlesim_rviz.launch.py'])
    )

    return LaunchDescription([
        launch_1,
        launch_2,
    ])
```

---

## Parâmetros

### Direto no launch file

```python
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, TextSubstitution
from launch_ros.actions import Node


def generate_launch_description():
    background_r_launch_arg = DeclareLaunchArgument(
        'background_r', default_value=TextSubstitution(text='0'))
    background_g_launch_arg = DeclareLaunchArgument(
        'background_g', default_value=TextSubstitution(text='84'))
    background_b_launch_arg = DeclareLaunchArgument(
        'background_b', default_value=TextSubstitution(text='122'))

    return LaunchDescription([
        background_r_launch_arg,
        background_g_launch_arg,
        background_b_launch_arg,
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='sim',
            parameters=[{
                'background_r': LaunchConfiguration('background_r'),
                'background_g': LaunchConfiguration('background_g'),
                'background_b': LaunchConfiguration('background_b'),
            }]
        ),
    ])
```

### Num arquivo YAML

Melhor quando a configuração cresce. O arquivo vai em `config/` dentro do
pacote:

```yaml
# config/turtlesim.yaml
/turtlesim2/sim:
   ros__parameters:
      background_b: 255
      background_g: 86
      background_r: 150
```

A chave é `/namespace/nome_do_no`. É por isso que renomear o nó quebra o YAML.

```python
Node(
    package='turtlesim',
    executable='turtlesim_node',
    name='sim',
    parameters=[os.path.join(
        get_package_share_directory('launch_tutorial'),
        'config', 'turtlesim.yaml')]
)
```

### Curinga

Quando a mesma configuração vale para todos os nós:

```yaml
/**:
   ros__parameters:
      background_b: 255
      background_g: 86
      background_r: 150
```

---

## Namespaces

Namespaces únicos permitem subir dois nós sem conflito. Quando são muitos nós,
declarar namespace um por um fica insustentável — `PushRosNamespace` empurra o
namespace para tudo que estiver dentro do grupo:

```python
from launch.actions import GroupAction
from launch_ros.actions import PushRosNamespace

turtlesim_world_2 = IncludeLaunchDescription(
    PythonLaunchDescriptionSource([os.path.join(
        get_package_share_directory('launch_tutorial'), 'launch'),
        '/turtlesim_world_2.launch.py'])
)

turtlesim_world_2_with_namespace = GroupAction(
    actions=[
        PushRosNamespace('turtlesim2'),
        turtlesim_world_2,
    ]
)
```

Isso permite incluir o **mesmo** launch file duas vezes, em namespaces
diferentes, sem duplicar uma linha de código.

---

## Reusando nós

Dois nós do mesmo executável convivem se tiverem nomes e parâmetros diferentes:

```python
def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'target_frame', default_value='turtle1',
            description='Target frame name.'
        ),
        Node(
            package='turtle_tf2_py',
            executable='turtle_tf2_broadcaster',
            name='broadcaster1',
            parameters=[{'turtlename': 'turtle1'}]
        ),
        Node(
            package='turtle_tf2_py',
            executable='turtle_tf2_broadcaster',
            name='broadcaster2',
            parameters=[{'turtlename': 'turtle2'}]
        ),
        Node(
            package='turtle_tf2_py',
            executable='turtle_tf2_listener',
            name='listener',
            parameters=[{'target_frame': LaunchConfiguration('target_frame')}]
        ),
    ])
```

---

## Remapping

```python
def generate_launch_description():
    return LaunchDescription([
        Node(
            package='turtlesim',
            executable='mimic',
            name='mimic',
            remappings=[
                ('/input/pose', '/turtle2/pose'),
                ('/output/cmd_vel', '/turtlesim2/turtle1/cmd_vel'),
            ]
        )
    ])
```

Este arquivo pega a pose da `turtle2` e a transforma em comando de velocidade
para a tartaruga do `turtlesim2`.

---

## Instalando tudo

```python
# setup.py
data_files=[
    (os.path.join('share', package_name, 'launch'),
        glob(os.path.join('launch', '*.launch.py'))),
    (os.path.join('share', package_name, 'config'),
        glob(os.path.join('config', '*.yaml'))),
],
```

Esquecer a linha do `config/` é a causa mais comum de "meu YAML não é lido":
ele ficou em `src/` e nunca chegou em `install/`.

```bash
ros2 launch launch_tutorial launch_turtlesim.launch.py
```

Os exercícios 8, 9 e 10 de [Exercícios de launch](10-launch-exercicios.md)
cobrem exatamente este capítulo.
