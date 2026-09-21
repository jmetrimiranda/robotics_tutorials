# `vui` — luz e som

*O módulo mais simples, e o melhor lugar para começar.*

| | |
|---|---|
| **Pasta** | `unitree_sdk2py/go2/vui/` |
| **Classe** | `VuiClient` |
| **Importação** | `from unitree_sdk2py.go2.vui.vui_client import VuiClient` |
| **Serviço no robô** | `"vui"` |
| **Versão** | `1.0.0.1` |
| **Tamanho** | 85 linhas |

"VUI" quer dizer *Voice User Interface* — interface de voz e luz. Na prática,
este módulo controla duas coisas: **o brilho do led da frente** e **o volume do
alto-falante**.

---

## Por que começar por aqui

Este é o único dos cinco módulos que **não move o robô**. Isso o torna a
ferramenta perfeita para:

1. **Testar a conexão.** Se `GetBrightness()` devolve `code = 0`, sua rede, sua
   interface e seu `Init()` estão corretos. Todo o resto do SDK vai funcionar.
2. **Aprender o padrão do SDK** sem risco de quebrar nada.
3. **Dar retorno visual** ao seu programa — o robô pisca quando termina uma
   tarefa, acende no máximo quando dá erro, e assim por diante.

!!! tip "Faça deste o seu primeiro teste, sempre"
    Antes de depurar um `SportClient` que não responde, rode um `GetBrightness`.
    Ele separa "problema de rede" de "problema no serviço de movimento" em cinco
    segundos.

---

## Os seis comandos

Três pares de "ajuste" e "pergunte":

| Método | Nº | O que faz | Devolve |
|---|---|---|---|
| `SetBrightness(level)` | 1005 | Ajusta o brilho do led. | `code` |
| `GetBrightness()` | 1006 | Pergunta o brilho atual. | `(code, nível)` |
| `SetVolume(level)` | 1003 | Ajusta o volume. | `code` |
| `GetVolume()` | 1004 | Pergunta o volume atual. | `(code, nível)` |
| `SetSwitch(enable)` | 1001 | Liga/desliga a interface. | `code` |
| `GetSwitch()` | 1002 | Pergunta se está ligada. | `(code, valor)` |

### A faixa de valores

**Não está documentada.** O que sabemos vem do exemplo oficial
(`example/vui_client/vui_client_example.py`), que percorre `range(1, 11)` e
depois define `0`:

```python
for i in range(1, 11):        # 1, 2, 3, ..., 10
    client.SetBrightness(i)
# ...
client.SetBrightness(0)       # apagado
```

Ou seja: a faixa prática é **0 a 10**, onde `0` é apagado/mudo e `10` é o
máximo. Trate isso como observação empírica, não como especificação.

!!! warning "`SetSwitch` faz o quê, exatamente?"
    O código só diz que envia `{"enable": true/false}` para o comando 1001.
    Nenhum comentário, nenhum exemplo oficial, nenhuma linha do `README.md`
    explica o que esse interruptor controla — se é a interface de voz inteira,
    se são os sons de sistema, ou outra coisa.

    O exemplo oficial do `vui` **não usa** `SetSwitch`. Por prudência, prefira
    `SetVolume(0)` para silenciar e `SetBrightness(0)` para apagar; esses dois
    têm efeito conhecido e reversível.

---

## Como o par Set/Get funciona por dentro

Vale ver os dois lado a lado, porque ilustra o padrão de todo o SDK.

**O `Set` é direto** — monta, envia, devolve o código:

```python
# vui_client.py:46
# 1003
def SetVolume(self, level: int):
    p = {}
    p["volume"] = level             # o campo se chama "volume"
    parameter = json.dumps(p)       # vira: '{"volume": 5}'

    code, data = self._Call(VUI_API_ID_SETVOLUME, parameter)
    return code                     # ignora o data, devolve só o código
```

**O `Get` precisa desempacotar** a resposta:

```python
# vui_client.py:54
# 1006        ◄── este comentário está ERRADO. GetVolume é 1004.
def GetVolume(self):
    p = {}
    parameter = json.dumps(p)       # envia '{}' — não há o que perguntar

    code, data = self._Call(VUI_API_ID_GETVOLUME, parameter)
    if code == 0:
        d = json.loads(data)        # a resposta vem como texto: '{"volume": 5}'
        return code, d["volume"]    # devolve o número de dentro
    else:
        return code, None           # deu erro: None no lugar do valor
```

**A consequência prática** desse `else` é que você precisa testar o `code`:

