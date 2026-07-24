# Flashcards

*Gerado automaticamente a partir de `anki/cartoes.yaml` — não edite à mão.*

Tente responder **antes** de abrir. Para revisar com repetição espaçada,
importe o `ros2-revisao.apkg` no Anki.


## 01 - Ambiente e CLI

??? question "Ativar (source) o ambiente ROS 2 Foxy no terminal atual :material-keyboard:"
    ```bash
    source /opt/ros/foxy/setup.bash
    ```

    Precisa ser feito em TODO terminal novo. Isso é o *underlay*.

??? question "Fazer o source do Foxy automaticamente em todo terminal novo :material-keyboard:"
    ```bash
    echo "source /opt/ros/foxy/setup.bash" >> ~/.bashrc
    ```

    Acrescenta a linha no fim do ~/.bashrc, que roda a cada shell interativo.

??? question "Conferir se as variáveis de ambiente do ROS estão setadas :material-keyboard:"
    ```bash
    printenv | grep -i ROS
    ```

    Deve mostrar ROS_VERSION=2, ROS_PYTHON_VERSION=3, ROS_DISTRO=foxy.

??? question "Definir o domain ID como 42 na sessão atual :material-keyboard:"
    ```bash
    export ROS_DOMAIN_ID=42
    ```

    Só nós com o MESMO domain ID se enxergam. Use 0–101 para ser seguro.

??? question "Limitar toda a comunicação ROS 2 ao localhost :material-keyboard:"
    ```bash
    export ROS_LOCALHOST_ONLY=1
    ```

    Útil em sala de aula / rede compartilhada, para não invadir o grafo dos outros.

??? question "Para que serve o ROS_DOMAIN_ID?"
    ```
    Isola grupos de nós na mesma rede: só nós com o mesmo domain ID se descobrem e se comunicam.
    ```

??? question "Instalar o pacote turtlesim (Foxy) :material-keyboard:"
    ```bash
    sudo apt install ros-foxy-turtlesim
    ```

??? question "Listar os executáveis disponíveis dentro do pacote turtlesim :material-keyboard:"
    ```bash
    ros2 pkg executables turtlesim
    ```

    Retorna turtlesim draw_square, turtlesim mimic, turtlesim turtle_teleop_key, turtlesim turtlesim_node.

??? question "Rodar o nó turtlesim_node do pacote turtlesim :material-keyboard:"
    ```bash
    ros2 run turtlesim turtlesim_node
    ```

    Forma geral: ros2 run <pacote> <executável>

??? question "Rodar o teleop de teclado do turtlesim :material-keyboard:"
    ```bash
    ros2 run turtlesim turtle_teleop_key
    ```

??? question "Instalar o rqt e todos os seus plugins (Foxy) :material-keyboard:"
    ```bash
    sudo apt install ~nros-foxy-rqt*
    ```

    O ~n é um padrão do apt (casa por NOME de pacote). Sem ele o glob não funciona.

??? question "O que é o ROS graph?"
    ```
    A rede de elementos ROS 2 processando dados ao mesmo tempo: nós, tópicos, serviços, actions e parâmetros, e as conexões entre eles.
    ```


## 02 - Nodes e Tópicos

??? question "Listar todos os nós rodando :material-keyboard:"
    ```bash
    ros2 node list
    ```

??? question "Ver publishers, subscribers, serviços e actions do nó /turtlesim :material-keyboard:"
    ```bash
    ros2 node info /turtlesim
    ```

    A barra é obrigatória: o nome é totalmente qualificado.

??? question "Subir o turtlesim_node renomeando o nó para my_turtle :material-keyboard:"
    ```bash
    ros2 run turtlesim turtlesim_node --ros-args --remap __node:=my_turtle
    ```

    Tudo que vem depois de --ros-args é argumento do ROS, não do executável.

??? question "Listar os tópicos ativos :material-keyboard:"
    ```bash
    ros2 topic list
    ```

??? question "Listar os tópicos ativos MOSTRANDO o tipo de mensagem de cada um :material-keyboard:"
    ```bash
    ros2 topic list -t
    ```

    O tipo aparece entre colchetes: /turtle1/cmd_vel [geometry_msgs/msg/Twist]

??? question "Ver ao vivo os dados publicados em /turtle1/cmd_vel :material-keyboard:"
    ```bash
    ros2 topic echo /turtle1/cmd_vel
    ```

    O echo cria um nó subscriber temporário — ele aparece no rqt_graph.

