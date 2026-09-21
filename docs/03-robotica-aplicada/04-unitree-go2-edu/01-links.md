# Links e referências

*A lista curta do que realmente se consulta enquanto se trabalha com o Go2 EDU.*

Cada link vem com um comentário do que esperar antes de clicar — o objetivo é
não ter que abrir cinco abas para descobrir qual delas tem a informação.

---

## Navegação autônoma

### Stack de autonomia da CMU

<https://github.com/jizhang-cmu/autonomy_stack_go2>

Repositório da CMU sobre stack de navegação do Unitree Go2 EDU. É a stack
completa: você define um ponto de destino e o robô vai sozinho mapeando o
caminho, ou dirige no joystick e a stack cuida do desvio de obstáculos.

O que tem dentro:

| Módulo | Base |
|---|---|
| SLAM | Point-LIO (`point_lio_unilidar`) |
| Planejador de rota | FAR Planner — grafo de visibilidade |
| Autonomia base | Autonomous Exploration Development Environment — análise de terreno, desvio de colisão, seguimento de waypoints |
| Extras | calibração de IMU, driver de câmera `go2_h264_repub`, ponte de simulação Unity via ROS-TCP-Endpoint |

Três modos de operação: *smart joystick* (padrão — joystick com desvio de
obstáculos), *waypoint* e *manual* (joystick cru, sem desvio).

!!! warning "Pontos de atenção antes de tentar rodar"
    - Exige a versão **EDU** — é a única com suporte de SDK.
    - Usa **apenas o lidar L1 embutido e a IMU dentro dele**. Não é uma stack de
      Mid-360; adaptar exige trocar o nó de SLAM.
    - Branch `foxy-humble`. O computador de bordo vem com Ubuntu 20.04 + **ROS 2
      Foxy**. Em computador externo os autores recomendam Foxy — relatam atraso
      de dados **> 1 s** com Humble.
    - DDS é o **cyclonedds**, e o ROS 2 **não pode estar "sourced"** na hora de
      compilá-lo.
    - Rede: porta do robô em `192.168.123.18`, computador externo em
      `192.168.123.100`.
    - Calibração de IMU é obrigatória uma vez (`ros2 run calibrate_imu
      calibrate_imu`) e grava `imu_calib_data.yaml` no Desktop — não mude nome
      nem local do arquivo.
    - Limitação conhecida: obstáculos precisam ter mais de ~0,3 m de altura por
      causa do ruído do lidar.

---

## Lidar Livox Mid-360S

### Manual do usuário (PDF)

<https://terra-1-g.djicdn.com/65c028cd298f4669a7f0e40e50ba1131/Mid-360S/UM/20260601/Livox_Mid-360s_User_Manual_en.pdf>

Manual do lidar Mid-360S, v1.0 (2026.04), 30 páginas. O PDF é cifrado
(AES-256) — alguns leitores online falham em abri-lo; baixe e abra localmente,
ou extraia o texto com `pdftotext -layout arquivo.pdf saida.txt`.

O que dá para tirar dele, para poupar a leitura:

**FOV e alcance**

- 360° na horizontal, **59° na vertical** no máximo — de **+52° a −7°**.
- O alcance efetivo **varia dentro do FOV vertical**: quanto mais perto da borda
  inferior, maior o alcance. Um alvo com 10% de refletividade na borda inferior
  é detectado a até **40 m**.
- Varredura **não repetitiva**: com 0,1 s de integração a cobertura equivale a
  um mecânico de 32 linhas; com 0,5 s passa de 70%, acima de um de 64 linhas.

**Alimentação**

- 9 V a 27 V, **12 V recomendado**. Acima de 27 V pode danificar.
- 6,5 W em regime normal; pico de partida de 18 W (0 °C a 35 °C) por ~8 s.
- Entre −20 °C e 0 °C entra em auto-aquecimento e chega a 14 W por até 10 min.

**Conector e rede**

