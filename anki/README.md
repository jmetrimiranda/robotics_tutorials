# Baralho de revisão de ROS 2

141 cartões em 11 subbaralhos. **92 deles pedem que você digite o comando** — o
Anki compara letra a letra com o gabarito e mostra o diff colorido.

## Importar

1. Anki → **Arquivo → Importar** → `ros2-revisao.apkg`
2. Os subbaralhos aparecem sob `ROS 2 — Revisão`.

Nada é sobrescrito: os IDs são estáveis, então você pode reimportar depois de
editar os cartões sem perder o histórico de revisão.

## Editar

Edite **`cartoes.yaml`**, nunca o `.apkg`:

```bash
python3 gerar_anki.py
```

Isso regenera duas coisas:

- `ros2-revisao.apkg` — reimporte no Anki, as edições são aplicadas por cima
- `99-flashcards.md` — a mesma coisa como página do mkdocs

## Os dois tipos de cartão

```yaml
- id: topic-009               # NÃO mude depois de importar
  deck: "02 - Nodes e Tópicos"
  tipo: cmd                   # caixa de digitação — resposta de UMA linha
  p: "Medir a taxa (Hz) de /turtle1/pose"
  r: "ros2 topic hz /turtle1/pose"
  n: "Retorna average rate, min, max, std dev."
```

```yaml
- id: py-001
  deck: "07 - rclpy: pub/sub e service/client"
  tipo: conceito              # pergunta/resposta, para blocos de código
  p: "Escreva de memória o main() padrão de um nó."
  r: |
    def main(args=None):
        rclpy.init(args=args)
        ...
  n: ""
```

O script aborta se você marcar como `cmd` uma resposta multilinha — a caixa de
digitação do Anki é de uma linha só.

## O que este baralho NÃO faz

Ele não te ensina a escrever um nó. Cartão de digitação é ótimo para comando e
péssimo para estrutura de 20 linhas.

Para os esqueletos (o `main()` de um nó, o corpo de um launch, o preenchimento
do `TransformStamped`), o drill certo é outro: arquivo vazio, escreve de
memória, e

```bash
diff -u _gabaritos/publisher.py /tmp/tentativa.py
```

Os cartões `conceito` que mostram código servem para você **reconhecer** que
esqueceu — o `diff` é que corrige de verdade.

## Rotina sugerida

- 15 min/dia com o baralho **inteiro**, todos os subbaralhos misturados.
  Intercalar assuntos retém mais que estudar um por vez, mesmo parecendo pior.
- 1 esqueleto por dia no `diff`.
- 1 exercício da página correspondente do mkdocs.