??? question "Ver a estrutura interna da mensagem geometry_msgs/msg/Twist :material-keyboard:"
    ```bash
    ros2 interface show geometry_msgs/msg/Twist
    ```

    ATENÇÃO: é geometry_msgs, com S. Retorna Vector3 linear / Vector3 angular.

??? question "Ver quantos publishers e subscribers tem o tópico /turtle1/cmd_vel :material-keyboard:"
    ```bash
    ros2 topic info /turtle1/cmd_vel
    ```

??? question "Qual flag do 'ros2 topic pub' publica UMA mensagem e encerra? :material-keyboard:"
    ```bash
    --once
    ```

    ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist "{...}"

??? question "Qual flag do 'ros2 topic pub' publica continuamente a 1 Hz? :material-keyboard:"
    ```bash
    -r 1
    ```

    Sem --once nem -r, o pub repete numa taxa padrão.

??? question "Escreva o comando completo para mandar a tartaruga andar e girar uma única vez."
    ```
    ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist \
      "{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 1.8}}"
    ```

    Os argumentos vão em YAML, entre aspas.

??? question "Medir a taxa (Hz) com que /turtle1/pose está sendo publicado :material-keyboard:"
    ```bash
    ros2 topic hz /turtle1/pose
    ```

    Retorna average rate, min, max, std dev e window.

??? question "Medir a largura de banda consumida por /turtle1/pose :material-keyboard:"
    ```bash
    ros2 topic bw /turtle1/pose
    ```

??? question "Abrir a ferramenta gráfica que desenha o grafo de nós e tópicos :material-keyboard:"
    ```bash
    rqt_graph
    ```

??? question "No rqt_graph, o que significa uma seta saindo do círculo (nó) para a caixa (tópico)?"
    ```
    O nó está PUBLICANDO no tópico. Seta da caixa para o círculo = o nó está inscrito (subscriber).
    ```

??? question "Diferença essencial entre tópico e serviço"
    ```
    Tópico é publish/subscribe contínuo e anônimo (muitos para muitos, sem resposta). Serviço é request/response pontual: só devolve dado quando alguém pede.
    ```

??? question "Um nó deve ser responsável por quantas coisas?"
    ```
    Uma só — propósito único e modular (ex.: controlar as rodas, ou publicar o dado de um sensor). O sistema completo é a soma de vários nós.
    ```


## 03 - Serviços e Parâmetros

??? question "Listar todos os serviços ativos :material-keyboard:"
    ```bash
    ros2 service list
    ```

??? question "Listar os serviços ativos mostrando o tipo de cada um :material-keyboard:"
    ```bash
    ros2 service list -t
    ```

??? question "Descobrir o tipo do serviço /clear :material-keyboard:"
    ```bash
    ros2 service type /clear
    ```

    Retorna std_srvs/srv/Empty.

??? question "Achar todos os serviços do tipo std_srvs/srv/Empty :material-keyboard:"
    ```bash
    ros2 service find std_srvs/srv/Empty
    ```

    Retorna /clear e /reset.

??? question "Ver os argumentos de request e response do serviço /spawn :material-keyboard:"
    ```bash
    ros2 interface show turtlesim/srv/Spawn
    ```

    É .srv, não .src. No Foxy o comando aceita o tipo sem extensão.

??? question "Num arquivo .srv, o que separa o request da response?"
    ```
    Três hífens: ---   (acima = request, abaixo = response)
    ```

    No .action são DOIS separadores: goal --- result --- feedback.

??? question "Escreva o comando que cria uma tartaruga chamada 'jorge' em (6,6)."
    ```
    ros2 service call /spawn turtlesim/srv/Spawn \
      "{x: 6.0, y: 6.0, theta: 1.0, name: 'jorge'}"
    ```

    Forma geral: ros2 service call <serviço> <tipo> <argumentos em YAML>

??? question "Listar os parâmetros de todos os nós :material-keyboard:"
    ```bash
    ros2 param list
    ```

??? question "Ler o valor atual do parâmetro background_g do nó /turtlesim :material-keyboard:"
    ```bash
    ros2 param get /turtlesim background_g
    ```

??? question "Mudar em tempo de execução o background_r do /turtlesim para 150 :material-keyboard:"
    ```bash
    ros2 param set /turtlesim background_r 150
    ```

    Responde 'Set parameter successful'. O efeito some ao reiniciar o nó.