- Conector **M12 A-Code 12 pinos** (macho, IP67). O cabo splitter 1-para-3
  (vendido à parte, 1,5 m) abre em alimentação, Ethernet RJ-45 e cabo de função.
- Dados por **UDP**. IP estático de fábrica: `192.168.1.1XX`, onde `XX` são os
  dois últimos dígitos do número de série. Máscara `255.255.255.0`, gateway
  `192.168.1.1`. O PC deve ir para IP estático (ex.: `192.168.1.50`).
- **Nunca ligue um dispositivo PoE** ao RJ-45 — dano irreversível.
- Sincronismo de tempo por **PTP (IEEE 1588-2008)** ou **GPS** (pinos 8 e 10,
  GPRMC a 9600 8N1).

**Montagem**

- Quatro furos **M3 com 5 mm de profundidade** na face inferior; corpo de
  aproximadamente 65 × 65 × 60 mm.
- Sem exigência de orientação, mas de cabeça para baixo exige ≥ 0,5 m do chão.
- Deixe ≥ 10 mm livres ao redor para dissipação; base metálica de ≥ 3 mm é o
  recomendado. O produto **não suporta carga extra**.

**IMU integrada**

- Acelerômetro e giroscópio de 3 eixos, **200 Hz**, ligada por padrão.
- Posição da IMU no referencial da nuvem de pontos:
  `x = 11,0 mm`, `y = 23,29 mm`, `z = −44,12 mm` — é esse o offset que vai na tf.

!!! warning "Dois lidars apontados um para o outro"
    O manual é explícito: evitar sobreposição de FOV entre lidars. Feixes
    apontados diretamente um para o outro podem causar **dano irreversível**.

!!! note "As especificações completas não estão no manual"
    A seção 5.2 do PDF apenas remete para <https://www.livoxtech.com/mid-360s/specs>.

### Página de downloads oficial

<https://www.livoxtech.com/mid-360s/downloads>

Página principal de documentos do Mid-360S. É de onde sai tudo: manual do
usuário, *Product Information*, **modelos 3D em `.stp`** (do sensor, do FOV e do
cabo splitter), Livox Viewer 2 para Windows e Linux, e o firmware com as release
notes.

Não tem SDK nem driver aqui — esses ficam no GitHub da Livox:

- SDK: <https://github.com/Livox-SDK/Livox-SDK2>
- Driver ROS 2: <https://github.com/Livox-SDK> (`livox_ros_driver2`)
- Protocolo de comunicação e sincronismo: <https://livox-wiki-cn.readthedocs.io>

### Peça 3D de montagem no Go2

<https://github.com/PathOn-AI/PathOnRoboticsOSS/tree/main/hardware/mounts/livox_mid360_go2_mount>

Peça 3D para o lidar Mid-360 no Go2. Suporte em balanço que joga o sensor à
frente da cabeça do robô, para o corpo não entrar no cone inferior do FOV.

- Arquivo: `cad/livox_mid360_mount.stl` — **só malha**, não há STEP.
- Impressão: **PETG** recomendado (PLA+ como alternativa), camada 0,20 mm, 4
  perímetros, 30–40% giroide, suportes em árvore sob o balanço. O motivo do PETG
  é carga sustentada: ~265 g na ponta de um braço longo, e PLA sofre *creep*.
- Fixação: 4 × M3 (≈ M3×8) no sensor; M3 com porcas na T-track da base.
  Arruelas de sorbothane são opcionais, para não passar vibração à IMU interna.
- **Não parafusa direto no robô**: depende de uma placa-base T-Track impressa
  separadamente (o README aponta para o modelo "Base Unitree Go2 (T-Track 30)"
  no Printables).
- Na montagem, confirme que o **+X do sensor aponta para a frente** e que o domo
  fica nivelado com o robô de pé — as stacks de SLAM assumem isso.