```python
code, volume = client.GetVolume()

# ERRADO — se deu erro, volume é None e isto quebra:
print(f"Volume: {volume + 1}")      # TypeError

# CERTO:
if code == 0:
    print(f"Volume: {volume}")
else:
    print(f"Não consegui ler o volume. code = {code}")
```

---

## Exemplo 1 — diagnóstico de conexão

Um programa que responde à pergunta "meu computador consegue falar com o robô?"
sem mover nada. Guarde este arquivo; você vai usá-lo muito.

```python
"""
Diagnóstico de conexão com o Go2. Não move o robô.
Uso: python3 diagnostico.py enp2s0
"""
import sys

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.vui.vui_client import VuiClient

ERROS = {
    3102: "falha ao enviar — rede caiu ou interface errada",
    3103: "faltou chamar Init() — bug no seu código",
    3104: "tempo esgotado — robô não respondeu",
    3203: "comando não existe nesta versão do firmware",
    3204: "parâmetro inválido",
}


def explicar(code):
    return ERROS.get(code, f"erro desconhecido ({code})")


def main():
    interface = sys.argv[1] if len(sys.argv) > 1 else None

    print("=" * 55)
    print("DIAGNÓSTICO DE CONEXÃO — Unitree Go2")
    print("=" * 55)
    print(f"Interface de rede: {interface or '(padrão — rodando no robô?)'}")

    # --- Etapa 1: abrir a comunicação --------------------------------
    print("\n[1/4] Abrindo comunicação...")
    try:
        ChannelFactoryInitialize(0, interface)
        print("      ok")
    except Exception as e:
        print(f"      FALHOU: {e}")
        print("      Confira o nome da interface com: ip addr")
        return

    # --- Etapa 2: criar e inicializar o cliente ----------------------
    print("[2/4] Criando cliente VUI...")
    client = VuiClient()
    client.SetTimeout(3.0)
    client.Init()
    print("      ok")

    # --- Etapa 3: o serviço responde? --------------------------------
    print("[3/4] Perguntando a versão do serviço no robô...")
    code, versao = client.GetServerApiVersion()
    if code != 0:
        print(f"      FALHOU: {explicar(code)}")
        print("\n      Checklist:")
        print("      - o robô está ligado e de pé/deitado (não em standby)?")
        print("      - o cabo de rede está conectado?")
        print("      - seu IP está em 192.168.123.x?")
        print("      - o nome da interface está certo?")
        return
    print(f"      ok — o robô roda a versão {versao}")

    # --- Etapa 4: ler um valor de verdade ----------------------------
    print("[4/4] Lendo brilho e volume atuais...")

    code_b, brilho = client.GetBrightness()
    code_v, volume = client.GetVolume()

    if code_b == 0:
        print(f"      brilho do led: {brilho}")
    else:
        print(f"      brilho: {explicar(code_b)}")

    if code_v == 0:
        print(f"      volume:        {volume}")
    else:
        print(f"      volume: {explicar(code_v)}")

    print("\n" + "=" * 55)
    if code_b == 0 and code_v == 0:
        print("TUDO CERTO. Você pode usar os outros módulos do SDK.")
    else:
        print("Comunicação parcial. Veja os erros acima.")
    print("=" * 55)


if __name__ == "__main__":
    main()
```

---

## Exemplo 2 — o led como sinalizador do seu programa

Uso prático e elegante: transformar o led numa barra de status. Quando o robô
está andando sozinho e você está a dez metros dele, ver a luz mudar é mais útil
que ler o terminal.

