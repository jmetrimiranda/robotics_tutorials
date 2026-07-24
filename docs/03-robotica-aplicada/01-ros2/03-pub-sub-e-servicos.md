# Publisher/Subscriber e Serviços

*A mesma coisa do capítulo anterior, agora em Python.*

---

## A pipeline de todo programa ROS

Tudo que você vai escrever daqui em diante segue quatro passos, documentados na
[rclpy](https://docs.ros2.org/foxy/api/rclpy/api/init_shutdown.html):

1. **Inicialização** — `rclpy.init()`, antes de qualquer nó existir.
2. **Criar um ou mais nós** — instanciando `Node` ou herdando dele.
3. **Processar callbacks** — `spin()`, `spin_once()` ou
   `spin_until_future_complete()`.
4. **Shutdown** — `rclpy.shutdown()`.

```python
def main(args=None):
    rclpy.init(args=args)
    node = MinhaClasse()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

!!! tip "Esse é o primeiro esqueleto para o drill do `diff`"
    Escreva-o de memória em um arquivo vazio antes de continuar lendo.

Criado o nó, é por ele que você cria publishers, subscriptions, serviços e
actions. O `spin` é quem mantém o processo vivo entregando as mensagens que
chegam aos callbacks — sem ele, o nó existe e não faz nada.

### A classe `Node`

Herdar de `rclpy.node.Node` e chamar o construtor do pai é o padrão:

```python
class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('minimal_publisher')
```

A string é o nome que aparece no `ros2 node list`. Outros parâmetros do
construtor (`context`, `cli_args`, `namespace`) estão na
[documentação do Node](https://docs.ros2.org/foxy/api/rclpy/api/node.html).

Três métodos que você vai usar o tempo todo:

| Método | Argumentos principais | Devolve |
|---|---|---|
| `create_publisher` | `msg_type`, `topic`, `qos_profile` | um publisher |
| `create_timer` | `timer_period_sec`, `callback` | um `Timer` |
| `get_logger()` | — | o logger do nó |

O `qos_profile` (aquele `10`) é o tamanho da fila: quantas mensagens ficam em
buffer se o subscriber não consegue consumir na velocidade da publicação.

O `get_logger().info('texto')` sai como `[INFO] [nome_do_node]: texto` e também
é gravado em `~/.ros/log/`.

---

## Publisher

```bash
ros2 pkg create --build-type ament_python py_pubsub
cd ~/ros2_ws/src/py_pubsub/py_pubsub
wget https://raw.githubusercontent.com/ros2/examples/foxy/rclpy/topics/minimal_publisher/examples_rclpy_minimal_publisher/publisher_member_function.py
```

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class MinimalPublisher(Node):

    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello World: %d' % self.i
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)
        self.i += 1


def main(args=None):
    rclpy.init(args=args)
    minimal_publisher = MinimalPublisher()
    rclpy.spin(minimal_publisher)
    minimal_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

A leitura: no construtor criamos o publisher (tipo, tópico, fila) e um timer
que dispara `timer_callback` a cada 0,5 s. O callback monta a mensagem,
publica, loga e incrementa o contador.

## Subscriber

```bash
wget https://raw.githubusercontent.com/ros2/examples/foxy/rclpy/topics/minimal_subscriber/examples_rclpy_minimal_subscriber/subscriber_member_function.py
```

```python
class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            String,
            'topic',
            self.listener_callback,
            10)
        self.subscription  # evita o warning de variável não usada

    def listener_callback(self, msg):
        self.get_logger().info('I heard: "%s"' % msg.data)
```

Note a simetria: publisher tem `(tipo, tópico, fila)`, subscription tem
`(tipo, tópico, callback, fila)`. O callback é a única diferença estrutural.

### Fechando o pacote

```xml
<!-- package.xml -->
<exec_depend>rclpy</exec_depend>
<exec_depend>std_msgs</exec_depend>
```

```python
# setup.py
entry_points={
    'console_scripts': [
        'talker = py_pubsub.publisher_member_function:main',
        'listener = py_pubsub.subscriber_member_function:main',
    ],
},
```

```bash
cd ~/ros2_ws
colcon build --packages-select py_pubsub
source install/local_setup.bash
ros2 run py_pubsub talker      # em um terminal
ros2 run py_pubsub listener    # em outro
```

---

## Serviço (servidor)

Quem envia a requisição é o **cliente**; quem responde é o **servidor**. A
estrutura do request e da response é definida pelo arquivo `.srv`:

```
int64 a
int64 b
---
int64 sum
```

```bash
ros2 pkg create --build-type ament_python py_srvcli \
  --dependencies rclpy example_interfaces
```

```python
from example_interfaces.srv import AddTwoInts

