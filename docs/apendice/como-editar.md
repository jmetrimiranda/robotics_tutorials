# Apêndice — Como editar este livro

Manual de sobrevivência. Se você só ler uma seção, leia a **Regra de Ouro**.

## A Regra de Ouro

O livro inteiro é feito de **duas coisas**:

1. A pasta `docs/` — o **conteúdo** (arquivos `.md`, um por página);
2. O arquivo `mkdocs.yml` — o **índice** (a seção `nav:` diz o que existe e em que ordem).

Toda tarefa de edição se resume a: **mexer num `.md`** e, se a página for nova,
**adicionar 1 linha no `nav:`**. Só isso. Capítulo e subcapítulo não são
"coisas" especiais — são apenas **indentação** dentro do `nav:`.

---

## Parte A — Criando um livro destes do zero

(Foi assim que este repositório nasceu. Guarde para quando quiser criar outro.)

```bash
# 1. Pasta do projeto + ambiente Python isolado
mkdir meu_livro && cd meu_livro
python3 -m venv .venv
source .venv/bin/activate

# 2. Instalar o gerador
pip install mkdocs-material

# 3. Criar o mínimo: um índice e uma página
mkdir docs
printf '# Meu Livro\n\nOlá!\n' > docs/index.md
printf 'site_name: Meu Livro\ntheme:\n  name: material\n' > mkdocs.yml

# 4. Ver funcionando
mkdocs serve      # abra http://127.0.0.1:8000
```

A partir daí, todo o resto (fórmulas, capítulos, publicação) é acrescentar
linhas no `mkdocs.yml` — compare com o `mkdocs.yml` deste repositório para ver
o que cada bloco adiciona.

---

## Parte B — As receitas do dia a dia

### Receita 1 — Editar uma página que já existe
Abra o `.md`, edite, salve (`Ctrl+S`). Com `mkdocs serve` rodando, o navegador
recarrega sozinho. Nada mais a fazer.

### Receita 2 — Nova página dentro de um subcapítulo
Exemplo: uma página "Event Handlers" dentro de ROS 2.

1. Crie o arquivo: `docs/03-robotica-aplicada/01-ros2/04-event-handlers.md`
2. No `mkdocs.yml`, dentro do bloco de ROS 2, adicione a linha:
```yaml
      - ROS 2:
          - Visão geral: 03-robotica-aplicada/01-ros2/index.md
          - CLI Tools: 03-robotica-aplicada/01-ros2/01-cli-tools.md
          - Event Handlers: 03-robotica-aplicada/01-ros2/04-event-handlers.md   # <- nova
```

### Receita 3 — Novo subcapítulo
Exemplo: "Controle" dentro de Fundamentos.

1. Crie a pasta e a página de abertura:
   `docs/02-fundamentos/06-controle/index.md`
2. No `nav:`, dentro de Fundamentos:
```yaml
  - Fundamentos:
      - Visão geral: 02-fundamentos/index.md
      - Controle: 02-fundamentos/06-controle/index.md    # <- novo
```
Quando o subcapítulo crescer, ele vira um bloco indentado com várias páginas
(como o ROS 2 é hoje).

### Receita 4 — Novo capítulo
Exemplo: "Hardware".

1. Crie `docs/04-hardware/index.md`
2. Bloco novo no `nav:`, no nível de cima:
```yaml
  - Hardware:
      - Visão geral: 04-hardware/index.md
```

### Receita 5 — Publicar na internet
```bash
git add .
git commit -m "novo conteudo"
git push
```
O GitHub Actions (arquivo `.github/workflows/publicar.yml`) compila e publica
sozinho. Configuração única, na primeira vez: no GitHub, **Settings → Pages →
Branch: `gh-pages`**.

---

## Parte C — Erros comuns (e o que significam)

| Sintoma | Causa | Conserto |
|---|---|---|
| `Config file 'mkdocs.yml' does not exist` | Você não está na pasta raiz do livro | `cd` para a pasta que contém o `mkdocs.yml` |
| Aviso: *"pages exist in docs but are not included in nav"* | Criou o `.md` e esqueceu a linha no `nav:` | Receita 2 |
| Erro de YAML ao servir | Indentação errada no `mkdocs.yml` | Use **espaços** (nunca TAB) e mantenha o alinhamento dos blocos |
| Página abre em 404 | Caminho no `nav:` não bate com o arquivo real | Confira o caminho letra a letra |
| `pip`/`mkdocs`: comando não encontrado | Esqueceu de ativar o ambiente | `source .venv/bin/activate` |

---

## Parte D — Convenções deste livro

- **Prefixos numéricos** (`01-`, `02-`...) nas pastas servem só para ordenar no
  seu editor de arquivos; o título que o leitor vê é o do `nav:`.
- **Capítulo/subcapítulo** = pasta com um `index.md` de abertura;
  **página** = um `.md` dentro dela.
- Fórmulas, código, caixas e diagramas: veja o
  [Guia de formatos](guia-de-formatos.md), que é a folha de exemplos viva.
- O `.venv/` e o `site/` **nunca** vão para o Git (já estão no `.gitignore`).
