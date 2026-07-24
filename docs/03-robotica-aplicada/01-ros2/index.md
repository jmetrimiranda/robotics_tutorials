# ROS 2

*Do primeiro `source` até um sistema multi-robô com tf2 e launch files.*

Este capítulo é a versão navegável do cheat sheet de ROS 2 — reorganizado em
seções, com os comandos conferidos e uma bateria de exercícios no fim de cada
página.

## Como estudar

O material tem três tipos de conhecimento, e cada um pede um método diferente.
Misturar os três no mesmo método é o jeito mais rápido de sentir que estudou
sem ter aprendido.

| Tipo | Exemplo | Como revisar |
|---|---|---|
| **Fato solto** | `ros2 topic hz`, `--packages-select` | Anki, cartão com digitação |
| **Esqueleto** | o `main()` de um nó, o corpo de um launch | Escrever de memória e dar `diff` |
| **Procedimento** | fazer o sistema subir e depurar | Os exercícios de cada página |

!!! tip "O drill do esqueleto"
    Guarde os arquivos de referência em `_gabaritos/`. O treino é: abrir um
    arquivo vazio, escrever o esqueleto de memória e rodar

    ```bash
    diff -u _gabaritos/action_server.py /tmp/tentativa.py
    ```

    O `diff` é o corretor honesto que o flashcard não consegue ser. Tentar
    produzir antes de ver o gabarito vale muito mais que reler.

!!! tip "Intercale"
    Uma sessão misturando tópico + serviço + action + launch retém mais que
    quatro sessões separadas por assunto — mesmo parecendo pior enquanto você faz.

## Mapa

<div class="grid cards" markdown>

- **[CLI Tools](01-cli-tools.md)** — ambiente, nós, tópicos, serviços,
  parâmetros, actions, bag e logs pela linha de comando
- **[Workspace e pacotes](02-workspace-e-pacotes.md)** — colcon, underlay/overlay,
  criar e instalar pacotes
- **[Publisher/Subscriber e Serviços](03-pub-sub-e-servicos.md)** — rclpy na prática
- **[Actions](04-actions.md)** — interface, servidor e cliente em Python
- **[Launch](05-launch-criando.md)** — do arquivo mínimo até projetos grandes
- **[tf2](11-tf2.md)** — broadcaster, listener e árvore de frames
- **[Flashcards](99-flashcards.md)** — o baralho inteiro em texto

</div>

## Sobre a distro

Todo o material foi escrito para o **Foxy Fitzroy**. O Foxy está em
*end-of-life* — as distros com suporte hoje são Humble, Jazzy e Kilted.

Vale decidir isso agora, enquanto o capítulo tem dez páginas e não duzentas.
O que muda se você migrar:

- `static_transform_publisher` passou a usar flags nomeadas
  (`--x --y --z --yaw --pitch --roll --frame-id --child-frame-id`);
  a forma posicional ficou deprecada.
- `rosbag2` mudou o formato de gravação padrão.
- `quaternion_from_euler` deixou de ser função copiada no tutorial e virou
  dependência do pacote `tf_transformations`.
- O resto — nós, tópicos, serviços, parâmetros, actions, colcon, launch — é
  praticamente idêntico.

Na prática: trocar `foxy` por `jazzy` resolve 90% do texto. Os pontos que
exigem atenção estão marcados com `!!! warning` ao longo das páginas.