??? question "Salvar todos os parâmetros do /turtlesim num arquivo YAML :material-keyboard:"
    ```bash
    ros2 param dump /turtlesim
    ```

    Gera ./turtlesim.yaml no diretório atual.

??? question "Carregar ./turtlesim.yaml num nó /turtlesim que JÁ está rodando :material-keyboard:"
    ```bash
    ros2 param load /turtlesim ./turtlesim.yaml
    ```

??? question "Subir o turtlesim_node já carregando o arquivo ./turtlesim.yaml :material-keyboard:"
    ```bash
    ros2 run turtlesim turtlesim_node --ros-args --params-file ./turtlesim.yaml
    ```

    Diferença para o 'param load': aqui os valores valem desde a inicialização.

??? question "Ver tipo e descrição do parâmetro my_parameter do nó /minimal_param_node :material-keyboard:"
    ```bash
    ros2 param describe /minimal_param_node my_parameter
    ```

    A descrição vem do ParameterDescriptor declarado no código.

??? question "Que tipos um parâmetro pode ter?"
    ```
    integer, float (double), boolean, string e listas desses tipos.
    ```

    Pense em parâmetro como 'a configuração de um nó'.


## 04 - Actions (CLI)

??? question "Listar todas as actions do grafo :material-keyboard:"
    ```bash
    ros2 action list
    ```

??? question "Listar as actions mostrando o tipo :material-keyboard:"
    ```bash
    ros2 action list -t
    ```

    /turtle1/rotate_absolute [turtlesim/action/RotateAbsolute]

??? question "Ver quem é cliente e quem é servidor da action /turtle1/rotate_absolute :material-keyboard:"
    ```bash
    ros2 action info /turtle1/rotate_absolute
    ```

??? question "Ver a estrutura (goal/result/feedback) do tipo RotateAbsolute :material-keyboard:"
    ```bash
    ros2 interface show turtlesim/action/RotateAbsolute
    ```

    theta --- delta --- remaining

??? question "Escreva o comando que manda a tartaruga girar para theta = 1.57."
    ```
    ros2 action send_goal /turtle1/rotate_absolute \
      turtlesim/action/RotateAbsolute "{theta: 1.57}"
    ```

    Forma geral: ros2 action send_goal <action> <tipo> <valores YAML>

??? question "Qual flag acrescentada ao send_goal mostra o feedback contínuo? :material-keyboard:"
    ```bash
    --feedback
    ```

    Sem ela você só vê o goal ID e o result final.

??? question "Quais são as três partes de uma action?"
    ```
    Goal (o pedido), Feedback (progresso periódico) e Result (o resultado final).
    ```

??? question "Action é construída em cima de quê, e para que serve?"
    ```
    Em cima de serviços (goal e result, request/response assíncrono) + tópico (feedback). Serve para tarefas longas, que dão progresso e podem ser canceladas.
    ```

??? question "Qual a ordem dos três blocos num arquivo .action?"
    ```
    # Goal (request)
    ---
    # Result
    ---
    # Feedback
    ```

    Dois separadores '---', três blocos.


## 05 - Bag, rqt_console e logs

??? question "Abrir a ferramenta gráfica de visualização de logs :material-keyboard:"
    ```bash
    ros2 run rqt_console rqt_console
    ```

    Permite filtrar por nível de severidade e salvar/recarregar mensagens.

??? question "Gravar os dados publicados em /turtle1/cmd_vel :material-keyboard:"
    ```bash
    ros2 bag record /turtle1/cmd_vel
    ```

    Ctrl+C encerra. O ros2 bag só grava o que passa por TÓPICO.

??? question "Gravar cmd_vel e pose num diretório chamado 'subset' :material-keyboard:"
    ```bash
    ros2 bag record -o subset /turtle1/cmd_vel /turtle1/pose
    ```

    -o define o nome do diretório; os tópicos vão em lista.

??? question "Ver duração, tamanho, tópicos e contagem de mensagens da bag 'subset' :material-keyboard:"
    ```bash
    ros2 bag info subset
    ```

    O campo Count explica por que o play demora mais que o movimento.

??? question "Reproduzir a bag 'subset' :material-keyboard:"
    ```bash
    ros2 bag play subset
    ```

    Feche o teleop antes, senão os dois disputam o cmd_vel.

