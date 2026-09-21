# `video` — câmera frontal

*Um comando só, e um mal-entendido que vale desfazer.*

| | |
|---|---|
| **Pasta** | `unitree_sdk2py/go2/video/` |
| **Classe** | `VideoClient` |
| **Importação** | `from unitree_sdk2py.go2.video.video_client import VideoClient` |
| **Serviço no robô** | `"videohub"` ← repare: não é `"video"` |
| **Versão** | `1.0.0.1` |
| **Tamanho** | 23 linhas — o menor módulo do SDK |

---

## O módulo inteiro, em uma tela

Este é literalmente todo o arquivo `video_client.py`:

```python
import json

from ...rpc.client import Client
from .video_api import *


"""
" class VideoClient
"""
class VideoClient(Client):
    def __init__(self):
        super().__init__(VIDEO_SERVICE_NAME, False)
        #                └─ "videohub"       └─ sem trava de exclusividade

    def Init(self):
        self._SetApiVerson(VIDEO_API_VERSION)
        self._RegistApi(VIDEO_API_ID_GETIMAGESAMPLE, 0)   # registra o único comando

    # 1001
    def GetImageSample(self):
        return self._CallBinary(VIDEO_API_ID_GETIMAGESAMPLE, [])
```

E o arquivo de números (`video_api.py`) tem três constantes:

```python
VIDEO_SERVICE_NAME = "videohub"
VIDEO_API_VERSION = "1.0.0.1"
VIDEO_API_ID_GETIMAGESAMPLE = 1001
```

É só isso. Um método, `GetImageSample()`, que não recebe nada.

!!! note "Curiosidade: o `import json` não serve para nada"
    O arquivo importa `json` e nunca usa. Sobrou da cópia dos outros módulos —
    é o mesmo esqueleto do `vui_client.py` e do `sport_client.py`, mas aqui não
    há dicionário para converter.

---

## Isto **não** é um stream de vídeo

O nome do módulo engana. Você não recebe um vídeo contínuo. Você **pede uma
foto**, e recebe uma foto. Se quiser movimento, pede de novo, num laço.

```
   pede  →  ┌───────┐  ←  1 foto (JPEG)
   pede  →  │ robô  │  ←  1 foto (JPEG)
   pede  →  └───────┘  ←  1 foto (JPEG)
```

**Consequência:** a taxa de quadros que você consegue depende da rapidez da
rede e do robô em atender cada pedido, não de uma configuração sua. Não há como
pedir "30 quadros por segundo". Você pede o mais rápido que der e vê no que dá.

