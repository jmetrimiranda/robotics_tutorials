#!/usr/bin/env python3
"""
Gera o baralho Anki de revisão de ROS 2 a partir de cartoes.yaml.

    pip install genanki pyyaml
    python3 gerar_anki.py

Saídas:
    ros2-revisao.apkg          -> importe no Anki (Arquivo > Importar)
    99-flashcards.md           -> a mesma coisa como página do mkdocs

Dois tipos de cartão:
    tipo: cmd      -> caixa de digitação ({{type:}} do Anki). Você digita o
                      comando e o Anki mostra um diff colorido com o gabarito.
                      Só use para respostas de UMA linha.
    tipo: conceito -> pergunta/resposta normal, para blocos de código e teoria.

IMPORTANTE: os ids em cartoes.yaml viram o GUID do cartão. Editar a pergunta
ou a resposta preserva o histórico de revisão; mudar o id cria um cartão novo.
"""

import hashlib
import html
import pathlib
import sys

try:
    import genanki
    import yaml
except ImportError:
    sys.exit("Faltam dependências: pip install genanki pyyaml")

AQUI = pathlib.Path(__file__).parent
ENTRADA = AQUI / "cartoes.yaml"
SAIDA_APKG = AQUI / "ros2-revisao.apkg"
SAIDA_MD = AQUI / "99-flashcards.md"
BARALHO_RAIZ = "ROS 2 — Revisão"


# ---------------------------------------------------------------- utilidades
def id_estavel(texto: str, piso: int = 1 << 30) -> int:
    """ID determinístico: rodar o script de novo não duplica nada no Anki."""
    h = hashlib.sha256(texto.encode()).hexdigest()
    return piso + int(h[:8], 16) % (1 << 30)


def esc(texto: str) -> str:
    """Escapa para HTML e preserva a formatação de bloco de código."""
    seguro = html.escape(texto.rstrip(), quote=False)
    if "\n" in seguro:
        return f'<pre class="codigo">{seguro}</pre>'
    return f'<code class="inline">{seguro}</code>'


def esc_digitado(texto: str) -> str:
    """
    Campo comparado pelo {{type:}}: escapa só o mínimo, para o diff do Anki
    bater caractere a caractere com o que você digitou.
    """
    return texto.strip().replace("&", "&amp;").replace("<", "&lt;")


CSS = """
.card {
  font-family: -apple-system, "Segoe UI", Roboto, sans-serif;
  font-size: 19px;
  text-align: left;
  color: #1a1a1a;
  background: #fafafa;
  padding: 18px 22px;
  line-height: 1.55;
}
.pergunta { font-size: 20px; margin-bottom: 14px; }
.dica {
  font-size: 13px; color: #6e6e6e; text-transform: uppercase;
  letter-spacing: .08em; margin-bottom: 6px;
}
code.inline, pre.codigo {
  font-family: "JetBrains Mono", "DejaVu Sans Mono", monospace;
  background: #f0f0f0; border: 1px solid #d8d8d8; border-radius: 4px;
  color: #1a1a1a;
}
code.inline { padding: 3px 7px; font-size: 17px; }
pre.codigo {
  display: block; padding: 12px 14px; font-size: 15px;
  white-space: pre; overflow-x: auto; margin: 10px 0;
}
hr#answer { border: none; border-top: 2px solid #1a1a1a; margin: 18px 0; }
.notas {
  font-size: 15px; color: #4a4a4a; margin-top: 14px;
  border-left: 3px solid #c8c8c8; padding-left: 12px;
}
input#typeans {
  font-family: "JetBrains Mono", "DejaVu Sans Mono", monospace;
  font-size: 17px; width: 100%; padding: 8px 10px;
  border: 2px solid #1a1a1a; border-radius: 4px;
  background: #fff; color: #1a1a1a; caret-color: #1a1a1a;
  box-sizing: border-box;
}
.typeGood { background: #b8e6b8; color: #1a1a1a; }
.typeBad  { background: #f0b8b8; color: #1a1a1a; }
.typeMissed { background: #ffe9a8; color: #1a1a1a; }
.nightMode .card { color: #e8e8e8; background: #232323; }
.nightMode code.inline, .nightMode pre.codigo {
  background: #2e2e2e; border-color: #454545; color: #e8e8e8;
}
.nightMode input#typeans {
  background: #1e1e1e; color: #e8e8e8; caret-color: #e8e8e8;
  border-color: #8a8a8a;
}
.nightMode .dica { color: #9a9a9a; }
.nightMode .notas { color: #b5b5b5; border-left-color: #555; }
.nightMode hr#answer { border-top-color: #888; }
"""

