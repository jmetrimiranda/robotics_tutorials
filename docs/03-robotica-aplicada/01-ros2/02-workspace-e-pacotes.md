# Workspace e pacotes

*Onde o código mora e como ele vira executável.*

---

## O workspace

Um workspace ROS é um diretório com uma estrutura específica. Ele sempre tem um
subdiretório `src/`, onde fica o código-fonte dos pacotes. O build cria mais
três, ao lado dele:

| Diretório | Conteúdo |
|---|---|
| `build/` | arquivos intermediários, uma subpasta por pacote |
| `install/` | onde cada pacote é instalado, um subdiretório por pacote |
| `log/` | logs de cada invocação do colcon |
| `src/` | o seu código |

```
ros2_ws/
├── build/
├── install/
├── log/
└── src/
    └── go2_missions/
        ├── package.xml
        ├── setup.py
        ├── setup.cfg
        ├── resource/
        │   └── go2_missions
        ├── test/
        │   ├── test_copyright.py
        │   ├── test_flake8.py
        │   └── test_pep257.py
        └── go2_missions/
            ├── __init__.py
            ├── patrol_node.py
            ├── waypoint_logger.py
            └── geometry_utils.py
```

## Underlay e overlay

O workspace que você constrói funciona como **overlay**: uma camada por cima de
um workspace base, o **underlay** — normalmente a própria distro em
`/opt/ros/foxy`.

A regra que não se quebra: **toda dependência dos seus pacotes precisa existir
no underlay**, porque o overlay vai buscá-la lá.

```bash
source /opt/ros/foxy/setup.bash    # underlay, primeiro
source install/local_setup.bash    # overlay, depois
```

| Arquivo | O que expõe |
|---|---|
| `local_setup.bash` | só os pacotes **deste** workspace |
| `setup.bash` | este workspace **mais** os underlays que ele herdou |

Na prática, dar source só no `install/setup.bash` do workspace resolve tudo.

!!! tip
    O overlay tem precedência. Se você modificar o `turtlesim` dentro do seu
    workspace, é a sua versão que roda — até você abrir um terminal em que só
    o Foxy foi carregado.

## Criando e construindo

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone https://github.com/ros/ros_tutorials.git -b foxy-devel
```

Antes de compilar, confira dependências faltando:

```bash
cd ~/ros2_ws
rosdep install -i --from-path src --rosdistro foxy -y
```

E compile, da **raiz** do workspace:

```bash
colcon build
```

```
Starting >>> turtlesim
Finished <<< turtlesim [5.49s]

Summary: 1 package finished [5.58s]
```

### Argumentos que valem a pena

| Argumento | Para quê |
|---|---|
| `--packages-select <pkg>` | compila **só** aquele pacote |
| `--packages-up-to <pkg>` | compila o pacote **mais** suas dependências |
| `--symlink-install` | usa links simbólicos: editar script Python não exige recompilar |
| `--event-handlers console_direct+` | mostra a saída do compilador no console |

!!! warning "Errata do cheat sheet"
    É `--packages-select` e `--packages-up-to` — **plural**, e `select`, não
    `selected`. As formas `--package-selected` e `--package-up-to` do cheat
    sheet original não existem e o colcon aborta.

Testes:

```bash
colcon test
colcon test --packages-select MEU_PKG --ctest-args -R MEU_TESTE
```

---

## Pacotes

Pacote é a unidade organizacional do código ROS 2. Um pacote Python mínimo tem:

```
my_package/
    package.xml            # meta-informação: nome, versão, dependências
    resource/my_package    # arquivo marcador
    setup.cfg
    setup.py               # entry_points e data_files
    my_package/            # mesmo nome do pacote
        __init__.py
```

Um workspace pode ter quantos pacotes você quiser, inclusive de build types
diferentes lado a lado:

```
workspace_folder/
    src/
      cpp_package_1/
          CMakeLists.txt
          include/cpp_package_1/
          package.xml
          src/
      py_package_1/
          package.xml
          resource/py_package_1
          setup.py
          py_package_1/
```

### Criando

Sempre de dentro de `src/`:

```bash
ros2 pkg create --build-type ament_python my_package
```

Variações úteis:

```bash
# já com um executável "Hello World" de exemplo
ros2 pkg create --build-type ament_python --node-name my_node my_package