??? question "Sem -o, qual o nome do diretório gerado pelo ros2 bag record?"
    ```
    rosbag2_ano_mes_dia-hora_minuto_segundo
    ```

    Dentro dele: um .db3 (sqlite3) e um metadata.yaml.


## 06 - Workspace, colcon e pacotes

??? question "Criar a estrutura inicial de um workspace chamado ros2_ws :material-keyboard:"
    ```bash
    mkdir -p ~/ros2_ws/src
    ```

    Todo pacote vai dentro de src/.

??? question "Compilar o workspace inteiro (da raiz) :material-keyboard:"
    ```bash
    colcon build
    ```

    Gera build/, install/ e log/ ao lado de src/.

??? question "Compilar SÓ o pacote my_package :material-keyboard:"
    ```bash
    colcon build --packages-select my_package
    ```

    PEGADINHA: é --packages-select (plural + select), não --package-selected.

??? question "Compilar my_package E todas as dependências dele (mas não o workspace todo) :material-keyboard:"
    ```bash
    colcon build --packages-up-to my_package
    ```

    PEGADINHA: --packages-up-to, plural.

??? question "Compilar de forma que editar um script Python não exija recompilar :material-keyboard:"
    ```bash
    colcon build --symlink-install
    ```

    Cria links simbólicos em vez de copiar os arquivos para install/.

??? question "Compilar mostrando a saída do compilador direto no console :material-keyboard:"
    ```bash
    colcon build --event-handlers console_direct+
    ```

    Sem isso a saída fica escondida em log/.

??? question "Checar dependências faltando antes do build (da raiz do workspace, Foxy) :material-keyboard:"
    ```bash
    rosdep install -i --from-path src --rosdistro foxy -y
    ```

    Boa prática antes de todo colcon build.

??? question "Rodar os testes do workspace :material-keyboard:"
    ```bash
    colcon test
    ```

??? question "Fazer o source do overlay (o seu workspace), da raiz dele :material-keyboard:"
    ```bash
    source install/local_setup.bash
    ```

??? question "Diferença entre install/setup.bash e install/local_setup.bash"
    ```
    local_setup.bash expõe só os pacotes DESTE workspace. setup.bash expõe este workspace mais os underlays que ele herdou (é o atalho do dia a dia).
    ```

??? question "O que são underlay e overlay?"
    ```
    Underlay = workspace base cujo source você faz primeiro (normalmente a distro, /opt/ros/foxy). Overlay = o seu workspace por cima. Toda dependência do overlay precisa existir no underlay.
    ```

    O overlay tem precedência: um turtlesim modificado no seu ws vence o da distro.

??? question "Quais os 4 diretórios da raiz de um workspace depois do build?"
    ```
    build/ (arquivos intermediários), install/ (onde cada pacote é instalado), log/ (logs de cada invocação do colcon) e src/ (código-fonte).
    ```

??? question "Criar um pacote Python chamado my_package (de dentro de src/) :material-keyboard:"
    ```bash
    ros2 pkg create --build-type ament_python my_package
    ```

??? question "Criar o pacote my_package já com um executável my_node de exemplo :material-keyboard:"
    ```bash
    ros2 pkg create --build-type ament_python --node-name my_node my_package
    ```

??? question "Criar o pacote py_srvcli já declarando as dependências rclpy e example_interfaces :material-keyboard:"
    ```bash
    ros2 pkg create --build-type ament_python py_srvcli --dependencies rclpy example_interfaces
    ```

    Com --dependencies você não precisa editar o package.xml na mão.

??? question "Criar um pacote CMake chamado tutorial_interfaces :material-keyboard:"
    ```bash
    ros2 pkg create --build-type ament_cmake tutorial_interfaces
    ```

    Interfaces (.msg/.srv/.action) SÓ podem ser geradas em pacote ament_cmake.

??? question "Qual o conteúdo mínimo de um pacote ROS 2 em Python?"
    ```
    my_package/
      package.xml            # meta-informação
      resource/my_package    # arquivo marcador
      setup.cfg
      setup.py               # entry_points, data_files
      my_package/            # mesmo nome do pacote, com __init__.py
    ```

??? question "Como registrar o executável 'talker' apontando para publisher_member_function.py?"
    ```
    entry_points={
        'console_scripts': [
            'talker = py_pubsub.publisher_member_function:main',
        ],
    },
    ```

    Padrão: 'nome_executavel = nome_pacote.nome_modulo:main'. Vai no setup.py.