# ------------------------------------------------------------------- modelos
MODELO_CMD = genanki.Model(
    id_estavel("ros2::modelo::comando"),
    "ROS 2 — Comando (digitar)",
    fields=[{"name": "Pergunta"}, {"name": "Comando"}, {"name": "Notas"}],
    templates=[
        {
            "name": "Digitar o comando",
            # {{type:Comando}} na FRENTE gera a caixa de input...
            "qfmt": (
                '<div class="dica">digite o comando</div>'
                '<div class="pergunta">{{Pergunta}}</div>'
                "{{type:Comando}}"
            ),
            # ...e no VERSO vira o diff colorido do que você digitou.
            "afmt": (
                '<div class="pergunta">{{Pergunta}}</div>'
                '<hr id="answer">'
                "{{type:Comando}}"
                '{{#Notas}}<div class="notas">{{Notas}}</div>{{/Notas}}'
            ),
        }
    ],
    css=CSS,
)

MODELO_CONCEITO = genanki.Model(
    id_estavel("ros2::modelo::conceito"),
    "ROS 2 — Conceito",
    fields=[{"name": "Pergunta"}, {"name": "Resposta"}, {"name": "Notas"}],
    templates=[
        {
            "name": "Conceito",
            "qfmt": '<div class="pergunta">{{Pergunta}}</div>',
            "afmt": (
                '<div class="pergunta">{{Pergunta}}</div>'
                '<hr id="answer">'
                "{{Resposta}}"
                '{{#Notas}}<div class="notas">{{Notas}}</div>{{/Notas}}'
            ),
        }
    ],
    css=CSS,
)


# ---------------------------------------------------------------------- main
def main() -> None:
    dados = yaml.safe_load(ENTRADA.read_text(encoding="utf-8"))
    cartoes = dados["cartoes"]

    baralhos: dict[str, genanki.Deck] = {}
    vistos: set[str] = set()
    contagem = {"cmd": 0, "conceito": 0}

    for c in cartoes:
        cid = c["id"]
        if cid in vistos:
            sys.exit(f"ERRO: id duplicado em cartoes.yaml -> {cid}")
        vistos.add(cid)

        nome_baralho = f"{BARALHO_RAIZ}::{c['deck']}"
        if nome_baralho not in baralhos:
            baralhos[nome_baralho] = genanki.Deck(
                id_estavel(f"ros2::deck::{nome_baralho}"), nome_baralho
            )

        pergunta = html.escape(c["p"].strip(), quote=False)
        notas = html.escape((c.get("n") or "").strip(), quote=False)
        tag = c["deck"].split(" - ", 1)[-1].lower().replace(" ", "-").replace(",", "")

        if c["tipo"] == "cmd":
            resposta = c["r"]
            if "\n" in resposta.strip():
                sys.exit(f"ERRO: cartão 'cmd' com resposta multilinha -> {cid}\n"
                         "       A caixa de digitação do Anki é de uma linha só.\n"
                         "       Troque para 'tipo: conceito'.")
            nota = genanki.Note(
                model=MODELO_CMD,
                fields=[pergunta, esc_digitado(resposta), notas],
                guid=genanki.guid_for(cid),
                tags=["ros2", tag, "digitar"],
            )
            contagem["cmd"] += 1
        else:
            nota = genanki.Note(
                model=MODELO_CONCEITO,
                fields=[pergunta, esc(c["r"]), notas],
                guid=genanki.guid_for(cid),
                tags=["ros2", tag],
            )
            contagem["conceito"] += 1

        baralhos[nome_baralho].add_note(nota)

    genanki.Package(list(baralhos.values())).write_to_file(SAIDA_APKG)

    # ------------------------------------------------ versão mkdocs (opcional)
    linhas = [
        "# Flashcards",
        "",
        "*Gerado automaticamente a partir de `anki/cartoes.yaml` — não edite à mão.*",
        "",
        "Tente responder **antes** de abrir. Para revisar com repetição espaçada,",
        "importe o `ros2-revisao.apkg` no Anki.",
        "",
    ]
    baralho_atual = None
    for c in cartoes:
        if c["deck"] != baralho_atual:
            baralho_atual = c["deck"]
            linhas += ["", f"## {baralho_atual}", ""]
        marca = " :material-keyboard:" if c["tipo"] == "cmd" else ""
        linhas.append(f'??? question "{c["p"].strip()}{marca}"')
        corpo = c["r"].rstrip()
        linguagem = "bash" if c["tipo"] == "cmd" else ""
        linhas.append(f"    ```{linguagem}")
        linhas += [f"    {ln}" for ln in corpo.split("\n")]
        linhas.append("    ```")
        if (c.get("n") or "").strip():
            linhas += ["", f"    {c['n'].strip()}"]
        linhas.append("")
    SAIDA_MD.write_text("\n".join(linhas) + "\n", encoding="utf-8")

    print(f"OK  {SAIDA_APKG.name}")
    print(f"    {len(cartoes)} cartões em {len(baralhos)} subbaralhos")
    print(f"    {contagem['cmd']} para digitar / {contagem['conceito']} de conceito")
    print(f"OK  {SAIDA_MD.name}")


if __name__ == "__main__":
    main()