!!! warning "Mid-360 não é Mid-360S"
    O suporte foi feito para o **Mid-360**. O padrão de 4 × M3 do Mid-360S
    coincide, mas as dimensões externas e o conector (M12 aviação no 360S)
    mudam. Confira o `.stp` oficial antes de imprimir.

!!! note "Licença"
    Os arquivos de hardware do repositório usam uma *Standard Digital File
    License*: impressão pessoal e não comercial. Uso educacional, comercial ou
    organizacional exige autorização por escrito. Leia a licença antes de usar.

---

## Unitree Go2 EDU — hardware

### Datasheet e especificações

<https://www.docs.quadruped.de/projects/go2/html/Overview_1.html#hardware-architecture>

Datasheet e especificações do Unitree Go2 EDU, mantido pela QUADRUPED ROBOTICS.
É a tabela comparativa mais completa entre AIR, PRO e EDU em um lugar só, e a
que responde rápido "essa peça existe na minha versão?".

Além da arquitetura de hardware, a página traz:

- Comparativo de payload, velocidade (EDU até 3,7 m/s), ângulo de subida,
  bateria e garantia entre as três versões.
- Interfaces físicas: saída DC 28,8 V para o Orin, RJ45 e porta **SBUS**
  (pinagem `NC / GND / SBUS` — **não fornece alimentação**).
- Especificações do lidar embutido **Unitree 4D L1**.
- Add-ons oficiais: MID-360, Hesai XT16R, Intel D435i, braço D1/D1-550.
- **Convenções de juntas**: pernas 0–3 como FR/FL/RR/RL, juntas 0–2 como
  hip/thigh/calf, limites de cada junta e eixos pela regra da mão direita — é a
  referência para escrever qualquer controle de baixo nível.
- Tabela de cores do led indicador.

!!! tip "A seção de arquitetura é só diagrama"
    O bloco *Hardware Architecture* é composto apenas por imagens, sem texto. Os
    detalhes de rede e IP ficam na página do driver ROS 2 do mesmo site.

---

## Unitree SDK

As páginas de suporte da Unitree são renderizadas por JavaScript — abrem no
navegador normalmente, mas não em ferramentas de linha de comando como `curl`.

### Quick Start

<https://support.unitree.com/home/en/developer/Quick_start>

Ponto de entrada do SDK2: configuração de rede com o robô, dependências,
compilação e o primeiro exemplo rodando. É a primeira página a abrir antes de
qualquer outra coisa do SDK.

### Interface ROS 2

<https://support.unitree.com/home/en/developer/ROS2_service>

Interface ROS 2 da Unitree — os pacotes de mensagens e serviços
(`unitree_go`, `unitree_api`) e como assinar os tópicos de estado e publicar
comandos a partir de um nó ROS 2.

### Interface Python

<https://support.unitree.com/home/en/developer/Python>

Documentação da interface Python do SDK2.

!!! note "Disclaimer sobre o repositório Python"
    O repositório [`unitree_sdk2_python`](https://github.com/unitreerobotics/unitree_sdk2_python)
    é dividido em duas partes: **`example/`** e **`unitree_sdk2py/`**. É dentro
    deste último que as funções são construídas, para então serem usadas em
    `example/`. Se você quiser entender o que está acontecendo de verdade — e
    não só copiar um exemplo — leia o segundo.

    O diretório do Go2 fica em
    <https://github.com/unitreerobotics/unitree_sdk2_python/tree/master/unitree_sdk2py/go2>
    e se organiza assim:

    | Módulo | Para que serve |
    |---|---|
    | `sport` | cliente de *sport mode* — locomoção, postura, marcha, comandos de movimento |
    | `obstacles_avoid` | liga/desliga e configura o desvio de obstáculos |
    | `robot_state` | consulta e gerencia os serviços e o estado do robô |
    | `video` | acesso ao stream da câmera embarcada |
    | `vui` | interface de usuário — led e áudio |

    Lendo o `sport/sport_client.py`, por exemplo, você vê exatamente qual
    chamada de API cada método dispara — informação que o exemplo esconde.