??? question "Como declarar no package.xml que o pacote usa rclpy e std_msgs em tempo de execução?"
    ```
    <exec_depend>rclpy</exec_depend>
    <exec_depend>std_msgs</exec_depend>
    ```


## 07 - rclpy: pub/sub e service/client

??? question "Escreva de memória o main() padrão de um nó ROS 2 em Python."
    ```
    def main(args=None):
        rclpy.init(args=args)
        node = MinhaClasse()
        rclpy.spin(node)
        node.destroy_node()
        rclpy.shutdown()
    
    if __name__ == '__main__':
        main()
    ```

    Pipeline: init -> cria nó -> spin (processa callbacks) -> shutdown.

??? question "Linha que inicializa o contexto ROS no começo do main :material-keyboard:"
    ```bash
    rclpy.init(args=args)
    ```

    Tem que vir ANTES de criar qualquer nó.

??? question "Linha que mantém o nó vivo processando callbacks :material-keyboard:"
    ```bash
    rclpy.spin(node)
    ```

    Variantes: spin_once() e spin_until_future_complete().

??? question "Linha que chama o construtor da classe Node dando o nome 'minimal_publisher' :material-keyboard:"
    ```bash
    super().__init__('minimal_publisher')
    ```

    É esse nome que aparece no 'ros2 node list'.

??? question "Criar um publisher de String no tópico 'topic' com fila 10 :material-keyboard:"
    ```bash
    self.publisher_ = self.create_publisher(String, 'topic', 10)
    ```

    Assinatura: create_publisher(msg_type, topic, qos_profile).

??? question "Criar um timer que chama self.timer_callback a cada 0.5 s :material-keyboard:"
    ```bash
    self.timer = self.create_timer(0.5, self.timer_callback)
    ```

    Assinatura: create_timer(timer_period_sec, callback).

??? question "Escreva a criação de um subscription de String em 'topic' com callback listener_callback."
    ```
    self.subscription = self.create_subscription(
        String,
        'topic',
        self.listener_callback,
        10)
    ```

    Assinatura: create_subscription(msg_type, topic, callback, qos_profile).

??? question "Publicar a mensagem msg no publisher self.publisher_ :material-keyboard:"
    ```bash
    self.publisher_.publish(msg)
    ```

??? question "Logar a string 'Publishing' no console do nó :material-keyboard:"
    ```bash
    self.get_logger().info('Publishing')
    ```

    Sai como [INFO] [nome_do_node]: Publishing. Também grava em ~/.ros/log/.

??? question "Importar o tipo de mensagem String :material-keyboard:"
    ```bash
    from std_msgs.msg import String
    ```

??? question "Criar um serviço AddTwoInts chamado 'add_two_ints' com callback add_two_ints_callback :material-keyboard:"
    ```bash
    self.srv = self.create_service(AddTwoInts, 'add_two_ints', self.add_two_ints_callback)
    ```

    O callback recebe (request, response) e DEVE retornar response.

??? question "Criar um cliente do serviço AddTwoInts chamado 'add_two_ints' :material-keyboard:"
    ```bash
    self.cli = self.create_client(AddTwoInts, 'add_two_ints')
    ```

??? question "Escreva o laço que espera o servidor de serviço ficar disponível."
    ```
    while not self.cli.wait_for_service(timeout_sec=1.0):
        self.get_logger().info('service not available, waiting again...')
    ```

??? question "Enviar o request de forma assíncrona guardando o Future :material-keyboard:"
    ```bash
    self.future = self.cli.call_async(self.req)
    ```

??? question "Bloquear até o Future self.future ser resolvido :material-keyboard:"
    ```bash
    rclpy.spin_until_future_complete(self, self.future)
    ```

    Depois disso, self.future.result() tem a response.

??? question "Escreva o callback de um serviço que soma a e b."
    ```
    def add_two_ints_callback(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info('Incoming request\na: %d b: %d' % (request.a, request.b))
        return response
    ```

    Esquecer o 'return response' é o erro clássico.

??? question "O que é o terceiro argumento (10) do create_publisher?"
    ```
    O QoS / tamanho da fila: quantas mensagens ficam em buffer se o subscriber não consegue consumir na velocidade da publicação.
    ```

??? question "Declarar um parâmetro 'my_parameter' com valor padrão 'world' :material-keyboard:"
    ```bash
    self.declare_parameter('my_parameter', 'world')
    ```

