# Unitree Go2 EDU

*O quadrúpede, o lidar em cima dele e os SDKs que fazem os dois conversarem.*

A versão **EDU** é a única da linha Go2 que permite desenvolvimento secundário —
AIR e PRO não expõem SDK. É por isso que praticamente toda a literatura de
pesquisa e todas as stacks de autonomia abertas assumem a EDU.

O que a EDU tem a mais que importa aqui:

- **SDK** (C++, Python e interface ROS 2) sobre DDS — as outras versões não têm.
- **Computação embarcada** opcional: módulo NVIDIA Jetson Orin (Nano 8 GB, até
  40 TOPS; ou NX 16 GB, até 100 TOPS), alimentado pela saída DC 28,8 V do robô.
- **RJ45** para ligar um PC externo ou o Orin na rede interna do robô.
- **Sensores de força no pé** (exclusivos da EDU) e módulo de posição sem fio.
- **Bateria de 15000 mAh** (2–4 h) contra 8000 mAh das outras.

O lidar que vem de fábrica é o **Unitree 4D L1** (905 nm, FOV 360° × 90°,
~21.600 amostras/s), com IMU integrada. Ele é suficiente para a stack da CMU,
mas é comum trocar ou complementar por um **Livox Mid-360 / Mid-360S** quando se
quer alcance maior e nuvem mais densa — daí a presença do manual do Mid-360S e
da peça de montagem nos links.

## Mapa

<div class="grid cards" markdown>

- **[Links e referências](01-links.md)** — documentação oficial, datasheets,
  stack de navegação da CMU, SDKs e a peça 3D do suporte do lidar

</div>