import rclpy
from rclpy.node import Node


class MinimalService(Node):

    def __init__(self):
        super().__init__('minimal_service')
        self.srv = self.create_service(
            AddTwoInts, 'add_two_ints', self.add_two_ints_callback)

    def add_two_ints_callback(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info(
            'Incoming request\na: %d b: %d' % (request.a, request.b))
        return response


def main(args=None):
    rclpy.init(args=args)
    minimal_service = MinimalService()
    rclpy.spin(minimal_service)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

!!! warning "O erro clássico"
    O callback **precisa** terminar com `return response`. Sem isso o cliente
    fica esperando para sempre e a mensagem de erro não ajuda em nada.

## Serviço (cliente)

```python
import sys

from example_interfaces.srv import AddTwoInts
import rclpy
from rclpy.node import Node


class MinimalClientAsync(Node):

    def __init__(self):
        super().__init__('minimal_client_async')
        self.cli = self.create_client(AddTwoInts, 'add_two_ints')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        self.req = AddTwoInts.Request()

    def send_request(self, a, b):
        self.req.a = a
        self.req.b = b
        self.future = self.cli.call_async(self.req)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()


def main(args=None):
    rclpy.init(args=args)
    minimal_client = MinimalClientAsync()
    response = minimal_client.send_request(int(sys.argv[1]), int(sys.argv[2]))
    minimal_client.get_logger().info(
        'Result of add_two_ints: for %d + %d = %d' %
        (int(sys.argv[1]), int(sys.argv[2]), response.sum))
    minimal_client.destroy_node()
    rclpy.shutdown()
```

O cliente tem mais coisa acontecendo que o servidor. Em quatro passos:

1. criar a instância de cliente pelo nó;
2. **esperar** o servidor ficar disponível;
3. montar o `Request`;
4. chamar de forma assíncrona (`call_async`) e bloquear no
   `spin_until_future_complete` até o `Future` resolver.

```bash
ros2 run py_srvcli service        # terminal 1
ros2 run py_srvcli client 2 3     # terminal 2
```

---

## Parâmetros dentro da classe

```python
import rclpy
import rclpy.node


class MinimalParam(rclpy.node.Node):

    def __init__(self):
        super().__init__('minimal_param_node')
        self.declare_parameter('my_parameter', 'world')
        self.timer = self.create_timer(1, self.timer_callback)

    def timer_callback(self):
        my_param = self.get_parameter('my_parameter').get_parameter_value().string_value
        self.get_logger().info('Hello %s!' % my_param)

        my_new_param = rclpy.parameter.Parameter(
            'my_parameter',
            rclpy.Parameter.Type.STRING,
            'world'
        )
        self.set_parameters([my_new_param])


def main():
    rclpy.init()
    node = MinimalParam()
    rclpy.spin(node)


if __name__ == '__main__':
    main()
```

`declare_parameter(nome, valor_padrão)` declara e define. A leitura é sempre
`get_parameter(nome).get_parameter_value().<tipo>_value` — existe
`string_value`, `integer_value`, `double_value`, `bool_value` e as versões
`_array_`.

!!! warning "Errata do cheat sheet"
    No original o `def main()` aparece indentado **dentro** da classe. Ele é
    função de módulo: precisa estar na margem esquerda, ou o entry point não
    encontra nada.

    Repare também que esse exemplo, do jeito que está, **reescreve** o
    parâmetro com `'world'` a cada segundo — o `ros2 param set` parece não
    funcionar. É proposital no tutorial, mas é um bom exercício remover.

### Descrição e restrições

```python
from rcl_interfaces.msg import ParameterDescriptor

my_parameter_descriptor = ParameterDescriptor(description='This parameter is mine!')
self.declare_parameter('my_parameter', 'world', my_parameter_descriptor)
```

```bash
ros2 param describe /minimal_param_node my_parameter
```

### Mudando de fora

```bash
ros2 param list
ros2 param set /minimal_param_node my_parameter earth
```

Ou por launch file:

```python
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='python_parameters',
            executable='minimal_param_node',
            name='custom_minimal_param_node',
            output='screen',
            emulate_tty=True,
            parameters=[
                {'my_parameter': 'earth'}
            ]
        )
    ])
```

Para o colcon instalar o launch file:

```python
# setup.py
data_files=[
    (os.path.join('share', package_name),
        glob('launch/*launch.[pxy][yma]*')),
],
```

---

## Interfaces customizadas

Quando as mensagens prontas não servem, você cria as suas. Elas ficam num
pacote **separado** — e esse pacote precisa ser `ament_cmake`, porque a geração
de código é feita pelo `rosidl`, que só roda em CMake. O resultado pode ser
usado tanto por C++ quanto por Python.

```bash
ros2 pkg create --build-type ament_cmake tutorial_interfaces
cd tutorial_interfaces
mkdir msg srv
```

```
# msg/Num.msg
int64 num
```

```
# msg/Sphere.msg
geometry_msgs/Point center
float64 radius
```

```
# srv/AddThreeInts.srv
int64 a
int64 b
int64 c
---
int64 sum
```

### `CMakeLists.txt`

```cmake
find_package(geometry_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Num.msg"
  "msg/Sphere.msg"
  "srv/AddThreeInts.srv"
  DEPENDENCIES geometry_msgs
)
```

### `package.xml`

```xml
<depend>geometry_msgs</depend>
<buildtool_depend>rosidl_default_generators</buildtool_depend>
<exec_depend>rosidl_default_runtime</exec_depend>
<member_of_group>rosidl_interface_packages</member_of_group>
```

### Construindo e usando

```bash
cd ~/ros2_ws
colcon build --packages-select tutorial_interfaces
source install/setup.bash
ros2 interface show tutorial_interfaces/msg/Num
```

No código, muda só o import e o tipo:

```python
from tutorial_interfaces.msg import Num          # antes: std_msgs.msg.String

self.publisher_ = self.create_publisher(Num, 'topic', 10)
msg = Num()
msg.num = self.i
```

E o pacote que **usa** a interface precisa declarar isso:

```xml
<exec_depend>tutorial_interfaces</exec_depend>
```

```bash
colcon build --packages-select py_pubsub
```

---

## Exercícios

### Exercício 1 — Esqueleto no escuro 🟢

**Objetivo:** o drill do `diff`.

**Especificação:** num arquivo vazio, escreva de memória um publisher completo:
imports, classe, construtor com publisher e timer, callback, `main`. Depois
`diff -u` contra o gabarito.

**✅ Aprovado se:** o diff tem menos de 5 linhas de diferença. Repita amanhã.

### Exercício 2 — Contador com parada 🟢

**Objetivo:** sair do copiar e colar.

**Especificação:** modifique o `talker` para publicar apenas 10 mensagens e
depois encerrar sozinho (sem `Ctrl+C`). O `listener` deve continuar vivo.

**✅ Aprovado se:** o talker termina limpo e o listener recebeu exatamente 10.

??? tip "Dica"
    O callback do timer pode chamar `raise SystemExit` — ou você pode cancelar
    o timer e chamar `rclpy.shutdown()` de dentro dele.

### Exercício 3 — Serviço de verdade 🟡

**Objetivo:** projetar a interface antes do código.

**Especificação:** crie um pacote de interfaces com um serviço
`DistanciaEuclidiana.srv` que recebe dois pontos (x1,y1,x2,y2) e devolve a
distância. Implemente servidor e cliente. O cliente recebe os quatro números
por `sys.argv`.

**✅ Aprovado se:** `ros2 service list -t` mostra o seu serviço com o seu tipo,
e a chamada funciona também por `ros2 service call` (sem usar seu cliente).

### Exercício 4 — Ponte 🟡

**Objetivo:** um nó que é publisher e subscriber ao mesmo tempo.

**Especificação:** escreva um nó que se inscreve em `/turtle1/pose`, e sempre
que a tartaruga passar de `x > 8.0` publica um `String` em `/aviso`.

**✅ Aprovado se:** `ros2 topic echo /aviso` só mostra mensagem quando a
tartaruga chega perto da parede direita.

### Exercício 5 — Parâmetro que obedece 🟠

**Objetivo:** consertar o exemplo do tutorial.

**Especificação:** pegue o `MinimalParam` e faça o `ros2 param set` funcionar de
verdade — ou seja, o valor definido de fora deve persistir. Depois adicione um
`ParameterDescriptor` com descrição e confira com `ros2 param describe`.

**✅ Aprovado se:** `ros2 param set /minimal_param_node my_parameter earth` muda
a saída do log **permanentemente**, e você sabe explicar qual linha do original
causava o problema.

### Exercício 6 — Interface própria ponta a ponta 🟠

**Objetivo:** o ciclo completo de uma mensagem customizada.

**Especificação:** crie `tutorial_interfaces/msg/Estado.msg` com um `string
nome`, um `float64 bateria` e um `bool ativo`. Faça o `talker` publicar isso e
o `listener` imprimir só quando `bateria < 20.0`.

**✅ Aprovado se:** `ros2 interface show` mostra sua mensagem, `ros2 topic echo`
mostra os três campos, e você sabe listar as **quatro** coisas que precisou
mexer (CMakeLists, package.xml do pacote de interfaces, package.xml do pacote
que usa, e o código).