!!! tip "Se você precisa de vídeo de verdade"
    Para um stream contínuo e com menos atraso, o caminho é outro: o Go2
    publica o vídeo comprimido num tópico de rede, e existe um driver dedicado
    que o converte para ROS 2 — o `go2_h264_repub`, que faz parte da
    [stack da CMU](../01-links.md#stack-de-autonomia-da-cmu) e publica em
    `/camera/image/raw`. Este módulo `video` serve para tirar fotos avulsas.

---

## O que `GetImageSample()` devolve

```python
code, data = client.GetImageSample()
```

- **`code`** — `0` se deu certo. Qualquer outro número é erro
  ([tabela](01-anatomia-de-um-client.md#a-tabela-de-codigos-de-erro)).
- **`data`** — os bytes de **um arquivo JPEG completo**, como uma lista de
  números.

O ponto importante: `data` **já é um arquivo `.jpg`**, inteirinho, com cabeçalho
e tudo. Você não precisa montar nada. Basta gravar em disco:

```python
with open("foto.jpg", "wb") as f:
    f.write(bytes(data))     # bytes() converte a lista em bytes de verdade
```

Aquele `bytes(data)` é necessário porque o SDK devolve uma lista de inteiros, e
funções de arquivo e de imagem querem um objeto `bytes`.

!!! warning "`data` vale `None` quando `code != 0`"
    Se der erro, `data` não é uma lista vazia — é `None`. Fazer
    `bytes(None)` levanta `TypeError`. **Sempre teste o `code` primeiro.**

---

## Exemplo 1 — tirar uma foto e salvar

O programa mais simples possível. Não precisa de tela gráfica, não precisa de
OpenCV, e o robô não se mexe.

```python
"""
Tira uma foto com a câmera frontal e salva em disco.
Uso: python3 foto.py enp2s0
"""
import sys

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.video.video_client import VideoClient


def main():
    ChannelFactoryInitialize(0, sys.argv[1] if len(sys.argv) > 1 else None)

    client = VideoClient()
    client.SetTimeout(3.0)
    client.Init()              # sem isto: code = 3103

    print("Pedindo uma foto...")
    code, data = client.GetImageSample()

    if code != 0:
        print(f"Falhou. code = {code}")
        # 3103 = esqueceu o Init()
        # 3104 = sem resposta: placa de rede errada, ou câmera desligada
        return

    # 'data' é uma lista de números. bytes() a transforma num arquivo.
    caminho = "foto_frontal.jpg"
    with open(caminho, "wb") as f:
        f.write(bytes(data))

    print(f"Salvo em {caminho} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
```

Abra o `foto_frontal.jpg` com qualquer visualizador. É um JPEG normal.

!!! tip "O tamanho em bytes já diz muita coisa"
    Um JPEG válido da câmera do Go2 costuma ter dezenas ou centenas de
    kilobytes. Se `len(data)` vier com pouquíssimos bytes, alguma coisa está
    errada mesmo com `code == 0`.

---

## Exemplo 2 — ver ao vivo, com OpenCV

Este é o exemplo oficial (`example/go2/front_camera/camera_opencv.py`),
reescrito com comentários e com os problemas do original corrigidos.

```python
"""
Mostra a imagem da câmera frontal numa janela, ao vivo.
Pressione ESC para sair.

Requer tela gráfica e OpenCV:  pip install opencv-python numpy
Uso: python3 ao_vivo.py enp2s0
"""
import sys

import cv2      # biblioteca de visão: decodifica o JPEG e desenha a janela
import numpy as np

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.video.video_client import VideoClient

TECLA_ESC = 27


def bytes_para_imagem(data):
    """
    Converte os bytes do JPEG numa imagem que o OpenCV entende.

    Dois passos:
      1. frombuffer  — lê os bytes como uma sequência de números de 0 a 255.
      2. imdecode    — interpreta essa sequência como um JPEG e devolve a
                       matriz de pixels colorida.
    """
    buffer = np.frombuffer(bytes(data), dtype=np.uint8)
    return cv2.imdecode(buffer, cv2.IMREAD_COLOR)


def main():
    ChannelFactoryInitialize(0, sys.argv[1] if len(sys.argv) > 1 else None)

    client = VideoClient()
    client.SetTimeout(3.0)
    client.Init()

    print("Janela aberta. Pressione ESC para sair.")
    ultima_imagem = None

    try:
        while True:
            code, data = client.GetImageSample()

            if code != 0:
                print(f"Erro ao pedir imagem: code = {code}")
                break

            imagem = bytes_para_imagem(data)

            # imdecode devolve None se os bytes não formarem um JPEG válido
            # (acontece com pacote corrompido). Pular o quadro é melhor
            # que derrubar o programa.
            if imagem is None:
                print("Quadro corrompido, pulando.")
                continue

            ultima_imagem = imagem
            cv2.imshow("camera frontal do Go2", imagem)

            # waitKey é obrigatório: é ele que efetivamente desenha a janela
            # e captura o teclado. O 20 são milissegundos de espera.
            if cv2.waitKey(20) == TECLA_ESC:
                break

    except KeyboardInterrupt:
        print("\nInterrompido.")

    finally:
        # Salva o último quadro como lembrança, se houver algum.
        if ultima_imagem is not None:
            cv2.imwrite("ultimo_quadro.jpg", ultima_imagem)
            print("Último quadro salvo em ultimo_quadro.jpg")

        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
```

!!! note "O que foi corrigido em relação ao exemplo oficial"
    O `camera_opencv.py` original tem três pontos frágeis:

    1. **Pede a primeira imagem duas vezes** — uma antes do `while` e outra
       logo na primeira volta. A primeira é jogada fora.
    2. **Não testa se `imdecode` devolveu `None`.** Um quadro corrompido faz o
       `cv2.imshow` levantar exceção.
    3. **Usa `cv2.destroyWindow("front_camera")`** no fim, que falha se a janela
       nunca chegou a abrir. `destroyAllWindows()` é seguro em qualquer caso.

!!! warning "Precisa de ambiente gráfico"
    `cv2.imshow` abre uma janela. Se você estiver conectado por SSH sem
    encaminhamento de tela, isso falha. Nesse caso use o
    [Exemplo 1](#exemplo-1-tirar-uma-foto-e-salvar) ou o
    [Exemplo 3](#exemplo-3-sequencia-de-fotos-com-resiliencia), que só gravam
    arquivos.

---

## Exemplo 3 — sequência de fotos, com resiliência

Útil para registrar um experimento, montar um time-lapse ou coletar imagens
para treinar um modelo. Este exemplo mostra como **não desistir no primeiro
erro** — importante em coletas longas, onde uma falha isolada de rede é normal.

```python
"""
Tira N fotos em intervalos regulares e salva numa pasta.
Continua tentando se uma foto falhar.

Uso: python3 sequencia.py enp2s0 30 1.0
        (30 fotos, uma a cada 1 segundo)
"""
import os
import sys
import time
from datetime import datetime

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.video.video_client import VideoClient

PASTA = "capturas"
MAX_FALHAS_SEGUIDAS = 5   # desiste depois disto


def tirar_foto(client, caminho):
    """Devolve True se salvou, False se falhou."""
    code, data = client.GetImageSample()

    if code != 0:
        print(f"  falha: code = {code}")
        return False

    with open(caminho, "wb") as f:
        f.write(bytes(data))
    return True


def main():
    interface = sys.argv[1] if len(sys.argv) > 1 else None
    total = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    intervalo = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0

    ChannelFactoryInitialize(0, interface)

    client = VideoClient()
    client.SetTimeout(3.0)
    client.Init()

    os.makedirs(PASTA, exist_ok=True)

    salvas = 0
    falhas_seguidas = 0

    print(f"Capturando {total} fotos, uma a cada {intervalo}s...")

    try:
        for i in range(total):
            # Nome com data e hora: fácil de ordenar, nunca sobrescreve.
            carimbo = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            caminho = os.path.join(PASTA, f"go2_{carimbo}.jpg")

            print(f"[{i + 1}/{total}] {caminho}")

            if tirar_foto(client, caminho):
                salvas += 1
                falhas_seguidas = 0      # zera o contador: voltou a funcionar
            else:
                falhas_seguidas += 1
                if falhas_seguidas >= MAX_FALHAS_SEGUIDAS:
                    print(f"\n{MAX_FALHAS_SEGUIDAS} falhas seguidas. Desistindo.")
                    print("Confira o cabo de rede e se o robô está ligado.")
                    break

            time.sleep(intervalo)

    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário.")

    print(f"\nResultado: {salvas} fotos salvas em ./{PASTA}/")


if __name__ == "__main__":
    main()
```

!!! tip "Montando um vídeo depois"
    Com as fotos na pasta, o `ffmpeg` junta tudo:

    ```bash
    ffmpeg -framerate 10 -pattern_type glob -i 'capturas/*.jpg' \
           -c:v libx264 -pix_fmt yuv420p timelapse.mp4
    ```

---

## Resumo prático

```python
ChannelFactoryInitialize(0, "enp2s0")

client = VideoClient()
client.SetTimeout(3.0)
client.Init()

code, data = client.GetImageSample()

if code == 0:
    with open("foto.jpg", "wb") as f:
        f.write(bytes(data))    # data JÁ é um JPEG completo
```

| Lembrete | Por quê |
|---|---|
| Não é stream | Cada `GetImageSample()` é uma foto avulsa |
| `data` é JPEG pronto | Grave direto, sem processar |
| `bytes(data)` | O SDK devolve lista de inteiros, não `bytes` |
| Teste `code` antes | `data` é `None` quando dá erro |
| Serviço é `"videohub"` | Nome diferente da pasta — aparece em erros |

---

**Próximo:** [`obstacles_avoid` — desvio de obstáculos](04-obstacles-avoid.md) ·
[voltar ao índice](index.md)
