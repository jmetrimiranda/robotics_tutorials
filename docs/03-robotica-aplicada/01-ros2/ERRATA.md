# Errata do cheat sheet original

Tudo isto foi corrigido nas páginas do mkdocs e no baralho do Anki. A lista
existe para você não reintroduzir os erros ao copiar do LaTeX.

## Comandos que não funcionam

| Onde | Está | Deveria ser |
|---|---|---|
| turtlesim | `ros2 pkg executables tutrtlesim` | `turtlesim` |
| turtlesim | `ros2 run trutlesim turtlesim_node` *(3 ocorrências)* | `turtlesim` |
| rqt | `sudo apt install ]nros-foxy-rqt*` | `~nros-foxy-rqt*` — o `~n` é um padrão do apt |
| Tópicos | `geometry_msg/msg/Twist` *(várias)* | `geometry_msgs` — com **s** |
| Serviços | `ros2 interface show <type_name>.src` | `.srv`; no Foxy, sem extensão nenhuma |
| Serviços | `ros2 service call spawn ...` | `/spawn` — com barra |
| Interfaces | `colcon build --package-selected tutorial_interfaces` | `--packages-select` |
| Pacotes | `colcon build --package-up-to hello_world` | `--packages-up-to` |

As duas últimas são a mesma armadilha: o argumento é **plural** (`--packages-`)
e o verbo é `select`, não `selected`.

## Código com bug

**Fibonacci — `execute_callback`**

```python
seq.append(seq[i] + seq[i-i])   # i-i é sempre 0 -> gera 0,1,1,1,1,...
seq.append(seq[i] + seq[i-1])   # correto
```

No mesmo bloco, `goal_handle.succeed()` aparece duas vezes — e a segunda está
escrita `succed()`, que levanta `AttributeError`.

**`MinimalParam` — indentação**

```python
class MinimalParam(rclpy.node.Node):
    ...
    def main():          # indentado DENTRO da classe
```

`main` é função de módulo. Indentado assim, o entry point do `setup.py` não
encontra nada.

**Pseudo-classe da action**

```python
class Result():
    self.sequece        # -> sequence
class Feedback();       # -> Feedback:
```

## Saídas de terminal transcritas errado

| Está | É |
|---|---|
| `Interger value is: 86` | `Integer value is: 86` |
| `Set parameter sucessfull` | `Set parameter successful` |

## Afirmações a revisar

- **"Goal pode ser intercambiado pela palavra Result"** — não pode. Goal é o
  pedido que o cliente manda; Result é o que o servidor devolve no fim. São
  blocos distintos do `.action`.

- **`use_provided_red`** é declarado no exemplo de substituições e nunca usado.
  No tutorial original ele controla um `IfCondition`/`UnlessCondition` que
  decide se a cor fornecida vale. Do jeito que ficou, o argumento não faz nada.

- **`MinimalParam` reescreve o próprio parâmetro** a cada segundo com
  `'world'`. É proposital no tutorial, mas faz o `ros2 param set` parecer
  quebrado. Vale um comentário no texto — virou o Exercício 5 da página de
  [Publisher/Subscriber e Serviços](03-pub-sub-e-servicos.md).

## Problemas de build do LaTeX

- `\includegraphics{images/node_gráfico.png}` numa caixa e
  `images/node_grafico.png` em outra: o mesmo arquivo com e sem acento. Uma das
  duas vai falhar.
- Imagens referenciadas com e sem o prefixo `images/`
  (`ros_graph.png`, `services_ros.png`, `actions.png` vs
  `images/node_grafico.png`).
- `\usepackage{hyperref}` e `\usepackage{tikz}` carregados duas vezes.
- Título de caixa: "publihser" → "publisher".