```python
"""
Usa o led do Go2 para sinalizar o andamento de uma tarefa.
Padrões de piscada diferentes para cada situação.
Uso: python3 sinalizador.py enp2s0
"""
import sys
import time

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.vui.vui_client import VuiClient

BRILHO_MAX = 10
BRILHO_MIN = 0


class Sinalizador:
    """
    Envolve o VuiClient num vocabulário de sinais visuais.

    A ideia: em vez de espalhar SetBrightness pelo código, você
    escreve sinal.trabalhando() e sinal.erro(), que se explicam sozinhos.
    """

    def __init__(self, client):
        self.client = client

    def _piscar(self, vezes, aceso_s, apagado_s):
        """Bloco básico: acende e apaga N vezes com a cadência dada."""
        for _ in range(vezes):
            self.client.SetBrightness(BRILHO_MAX)
            time.sleep(aceso_s)
            self.client.SetBrightness(BRILHO_MIN)
            time.sleep(apagado_s)

    def pronto(self):
        """Uma piscada longa: o programa iniciou."""
        print("[sinal] pronto")
        self._piscar(1, 1.0, 0.3)

    def trabalhando(self, segundos):
        """Pulsação lenta e contínua enquanto a tarefa roda."""
        print(f"[sinal] trabalhando por {segundos}s")
        fim = time.time() + segundos
        while time.time() < fim:
            # Sobe o brilho gradualmente e desce: efeito de "respiração".
            for nivel in list(range(0, 11)) + list(range(9, 0, -1)):
                if time.time() >= fim:
                    break
                self.client.SetBrightness(nivel)
                time.sleep(0.08)

    def sucesso(self):
        """Três piscadas rápidas: deu tudo certo."""
        print("[sinal] sucesso")
        self._piscar(3, 0.15, 0.15)
        self.client.SetBrightness(BRILHO_MIN)

    def erro(self):
        """Piscadas rápidas e insistentes: alguma coisa falhou."""
        print("[sinal] ERRO")
        self._piscar(8, 0.08, 0.08)
        self.client.SetBrightness(BRILHO_MAX)   # fica aceso, chamando atenção


def tarefa_simulada():
    """Coloque aqui o trabalho de verdade. Devolve True se deu certo."""
    time.sleep(0.1)
    return True


def main():
    ChannelFactoryInitialize(0, sys.argv[1] if len(sys.argv) > 1 else None)

    client = VuiClient()
    client.SetTimeout(3.0)
    client.Init()

    # Confere a conexão antes de depender do led para comunicar qualquer coisa.
    code, _ = client.GetBrightness()
    if code != 0:
        print(f"Sem conexão com o robô (code={code}). Abortando.")
        return

    # Guarda o brilho original para restaurar no fim — boa educação.
    _, brilho_original = client.GetBrightness()

    sinal = Sinalizador(client)

    try:
        sinal.pronto()
        time.sleep(0.5)

        sinal.trabalhando(6)

        if tarefa_simulada():
            sinal.sucesso()
        else:
            sinal.erro()

    except KeyboardInterrupt:
        sinal.erro()

    finally:
        time.sleep(1)
        # Devolve o robô ao estado em que estava.
        client.SetBrightness(brilho_original if brilho_original is not None else 5)
        print("Brilho restaurado.")


if __name__ == "__main__":
    main()
```

!!! tip "Restaurar o estado original é uma boa prática geral"
    Ler o valor antes de mexer e devolvê-lo no `finally` vale para todo o SDK,
    não só para o led. O próximo programa (ou a próxima pessoa) não espera
    encontrar o robô com o volume no zero porque o seu script morreu no meio.

---

## Os erros de copiar e colar

O `vui_client.py` é o arquivo que mais mostra que o módulo `go2/` foi feito
duplicando arquivos sem revisar. Três achados:

### 1. A faixa diz `VideoClient`

```python
"""
" class VideoClient      ◄── mas a classe abaixo é VuiClient
"""
class VuiClient(Client):
```

O arquivo foi copiado do `video_client.py` e o comentário ficou.

### 2. Um comentário de número errado

```python
    # 1006                     ◄── errado
    def GetVolume(self):
        code, data = self._Call(VUI_API_ID_GETVOLUME, parameter)
```

Conferindo o `vui_api.py`:

```python
VUI_API_ID_GETVOLUME = 1004       # ◄── é 1004, não 1006
VUI_API_ID_GETBRIGHTNESS = 1006   # ◄── 1006 é este aqui
```

O comentário `# 1006` aparece acima de **dois** métodos diferentes no mesmo
arquivo.

### 3. `SetBrightness` e `GetBrightness` estão fora de ordem

Os métodos aparecem na ordem 1001, 1002, 1003, 1006, 1005, 1006 — porque foram
copiados e reordenados sem ajustar os comentários.

!!! note "Isso importa?"
    O **código funciona** — ele usa as constantes (`VUI_API_ID_GETVOLUME`), não
    os comentários. Mas importa como aviso: **não confie nos comentários deste
    repositório.** Confira sempre contra o arquivo `*_api.py`, que é a fonte
    de verdade.

---

## Resumo prático

```python
ChannelFactoryInitialize(0, "enp2s0")

client = VuiClient()
client.SetTimeout(3.0)
client.Init()

# Perguntar (sempre teste o code antes de usar o valor!)
code, brilho = client.GetBrightness()
code, volume = client.GetVolume()

# Ajustar (0 = desligado, 10 = máximo)
client.SetBrightness(0)    # apaga
client.SetVolume(5)        # meio volume
```

| Uso | Por quê |
|---|---|
| Primeiro teste de conexão | Não move o robô, resposta imediata |
| Sinalizador visual | Você vê o estado do programa de longe |
| Evite `SetSwitch` | Ninguém documentou o que ele desliga |

---

**Próximo:** [`robot_state` — serviços do robô](06-robot-state.md) ·
[voltar ao índice](index.md)