??? question "Ler o valor string do parâmetro 'my_parameter' :material-keyboard:"
    ```bash
    self.get_parameter('my_parameter').get_parameter_value().string_value
    ```

    Outros: integer_value, double_value, bool_value, string_array_value.


## 08 - Interfaces customizadas

??? question "Por que um pacote de interfaces (.msg/.srv/.action) precisa ser ament_cmake?"
    ```
    Porque a geração de código das interfaces é feita pelo rosidl, que só roda em CMake. O pacote gerado pode ser usado depois tanto por C++ quanto por Python.
    ```

??? question "Escreva o bloco do CMakeLists.txt que gera Num.msg, Sphere.msg e AddThreeInts.srv."
    ```
    find_package(rosidl_default_generators REQUIRED)
    
    rosidl_generate_interfaces(${PROJECT_NAME}
      "msg/Num.msg"
      "msg/Sphere.msg"
      "srv/AddThreeInts.srv"
      DEPENDENCIES geometry_msgs
    )
    ```

    DEPENDENCIES lista os pacotes de que as mensagens dependem.

??? question "Quais tags o package.xml de um pacote de interfaces precisa ter?"
    ```
    <buildtool_depend>rosidl_default_generators</buildtool_depend>
    <exec_depend>rosidl_default_runtime</exec_depend>
    <member_of_group>rosidl_interface_packages</member_of_group>
    ```

    Mais um <depend> para cada pacote de mensagens usado (ex.: geometry_msgs).

??? question "Confirmar que a interface tutorial_interfaces/msg/Num foi gerada :material-keyboard:"
    ```bash
    ros2 interface show tutorial_interfaces/msg/Num
    ```

    Faça o source do workspace antes.

??? question "Importar a mensagem customizada Num do pacote tutorial_interfaces :material-keyboard:"
    ```bash
    from tutorial_interfaces.msg import Num
    ```

    Serviço: from tutorial_interfaces.srv import AddThreeInts


## 09 - Actions em Python

??? question "Escreva a criação de um ActionServer de Fibonacci no nome 'fibonacci'."
    ```
    self._action_server = ActionServer(
        self,
        Fibonacci,
        'fibonacci',
        self.execute_callback)
    ```

    from rclpy.action import ActionServer. Os outros callbacks (goal/cancel/handle_accepted) são opcionais.

??? question "Criar um ActionClient de Fibonacci no nome 'fibonacci' :material-keyboard:"
    ```bash
    self._action_client = ActionClient(self, Fibonacci, 'fibonacci')
    ```

    from rclpy.action import ActionClient

??? question "Marcar o goal como concluído com sucesso, dentro do execute_callback :material-keyboard:"
    ```bash
    goal_handle.succeed()
    ```

    Chame ANTES de montar e retornar o Result.

??? question "Publicar o feedback_msg para o cliente :material-keyboard:"
    ```bash
    goal_handle.publish_feedback(feedback_msg)
    ```

    O feedback trafega por tópico, por isso não precisa de Future.

??? question "Enviar o goal de forma assíncrona (cliente) :material-keyboard:"
    ```bash
    self._action_client.send_goal_async(goal_msg)
    ```

    Retorna um Future cujo .result() é um ClientGoalHandle.

??? question "Registrar goal_response_callback para quando o Future do goal resolver :material-keyboard:"
    ```bash
    self._send_goal_future.add_done_callback(self.goal_response_callback)
    ```

??? question "Pedir o resultado ao servidor a partir do goal_handle :material-keyboard:"
    ```bash
    self._get_result_future = goal_handle.get_result_async()
    ```

    Segunda chamada assíncrona: uma para aceitar o goal, outra para o result.

??? question "Pedir o feedback ao enviar o goal (argumento do send_goal_async) :material-keyboard:"
    ```bash
    feedback_callback=self.feedback_callback
    ```

    send_goal_async(goal_msg, feedback_callback=self.feedback_callback)

??? question "Como o cliente verifica se o goal foi aceito?"
    ```
    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected :(')
            return
    ```

??? question "Quais são os callbacks do ActionServer, em ordem, e quais são obrigatórios?"
    ```
    goal_callback (aceita/rejeita) -> handle_accepted_callback (despacha) -> execute_callback (faz o trabalho). Só o execute_callback é obrigatório; os outros têm implementação padrão. Em paralelo existe o cancel_callback.
    ```


