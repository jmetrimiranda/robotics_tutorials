# `robot_state` — serviços do robô

*O painel de disjuntores do Go2.*

| | |
|---|---|
| **Pasta** | `unitree_sdk2py/go2/robot_state/` |
| **Classe** | `RobotStateClient` |
| **Importação** | `from unitree_sdk2py.go2.robot_state.robot_state_client import RobotStateClient` |
| **Serviço no robô** | `"robot_state"` |
| **Versão** | `1.0.0.1` |
| **Tamanho** | 84 linhas |

---

## O que são "serviços", e por que você precisa mexer neles

Como visto na [Anatomia](01-anatomia-de-um-client.md#a-ideia-central-voce-manda-um-pedido-o-robo-responde),
dentro do Go2 rodam vários programinhas independentes — os **serviços**. Um
deles é o `sport_mode`: o que faz o robô se equilibrar, andar e não cair.

Esse serviço é o "motorista automático" do robô. Ele está **sempre mandando
comandos nos motores**, o tempo todo, para manter o equilíbrio.

Isso cria um problema:

```
  Seu programa de baixo nível        sport_mode
   "perna esquerda, 30°"    ──┐   ┌── "perna esquerda, 45°!"
                              ▼   ▼
                        ┌─────────────┐
                        │   MOTORES   │  ← recebem ordens contraditórias
                        └─────────────┘     e o robô treme, ou cai
```

**Se você quiser controlar os motores diretamente, precisa desligar o
`sport_mode` primeiro.** É exatamente para isso que este módulo existe.

!!! note "Quando você NÃO precisa deste módulo"
    Se você só usa [`sport`](02-sport.md), [`video`](03-video.md),
    [`vui`](05-vui.md) e [`obstacles_avoid`](04-obstacles-avoid.md), pode ignorar
    esta página inteira. O `robot_state` só é necessário para controle de baixo
    nível (comandar motor por motor) ou para diagnosticar o que está ligado
    dentro do robô.

---

## Os três comandos

| Método | Nº | O que faz |
|---|---|---|
| `ServiceList()` | 1003 | Lista todos os serviços e seus estados. |
| `ServiceSwitch(nome, ligar)` | 1001 | Liga ou desliga um serviço pelo nome. |
| `SetReportFreq(interval, duration)` | 1002 | Ajusta a frequência de relatórios. **Tem um defeito** ([veja](#o-defeito-do-setreportfreq)). |

---

## `ServiceList` — o inventário

Este método devolve uma lista de objetos `ServiceState`, uma classinha de três
campos definida logo acima do cliente:

```python
# robot_state_client.py:11
class ServiceState:
    def __init__(self, name: str = None, status: int = None, protect: bool = None):
        self.name = name        # o nome do serviço, ex.: "sport_mode"
        self.status = status    # um número (veja abaixo)
        self.protect = protect  # True = protegido, não pode ser desligado
```

E o método monta essa lista a partir da resposta do robô:

```python
# robot_state_client.py:32
def ServiceList(self):
    code, data = self._Call(ROBOT_STATE_API_ID_SERVICE_LIST, json.dumps({}))

    if code != 0:
        return code, None          # ◄── atenção: None, não lista vazia

    lst = []
    d = json.loads(data)           # a resposta é uma lista em formato texto
    for t in d:                    # para cada serviço na resposta...
        s = ServiceState()
        s.name = t["name"]
        s.status = t["status"]
        s.protect = t["protect"]
        lst.append(s)

    return code, lst
```

### O que significa `status`?

**Não está documentado.** O que dá para deduzir vem do `ServiceSwitch`, que
trata os valores assim:

```python
# robot_state_client.py:69
if status == 5:
    return ROBOT_STATE_ERR_SERVICE_PROTECTED    # 5202

if status != 0 and status != 1:
    return ROBOT_STATE_ERR_SERVICE_SWITCH       # 5201

return code   # ou seja: 0 e 1 são os únicos valores aceitos como sucesso
```

Traduzindo o que o código nos permite afirmar:

| `status` | Interpretação |
|---|---|
| 0 | Resultado válido (provavelmente: desligado) |
| 1 | Resultado válido (provavelmente: ligado) |
| 5 | Serviço protegido — recusou-se a mudar |
| outro | Falha genérica na operação |

!!! warning "O 'provavelmente' é honesto"
    O código não diz que 0 é desligado e 1 é ligado — só diz que ambos são
    aceitos como sucesso. A leitura de que 0/1 correspondem a desligado/ligado é
    a interpretação natural, mas não está escrita em lugar nenhum. Confirme
    empiricamente no seu robô antes de construir lógica em cima disso.

### O campo `protect`

Alguns serviços são essenciais para o robô funcionar e não podem ser
desligados pelo SDK. Esses vêm com `protect = True`, e tentar desligá-los
devolve `5202`. É uma proteção contra você derrubar o robô por acidente.

---

## Exemplo 1 — listar tudo que roda no robô

Não muda nada. É a radiografia do seu Go2, e o ponto de partida antes de
desligar qualquer coisa.

```python
"""
Lista todos os serviços do Go2 e seus estados.
Não altera nada — é só leitura.
Uso: python3 listar_servicos.py enp2s0
"""
import sys

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.robot_state.robot_state_client import RobotStateClient


def descrever_status(status):
    """Traduz o número em algo legível, com a ressalva de sempre."""
    return {
        0: "desligado (provável)",
        1: "ligado (provável)",
        5: "protegido",
    }.get(status, f"desconhecido ({status})")


def main():
    ChannelFactoryInitialize(0, sys.argv[1] if len(sys.argv) > 1 else None)

    client = RobotStateClient()
    client.SetTimeout(3.0)
    client.Init()

    code, servicos = client.ServiceList()

    if code != 0:
        print(f"Falha ao listar. code = {code}")
        return

    # Lembre: quando code != 0, 'servicos' é None. Já tratamos acima.
    print(f"\n{len(servicos)} serviços encontrados:\n")
    print(f"{'NOME':<28} {'STATUS':<24} {'PROTEGIDO'}")
    print("-" * 65)

    for s in servicos:
        protegido = "sim ← não dá para desligar" if s.protect else "não"
        print(f"{s.name:<28} {descrever_status(s.status):<24} {protegido}")

    # Destaca o que mais importa para quem vai fazer controle de baixo nível.
    print()
    for s in servicos:
        if "sport" in s.name.lower():
            print(f"O serviço de movimento é: '{s.name}'")
            print(f"  status: {descrever_status(s.status)}")
            print(f"  É este nome que você passa para ServiceSwitch().")


if __name__ == "__main__":
    main()
```

!!! tip "Rode isto antes de tudo"
    A lista exata de serviços **varia com a versão do firmware**. Não copie um
    nome de serviço de um tutorial da internet — rode este programa e use o nome
    que o *seu* robô devolveu.

---

## Exemplo 2 — desligar o `sport_mode` com segurança

O caso de uso principal do módulo. Este programa desliga o piloto automático,
espera, e religa — deixando o robô como encontrou.

```python
"""
Desliga o serviço de movimento (sport_mode), espera, e religa.

ATENÇÃO: com o sport_mode desligado, o robô NÃO se equilibra.
Ele precisa estar DEITADO no chão antes de você rodar isto.

Uso: python3 desliga_sport.py enp2s0
"""
import sys
import time

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.robot_state.robot_state_client import RobotStateClient


def achar_servico_de_movimento(client):
    """
    Procura o serviço de movimento pelo nome, em vez de assumir
    que ele se chama 'sport_mode'. Nomes mudam entre firmwares.
    """
    code, servicos = client.ServiceList()
    if code != 0:
        return None, code

    for s in servicos:
        if "sport" in s.name.lower():
            return s, 0

    return None, 0


def main():
    print("=" * 60)
    print("ATENÇÃO: este programa desliga o equilíbrio do robô.")
    print("O robô DEVE estar DEITADO no chão, em superfície plana.")
    print("Se ele estiver de pé, vai desabar.")
    print("=" * 60)

    resposta = input("Digite 'sim' para continuar: ")
    if resposta.strip().lower() != "sim":
        print("Cancelado.")
        return

    ChannelFactoryInitialize(0, sys.argv[1] if len(sys.argv) > 1 else None)

    client = RobotStateClient()
    client.SetTimeout(3.0)
    client.Init()

    # --- 1. Descobre o nome exato do serviço -------------------------
    servico, code = achar_servico_de_movimento(client)

    if code != 0:
        print(f"Não consegui listar os serviços. code = {code}")
        return

    if servico is None:
        print("Nenhum serviço com 'sport' no nome. Rode o Exemplo 1")
        print("para ver a lista completa do seu robô.")
        return

    print(f"\nServiço encontrado: '{servico.name}'")
    print(f"  status atual: {servico.status}")
    print(f"  protegido:    {servico.protect}")

    if servico.protect:
        print("\nEste serviço é protegido e não pode ser desligado pelo SDK.")
        print("Use o aplicativo do celular para desativá-lo.")
        return

    # --- 2. Desliga ---------------------------------------------------
    print(f"\nDesligando '{servico.name}'...")
    code = client.ServiceSwitch(servico.name, False)

    if code == 5202:
        print("  recusado: serviço protegido.")
        return
    if code == 5201:
        print("  falhou: o robô recusou a operação.")
        return
    if code != 0:
        print(f"  falhou. code = {code}")
        return

    print("  desligado. O robô agora está 'mole'.")
    print("  → É AQUI que você rodaria seu controle de baixo nível.")

    try:
        for i in range(5, 0, -1):
            print(f"  religando em {i}s...", end="\r")
            time.sleep(1)
        print()
    except KeyboardInterrupt:
        print("\n  interrompido — religando agora")

    finally:
        # --- 3. Religa — SEMPRE ---------------------------------------
        print(f"Religando '{servico.name}'...")
        code = client.ServiceSwitch(servico.name, True)
        if code == 0:
            print("  religado. O robô voltou ao normal.")
        else:
            print(f"  ATENÇÃO: falhou ao religar (code={code}).")
            print("  Reinicie o robô pelo aplicativo ou pelo botão.")


if __name__ == "__main__":
    main()
```

!!! danger "Não faça isto com o robô de pé"
    Com o `sport_mode` desligado, nada segura o robô. Um Go2 de pé desaba de
    cerca de 40 cm de altura, com 15 kg. Isso danifica os motores e pode
    machucar alguém. **Deite o robô primeiro** — com `StandDown()` e depois
    `Damp()`, pelo [módulo `sport`](02-sport.md), ou pelo controle remoto.

!!! tip "O `finally` é obrigatório aqui, não opcional"
    Se o seu programa morrer com o `sport_mode` desligado, o robô fica inerte
    até você religar manualmente ou reiniciá-lo. O `try/finally` acima garante
    que o serviço volta mesmo com `Ctrl+C`.

---

## Exemplo 3 — vigia de serviços

Fica olhando a lista de serviços e avisa quando algum muda de estado. Útil
durante experimentos longos: se o `sport_mode` cair sozinho (bateria baixa,
erro interno), você fica sabendo na hora em vez de descobrir pelo robô no chão.

```python
"""
Monitora os serviços do robô e avisa quando algum muda de estado.
Não altera nada.
Uso: python3 vigia.py enp2s0 [intervalo_segundos]
"""
import sys
import time
from datetime import datetime

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.robot_state.robot_state_client import RobotStateClient


def tirar_foto_do_estado(client):
    """
    Devolve um dicionário {nome: status} ou None se a leitura falhar.
    Chamo de 'foto' porque é o estado congelado num instante.
    """
    code, servicos = client.ServiceList()
    if code != 0:
        return None
    return {s.name: s.status for s in servicos}


def agora():
    return datetime.now().strftime("%H:%M:%S")


def main():
    interface = sys.argv[1] if len(sys.argv) > 1 else None
    intervalo = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0

    ChannelFactoryInitialize(0, interface)

    client = RobotStateClient()
    client.SetTimeout(3.0)
    client.Init()

    anterior = tirar_foto_do_estado(client)
    if anterior is None:
        print("Não consegui ler o estado inicial. Robô conectado?")
        return

    print(f"[{agora()}] Vigiando {len(anterior)} serviços "
          f"a cada {intervalo}s. Ctrl+C para sair.\n")
    for nome, status in sorted(anterior.items()):
        print(f"  {nome:<28} status={status}")
    print()

    falhas_de_leitura = 0

    try:
        while True:
            time.sleep(intervalo)
            atual = tirar_foto_do_estado(client)

            # Leitura falhou: pode ser oscilação de rede. Avisa mas insiste.
            if atual is None:
                falhas_de_leitura += 1
                print(f"[{agora()}] leitura falhou ({falhas_de_leitura}x)")
                continue

            if falhas_de_leitura:
                print(f"[{agora()}] comunicação restabelecida")
                falhas_de_leitura = 0

            # Compara a foto nova com a antiga, serviço por serviço.
            for nome, status in atual.items():
                if nome not in anterior:
                    print(f"[{agora()}] NOVO serviço: {nome} (status={status})")
                elif anterior[nome] != status:
                    print(f"[{agora()}] MUDOU: {nome} "
                          f"{anterior[nome]} → {status}")

            for nome in anterior:
                if nome not in atual:
                    print(f"[{agora()}] SUMIU: {nome}")

            anterior = atual

    except KeyboardInterrupt:
        print(f"\n[{agora()}] Vigia encerrado.")


if __name__ == "__main__":
    main()
```

---

## O defeito do `SetReportFreq`

Este método **não funciona como escrito**. É um defeito real no repositório:

```python
# robot_state_client.py:77
def SetReportFreq(self, interval: int, duration: int):
    p = {}
    p["interval"] = interval
    p["duration"] = duration
    parameter = json.dumps(p)       # ◄── converte para texto...

    code, data = self._Call(ROBOT_STATE_API_ID_REPORT_FREQ, p)
    #                                                       ▲
    #                                    ...e manda 'p', não 'parameter'!
    return code
```

A variável `parameter` é criada e **nunca usada**. O que vai para `_Call` é o
dicionário `p` cru, em vez do texto JSON que o robô espera.

**Todos os outros 51 métodos do módulo `go2/` passam `parameter`.** Este é o
único que passa `p`. É um erro de digitação, não uma escolha.

**O que acontece na prática:** o resto do encanamento espera um texto. Passar um
dicionário vai, na melhor das hipóteses, gerar uma mensagem malformada que o
robô rejeita (`3204`, parâmetro inválido) e, na pior, levantar uma exceção
dentro do SDK.

**Como contornar**, se você realmente precisar deste comando:

```python
import json
from unitree_sdk2py.go2.robot_state.robot_state_api import (
    ROBOT_STATE_API_ID_REPORT_FREQ,
)

def set_report_freq_corrigido(client, interval, duration):
    """Versão sem o bug: passa o texto JSON, como todos os outros métodos."""
    p = {"interval": interval, "duration": duration}
    parameter = json.dumps(p)                          # ← o texto
    code, data = client._Call(ROBOT_STATE_API_ID_REPORT_FREQ, parameter)
    return code

# uso:
code = set_report_freq_corrigido(client, 1000, 60)
```

!!! note "O que o método faria, se funcionasse"
    Ajustar a frequência com que o robô envia relatórios de estado —
    `interval` seria o espaçamento entre relatórios e `duration` por quanto
    tempo manter essa frequência. As unidades não são documentadas
    (provavelmente milissegundos e segundos). Como o método está quebrado, isso
    nunca foi exercitado por ninguém — o que explica o defeito ter sobrevivido.

---

## Resumo prático

```python
client = RobotStateClient()
client.SetTimeout(3.0)
client.Init()

# 1. Descubra os nomes reais no SEU robô
code, servicos = client.ServiceList()
for s in servicos:
    print(s.name, s.status, s.protect)

# 2. Desligue o piloto automático (COM O ROBÔ DEITADO!)
code = client.ServiceSwitch("sport_mode", False)
#  5202 = protegido, não dá
#  5201 = o robô recusou

# 3. Faça seu controle de baixo nível aqui

# 4. Religue — sempre, num finally
client.ServiceSwitch("sport_mode", True)
```

| Regra | Motivo |
|---|---|
| Deite o robô antes de desligar o `sport_mode` | Sem ele, o robô desaba |
| Religue num `finally` | Senão o robô fica inerte após um `Ctrl+C` |
| Descubra o nome com `ServiceList()` | Nomes variam entre firmwares |
| `servicos` é `None` quando `code != 0` | Teste o código antes de iterar |
| Não use `SetReportFreq` direto | Está quebrado; use a versão corrigida acima |

---

**Voltar ao [índice do SDK](index.md)** ·
**Voltar aos [links do Go2 EDU](../01-links.md)**
