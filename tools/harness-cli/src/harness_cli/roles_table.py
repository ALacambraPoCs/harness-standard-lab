"""Vista Markdown de standard/roles.yaml (fuente única de la estructura canónica)."""
from __future__ import annotations

from .standard import Standard

MARK_START = "<!-- generado:roles:inicio (harness roles --write) -->"
MARK_END = "<!-- generado:roles:fin -->"
SIMBOLO = {"obligatorio": "O", "condicional": "C", "recomendado": "R", "opcional": "P",
           "generado": "G", "prohibido-versionar": "X"}


def table(std: Standard) -> str:
    rows = ["| Rol | Ruta por defecto | Tipo | Oblig. | Nivel | Capa | Reubicable | Condición | Ficha |",
            "|---|---|---|---|---|---|---|---|---|"]
    for name, r in std.roles.items():
        ruta = r["ruta"] if not r.get("relativa_a") else f"{{{r['relativa_a']}}}/{r['ruta']}"
        alts = f" (alt.: {', '.join(a for a in r['alternativas'] if a != r['ruta'])})" if r.get("alternativas") else ""
        ficha = r["ficha"] if r["ficha"].startswith("pendiente:") else f"[ficha]({r['ficha'].replace('standard/', '')})"
        rows.append(f"| `{name}` | `{ruta}`{alts} | {r['tipo']} | {SIMBOLO[r['obligatoriedad']]} | {r['nivel_minimo']} | "
                    f"{r['capa']} | {'sí' if r['reubicable'] else 'no'} | {r.get('condicion', '—')} | {ficha} |")
    return "\n".join(rows)


def render_into(text: str, std: Standard) -> str:
    a, b = text.index(MARK_START), text.index(MARK_END)
    return text[: a + len(MARK_START)] + "\n" + table(std) + "\n" + text[b:]