## 10 - Launch files

??? question "Rodar o launch multisim.launch.py do pacote turtlesim :material-keyboard:"
    ```bash
    ros2 launch turtlesim multisim.launch.py
    ```

    Forma geral: ros2 launch <pacote> <arquivo>

??? question "Rodar um launch file solto, pelo caminho do arquivo :material-keyboard:"
    ```bash
    ros2 launch turtlesim_mimic_launch.py
    ```

    Funciona, mas o certo é instalar dentro de um pacote.

??? question "Qual flag lista os argumentos aceitos por um launch file? :material-keyboard:"
    ```bash
    --show-args
    ```

    ros2 launch pkg arq.launch.py --show-args

??? question "Passar o argumento use_sim_time=true na linha de comando do launch :material-keyboard:"
    ```bash
    ros2 launch pkg arq.launch.py use_sim_time:=true
    ```

    É := (dois pontos igual), não =.

??? question "Escreva o esqueleto mínimo de um launch file em Python."
    ```
    from launch import LaunchDescription
    from launch_ros.actions import Node
    
    def generate_launch_description():
        return LaunchDescription([
            Node(
                package='turtlesim',
                executable='turtlesim_node',
                name='sim'
            ),
        ])
    ```

    LaunchDescription vem de 'launch'; Node vem de 'launch_ros.actions'.

??? question "Qual função todo launch file Python precisa definir? :material-keyboard:"
    ```bash
    generate_launch_description
    ```

    O ros2 launch procura exatamente por esse nome.

??? question "Declarar o argumento 'cor_r' com default 200 e ler o valor dele."
    ```
    DeclareLaunchArgument('cor_r', default_value='200')
    ...
    LaunchConfiguration('cor_r')
    ```

    DeclareLaunchArgument declara; LaunchConfiguration lê (na hora da execução).

??? question "Incluir outro launch file passando argumentos para ele."
    ```
    IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('meu_pkg'), 'launch'),
            '/filho.launch.py']),
        launch_arguments={'cor_r': '200'}.items()
    )
    ```

    O .items() no fim não é opcional: launch_arguments espera pares, não dict.

??? question "Executar um comando de shell qualquer a partir do launch."
    ```
    ExecuteProcess(
        cmd=[['ros2 topic pub --once /turtle1/cmd_vel ...']],
        shell=True,
        output='screen'
    )
    ```

    É como você chama serviço/tópico de dentro do launch.

??? question "Agrupar actions dentro de um namespace."
    ```
    GroupAction(
        actions=[
            PushRosNamespace('turtlesim2'),
            turtlesim_world_2,
        ]
    )
    ```

    PushRosNamespace vem de launch_ros.actions. Evita declarar namespace nó a nó.

??? question "Executar uma lista de actions 5 segundos depois do início."
    ```
    TimerAction(period=5.0, actions=[...])
    ```

??? question "Disparar uma action quando outro processo terminar."
    ```
    RegisterEventHandler(
        OnProcessExit(
            target_action=processo_anterior,
            on_exit=[proxima_action],
        )
    )
    ```

    Mais robusto que TimerAction: reage a evento, não a relógio.

??? question "Quais são os 5 event handlers de launch e quando disparam?"
    ```
    OnProcessStart (processo começou), OnProcessIO (imprimiu algo), OnExecutionComplete (action concluiu), OnProcessExit (processo morreu), OnShutdown (o launch inteiro está desligando).
    ```

??? question "Remapear tópicos de um nó dentro do launch."
    ```
    remappings=[
        ('/input/pose', '/turtle1/pose'),
        ('/output/cmd_vel', '/turtle2/cmd_vel'),
    ]
    ```

    Par (nome_original, nome_novo).

??? question "O que colocar no setup.py para o colcon instalar os launch files?"
    ```
    data_files=[
        (os.path.join('share', package_name, 'launch'),
            glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
    ],
    ```

    Precisa de 'import os' e 'from glob import glob' no topo.