# já declarando dependências (evita editar package.xml na mão)
ros2 pkg create --build-type ament_python py_srvcli \
  --dependencies rclpy example_interfaces

# pacote CMake (obrigatório para interfaces .msg/.srv/.action)
ros2 pkg create --build-type ament_cmake tutorial_interfaces
```

### Construindo e usando

```bash
cd ~/ros2_ws
colcon build --packages-select my_package
source install/local_setup.bash
ros2 run my_package my_node
```

```
Hi from my_package.
```

### Entry points

Um arquivo `.py` solto dentro do pacote **não** vira executável. Ele precisa
estar registrado no `setup.py`:

```python
entry_points={
    'console_scripts': [
        'nome_executavel = nome_pacote.nome_modulo:main',
    ],
},
```

O padrão: à esquerda o nome que você vai digitar no `ros2 run`, à direita o
caminho do módulo até a função `main`.

Exemplo completo — um pacote `hello_world` com um `first_node.py`:

```python
# hello_world/hello_world/first_node.py
def main():
    print("Hello World")

if __name__ == '__main__':
    main()
```

```python
# hello_world/setup.py
entry_points={
    'console_scripts': [
        'first_node = hello_world.first_node:main',
    ],
},
```

```bash
colcon build --packages-up-to hello_world
source install/local_setup.bash
ros2 run hello_world first_node
```

### Dependências no `package.xml`

Cada `import` do seu código precisa de uma declaração correspondente:

```xml
<exec_depend>rclpy</exec_depend>
<exec_depend>std_msgs</exec_depend>
```

Se você mudar o `package.xml` (nome, versão, descrição, licença), lembre de
espelhar as mesmas alterações no `setup.py`.

---

## Exercícios

### Exercício 1 — Do zero ao executável 🟢

**Objetivo:** o caminho completo sem copiar nada.

**Especificação:** crie o workspace `~/rev_ws`, um pacote `saudacao`, um nó que
imprime seu nome, registre o entry point e rode com `ros2 run`. Sem consultar
esta página.

**✅ Aprovado se:** `ros2 run saudacao meu_no` imprime. Se falhar, o erro que
você recebeu já diz qual etapa faltou — leia antes de olhar a dica.

??? tip "Dica"
    As três etapas que as pessoas esquecem: `entry_points` no `setup.py`,
    `colcon build`, e `source install/local_setup.bash` num terminal **novo**.

### Exercício 2 — Overlay vencendo o underlay 🟡

**Objetivo:** provar na prática que overlay tem precedência.

**Especificação:** clone o `ros_tutorials` no seu workspace, abra
`src/ros_tutorials/turtlesim/src/turtle_frame.cpp` e troque o título da janela
de `"TurtleSim"` para `"MyTurtleSim"` (linha 52). Compile e rode.

Depois abra um terminal onde você faz source **só** do Foxy e rode de novo.

**✅ Aprovado se:** um terminal abre `MyTurtleSim` e o outro abre `TurtleSim`, e
você sabe explicar por quê.

### Exercício 3 — Economia de build 🟡

**Objetivo:** parar de recompilar o mundo.

**Especificação:** com dois ou três pacotes no workspace, meça o tempo de
`colcon build` e compare com `--packages-select`. Depois edite só um `.py` e
descubra, na prática, o que o `--symlink-install` muda.

**✅ Aprovado se:** você consegue dizer em uma frase quando usar cada um dos
três, e conseguiu editar um script Python e ver o efeito **sem** recompilar.

### Exercício 4 — Quebrando de propósito 🟠

**Objetivo:** aprender a ler erro de dependência.

**Especificação:** num pacote que funciona, remova a linha
`<exec_depend>rclpy</exec_depend>` do `package.xml`, apague `build/`, `install/`
e `log/`, e reconstrua. Rode `rosdep install -i --from-path src --rosdistro foxy -y`
e veja o que ele diz.

**✅ Aprovado se:** você sabe distinguir um erro de *build* de um erro de
*dependência declarada* — e sabe por que o pacote pode continuar funcionando na
sua máquina mesmo com a declaração faltando.
