# Launch em pacotes

*Tirando o arquivo do "solto na pasta" e colocando onde o ROS acha.*

---

## A convenção

Por convenção, todos os launch files de um pacote ficam numa pasta chamada
`launch/`, dentro do pacote:

```
src/
  py_launch_example/
    launch/
      my_script_launch.py
    package.xml
    py_launch_example/
    resource/
    setup.cfg
    setup.py
    test/
```

O nome do arquivo precisa terminar em `_launch.py` **ou** `.launch.py` — sem
isso o `ros2 launch` não o encontra.

## Fazendo o colcon instalar

Um arquivo em `src/` não é visível para o `ros2 launch`: ele precisa ser
copiado para `install/`. Isso se declara no `setup.py`, em `data_files`:

```python
import os
from glob import glob
from setuptools import setup

package_name = 'py_launch_example'

setup(
    # ... outros parâmetros
    data_files=[
        # ... outros data files
        (os.path.join('share', package_name, 'launch'),
            glob(os.path.join('launch', '*launch.[pxy][yma]*')))
    ]
)
```

O glob `*launch.[pxy][yma]*` casa com `.launch.py`, `.launch.xml` e
`.launch.yaml` de uma vez só. Os dois imports no topo não são opcionais.

## O arquivo

```python
import launch
import launch_ros.actions


def generate_launch_description():
    return launch.LaunchDescription([
        launch_ros.actions.Node(
            package='demo_nodes_cpp',
            executable='talker',
            name='talker'),
    ])
```

## Construindo e rodando

```bash
colcon build
source install/local_setup.bash
ros2 launch py_launch_example my_script_launch.py
```

!!! tip "A pegadinha do src/ vs install/"
    Se você editar o launch file e nada mudar, é quase sempre isso: você editou
    o `src/` e o `ros2 launch` está lendo o `install/`. Rode `colcon build` de
    novo — ou compile com `--symlink-install` e o problema some.

## Declarando a dependência

É boa prática avisar que o pacote depende da ferramenta de launch:

```xml
<exec_depend>ros2launch</exec_depend>
```