??? question "Como um YAML de parâmetros aplica a MESMA config a todos os nós?"
    ```
    /**:
       ros__parameters:
          background_r: 150
    ```

    /** é o curinga. Sem ele, a chave é /namespace/nome_do_no.

??? question "Por que o turtle_teleop_key não recebe teclado quando lançado por launch, e como resolver?"
    ```
    Processos do launch não ganham TTY. Solução:
    Node(package='turtlesim', executable='turtle_teleop_key',
         prefix='xterm -e', output='screen')
    ```

    Precisa de: sudo apt install xterm

??? question "No Foxy não existe ForLoop/ForEach. Como repetir N actions com N vindo da CLI?"
    ```
    def gerar(context):
        n = int(LaunchConfiguration('voltas').perform(context))
        return [TimerAction(period=2.0*i, actions=[...]) for i in range(n)]
    
    OpaqueFunction(function=gerar)
    ```

    Só o OpaqueFunction tem acesso ao contexto de execução (.perform).


## 11 - tf2

??? question "Publicar via CLI uma transformação estática 1 m acima de 'world' para 'mystaticturtle' (Foxy) :material-keyboard:"
    ```bash
    ros2 run tf2_ros static_transform_publisher 0 0 1 0 0 0 world mystaticturtle
    ```

    ORDEM NO FOXY: x y z yaw pitch roll frame_id child_frame_id. Cuidado: yaw vem primeiro.

??? question "Ver a transformação entre os frames world e turtle1 :material-keyboard:"
    ```bash
    ros2 run tf2_ros tf2_echo world turtle1
    ```

    Imprime Translation e Rotation (quaternion) a cada atualização.

??? question "Fazer echo no /tf_static (que usa QoS transient_local) :material-keyboard:"
    ```bash
    ros2 topic echo --qos-reliability reliable --qos-durability transient_local /tf_static
    ```

    Sem os flags de QoS você não vê nada: o /tf_static publica uma vez só, com latch.

??? question "Criar o broadcaster de transformações ESTÁTICAS dentro do nó :material-keyboard:"
    ```bash
    self.tf_static_broadcaster = StaticTransformBroadcaster(self)
    ```

    from tf2_ros.static_transform_broadcaster import StaticTransformBroadcaster

??? question "Criar o broadcaster de transformações DINÂMICAS dentro do nó :material-keyboard:"
    ```bash
    self.tf_broadcaster = TransformBroadcaster(self)
    ```

    from tf2_ros import TransformBroadcaster

??? question "Enviar a transformação t :material-keyboard:"
    ```bash
    self.tf_broadcaster.sendTransform(t)
    ```

    sendTransform, camelCase.

??? question "Escreva de memória o preenchimento de um TransformStamped."
    ```
    t = TransformStamped()
    t.header.stamp = self.get_clock().now().to_msg()
    t.header.frame_id = 'world'          # frame PAI
    t.child_frame_id = 'turtle1'         # frame FILHO
    t.transform.translation.x = msg.x
    t.transform.translation.y = msg.y
    t.transform.translation.z = 0.0
    q = quaternion_from_euler(0, 0, msg.theta)
    t.transform.rotation.x = q[0]
    t.transform.rotation.y = q[1]
    t.transform.rotation.z = q[2]
    t.transform.rotation.w = q[3]
    self.tf_broadcaster.sendTransform(t)
    ```

    Ordem: stamp -> frame pai -> frame filho -> translação -> rotação -> envia.

??? question "Escreva as duas linhas que montam um listener de tf2."
    ```
    self.tf_buffer = Buffer()
    self.tf_listener = TransformListener(self.tf_buffer, self)
    ```

    O Buffer guarda ~10 s de transformações; o Listener se inscreve em /tf e /tf_static.

??? question "Consultar a transformação mais recente entre dois frames (com tratamento de erro)."
    ```
    try:
        t = self.tf_buffer.lookup_transform(
            to_frame_rel,
            from_frame_rel,
            rclpy.time.Time())
    except TransformException as ex:
        self.get_logger().info(f'Could not transform: {ex}')
        return
    ```

    rclpy.time.Time() vazio = 'a última disponível'.

??? question "Fórmula de controle usada para uma tartaruga perseguir a outra"
    ```
    comando = ganho x erro
    
    msg.angular.z = 1.0 * atan2(t.transform.translation.y, t.transform.translation.x)
    msg.linear.x  = 0.5 * sqrt(x**2 + y**2)
    ```

    Erro angular = ângulo até o alvo; erro linear = distância euclidiana.

??? question "Para que serve publicar transformações estáticas?"
    ```
    Para descrever a relação fixa entre a base do robô e as partes que não se movem (sensores, por exemplo). Publica uma vez no /tf_static, com latch.
    ```

