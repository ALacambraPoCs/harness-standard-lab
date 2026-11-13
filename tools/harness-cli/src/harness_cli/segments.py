"""Mapa de segmentos (ADR-014 rev. 2, D-083; F4.2).

- `propose`: analiza el repositorio (inventario, cambio en git, imports de Python, CODEOWNERS) y propone un
  borrador. **No escribe nada**: una persona lo ajusta y lo versiona (2a).
- `graph`: dependencias reales entre los segmentos de un mapa, clasificadas como declaradas, deuda o no
  declaradas (2c). La regla que las convierte en errores es `segments check` (F4.3).

Solo Python se analiza (AST, sin ejecutar nada). Para el resto de lenguajes, las dependencias se declaran
«no verificadas» (2e).
"""
from __future__ import annotations

import ast
import collections
import datetime as dt
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .matchers import SKIP_DIRS, compile_pattern, owners_for, parse_codeowners

RUTA_MAPA = ".harness/segments.yaml"
EXCLUIR_SUGERIDO = {"docs", "doc", "examples", "example", "assets", "images", "img"}
LENGUAJES = {".py": "python", ".ts": "typescript", ".tsx": "typescript", ".js": "javascript", ".jsx": "javascript",
             ".mjs": "javascript", ".go": "go", ".java": "java", ".kt": "kotlin", ".rs": "rust", ".cs": "csharp",
             ".rb": "ruby", ".tf": "terraform", ".sh": "shell"}
LOCKFILES = {"package-lock.json", "pnpm-lock.yaml", "yarn.lock", "poetry.lock", "uv.lock", "Pipfile.lock",
             "Cargo.lock", "go.sum", "composer.lock", "bun.lock", "bun.lockb"}


class MapaError(Exception):
    pass


# ───────────────────────────── inventario ─────────────────────────────

def tracked_files(root: Path) -> list[str]:
    """Archivos versionados (git ls-files) o, fuera de git, todos salvo dependencias y worktrees."""
    r = subprocess.run(["git", "ls-files", "-z"], cwd=root, capture_output=True)
    if r.returncode == 0:
        return sorted(p for p in r.stdout.decode("utf-8", "replace").split("\0") if p)
    out = []
    for p in root.rglob("*"):
        rel = p.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts) or rel.parts[:2] == (".claude", "worktrees"):
            continue
        if p.is_file():
            out.append(rel.as_posix())
    return sorted(out)


def churn(root: Path, since: str) -> collections.Counter:
    """Commits que tocan cada archivo desde `since` (sintaxis de `git log --since`)."""
    r = subprocess.run(["git", "log", f"--since={since}", "--name-only", "--format=%x00"], cwd=root,
                       capture_output=True, text=True)
    c: collections.Counter = collections.Counter()
    if r.returncode != 0:
        return c
    for commit in r.stdout.split("\0"):
        for f in {ln.strip() for ln in commit.splitlines() if ln.strip()}:
            c[f] += 1
    return c


# ───────────────────────────── imports de Python ─────────────────────────────

def _raices(root: Path, files: list[str], declared: list[str] | None) -> list[str]:
    if declared is not None:
        return [r.strip("/") for r in declared]
    return [""] + (["src"] if any(f.startswith("src/") for f in files) else [])


def module_index(files: list[str], raices: list[str]) -> dict[str, str]:
    """módulo con puntos → archivo. Un archivo puede tener un nombre por raíz (`src/pkg/x.py` → `pkg.x`)."""
    idx: dict[str, str] = {}
    for f in files:
        if not f.endswith(".py"):
            continue
        for raiz in sorted(raices, key=len, reverse=True):
            if raiz and not f.startswith(raiz + "/"):
                continue
            rel = f[len(raiz) + 1:] if raiz else f
            parts = rel[:-3].split("/")
            if parts[-1] == "__init__":
                parts = parts[:-1]
            if parts and all(p.isidentifier() for p in parts):
                idx.setdefault(".".join(parts), f)
            break
    return idx


def python_imports(root: Path, files: list[str], raices: list[str]) -> tuple[list[tuple[str, str]], list[str]]:
    """Aristas (archivo origen, archivo destino) entre archivos del repositorio, y archivos que no se pudieron analizar."""
    idx = module_index(files, raices)
    inv = {p: m for m, p in idx.items()}
    edges: list[tuple[str, str]] = []
    fallidos: list[str] = []

    def resolver(nombre: str) -> str | None:
        parts = nombre.split(".")
        for i in range(len(parts), 0, -1):
            hit = idx.get(".".join(parts[:i]))
            if hit:
                return hit
        return None

    for f in files:
        if not f.endswith(".py") or f not in inv:
            continue
        try:
            tree = ast.parse((root / f).read_text(encoding="utf-8"), filename=f)
        except (SyntaxError, UnicodeDecodeError, OSError, ValueError):
            fallidos.append(f)
            continue
        mod = inv[f]
        paquete = mod if f.endswith("__init__.py") else mod.rpartition(".")[0]
        for n in ast.walk(tree):
            nombres: list[str] = []
            if isinstance(n, ast.Import):
                nombres = [a.name for a in n.names]
            elif isinstance(n, ast.ImportFrom):
                base = n.module or ""
                if n.level:
                    ups = paquete.split(".") if paquete else []
                    ups = ups[: len(ups) - (n.level - 1)] if n.level > 1 else ups
                    base = ".".join([*ups, base] if base else ups)
                nombres = [f"{base}.{a.name}" if base else a.name for a in n.names] or [base]
            for nombre in nombres:
                dst = resolver(nombre)
                if dst and dst != f:
                    edges.append((f, dst))
    return edges, fallidos


# ───────────────────────────── mapa ─────────────────────────────

@dataclass
class Segmento:
    id: str
    datos: dict
    _rx: list = field(default_factory=list)
    _ex: list = field(default_factory=list)

    def contiene(self, path: str) -> bool:
        return any(r.match(path) for r in self._rx) and not any(r.match(path) for r in self._ex)


@dataclass
class Mapa:
    datos: dict
    segmentos: list[Segmento]
    excluidos: list = field(default_factory=list)

    def asignar(self, path: str) -> list[str]:
        return [s.id for s in self.segmentos if s.contiene(path)]

    def excluido(self, path: str) -> bool:
        return any(r.match(path) for r in self.excluidos)


def _rx(pats):
    return [compile_pattern(p) for p in pats or []]


def _fechas_a_texto(x):
    """YAML convierte `2027-06-30` sin comillas en una fecha; el esquema espera texto con formato de fecha."""
    if isinstance(x, dict):
        return {k: _fechas_a_texto(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_fechas_a_texto(v) for v in x]
    return x.isoformat() if isinstance(x, (dt.date, dt.datetime)) else x


def load_map(std, root: Path, ruta: str = RUTA_MAPA) -> tuple[Mapa | None, list[str]]:
    p = root / ruta
    if not p.is_file():
        return None, [f"no existe {ruta}"]
    try:
        datos = yaml.safe_load(p.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        return None, [f"{ruta}: YAML inválido: {e}"]
    datos = _fechas_a_texto(datos)
    errs = [f"{ruta}: `{'/'.join(str(x) for x in e.absolute_path) or '(raíz)'}`: {e.message}"
            for e in std.validator("segments").iter_errors(datos)]
    if errs:
        return None, errs
    ids = [s["id"] for s in datos["segmentos"]]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        errs.append(f"{ruta}: ids repetidos: {', '.join(dup)}")
    for s in datos["segmentos"]:
        for d in s.get("depende_de") or []:
            if d not in ids:
                errs.append(f"{ruta}: `{s['id']}` depende de `{d}`, que no es un segmento")
            if d == s["id"]:
                errs.append(f"{ruta}: `{s['id']}` depende de sí mismo")
    for d in datos.get("deuda") or []:
        for k in ("de", "a"):
            if d[k] not in ids:
                errs.append(f"{ruta}: deuda `{d['de']} → {d['a']}`: `{d[k]}` no es un segmento")
    if errs:
        return None, errs
    segs = [Segmento(s["id"], s, _rx(s["rutas"]), _rx(s.get("excluir"))) for s in datos["segmentos"]]
    excl = [r for e in datos.get("excluidos") or [] for r in _rx(e["rutas"])]
    return Mapa(datos, segs, excl), []


# ───────────────────────────── graph ─────────────────────────────

def graph(std, root: Path, ruta: str = RUTA_MAPA, today: dt.date | None = None) -> dict:
    mapa, errs = load_map(std, root, ruta)
    if errs:
        raise MapaError("; ".join(errs))
    today = today or dt.date.today()
    files = tracked_files(root)
    seg_de: dict[str, str] = {}
    sin_asignar, solapados = [], []
    for f in files:
        ids = mapa.asignar(f)
        if len(ids) > 1:
            solapados.append((f, ids))
        if ids:
            seg_de[f] = ids[0]
        elif not mapa.excluido(f):
            sin_asignar.append(f)
    raices = _raices(root, files, (mapa.datos.get("python") or {}).get("raices"))
    edges, fallidos = python_imports(root, files, raices)
    cuenta: collections.Counter = collections.Counter()
    ejemplos: dict[tuple[str, str], tuple[str, str]] = {}
    for a, b in edges:
        sa, sb = seg_de.get(a), seg_de.get(b)
        if sa and sb and sa != sb:
            cuenta[(sa, sb)] += 1
            ejemplos.setdefault((sa, sb), (a, b))
    declaradas = {(s.id, d) for s in mapa.segmentos for d in s.datos.get("depende_de") or []}
    deuda = {(d["de"], d["a"]): d for d in mapa.datos.get("deuda") or []}
    aristas = []
    for (sa, sb), n in sorted(cuenta.items()):
        if (sa, sb) in declaradas:
            estado = "declarada"
        elif (sa, sb) in deuda:
            cad = dt.date.fromisoformat(str(deuda[(sa, sb)]["caduca"]))
            estado = "deuda caducada" if cad < today else "deuda"
        else:
            estado = "no declarada"
        aristas.append({"de": sa, "a": sb, "imports": n, "estado": estado, "ejemplo": list(ejemplos[(sa, sb)])})
    no_py = sorted({s.id for s in mapa.segmentos if (s.datos.get("lenguaje") or "python") != "python"})
    return {
        "mapa": ruta,
        "segmentos": [s.id for s in mapa.segmentos],
        "aristas": aristas,
        "declaradas_sin_uso": sorted(f"{a} → {b}" for a, b in declaradas - set(cuenta)),
        "deuda_sin_uso": sorted(f"{a} → {b}" for a, b in set(deuda) - set(cuenta)),
        "mutuas": sorted({f"{a} ↔ {b}" for (a, b) in cuenta if (b, a) in cuenta and a < b}),
        "sin_asignar": len(sin_asignar),
        "sin_asignar_ejemplos": sin_asignar[:10],
        "solapados": len(solapados),
        "solapados_ejemplos": [f"{f}: {', '.join(i)}" for f, i in solapados[:10]],
        "no_analizados": fallidos,
        "no_verificados": no_py,
    }


def graph_markdown(g: dict) -> str:
    segs = g["segmentos"]
    m = {(a["de"], a["a"]): a for a in g["aristas"]}
    marca = {"declarada": "", "deuda": " (D)", "deuda caducada": " (D!)", "no declarada": " **(X)**"}
    out = [f"# Dependencias reales entre segmentos ({g['mapa']})", "",
           "Imports de Python entre archivos de segmentos distintos. `(D)` deuda vigente, `(D!)` deuda caducada, "
           "**`(X)`** no declarada.", "", "| De ↓ / a → | " + " | ".join(segs) + " |",
           "|---|" + "---|" * len(segs)]
    for a in segs:
        fila = []
        for b in segs:
            e = m.get((a, b))
            fila.append("—" if a == b else (f"{e['imports']}{marca[e['estado']]}" if e else ""))
        out.append(f"| **{a}** | " + " | ".join(fila) + " |")
    resumen = collections.Counter(a["estado"] for a in g["aristas"])
    out += ["", f"**Aristas:** {len(g['aristas'])} — " + ", ".join(f"{k}: {v}" for k, v in sorted(resumen.items())),
            f"**Dependencias mutuas:** {len(g['mutuas'])}" + (f" ({'; '.join(g['mutuas'])})" if g["mutuas"] else ""),
            f"**Archivos sin segmento ni exclusión:** {g['sin_asignar']}"
            + (f" (p. ej. {', '.join(g['sin_asignar_ejemplos'][:3])})" if g["sin_asignar"] else ""),
            f"**Archivos en más de un segmento:** {g['solapados']}"]
    if g["declaradas_sin_uso"]:
        out.append(f"**Declaradas sin uso real:** {', '.join(g['declaradas_sin_uso'])}")
    if g["deuda_sin_uso"]:
        out.append(f"**Deuda ya saldada (se puede borrar):** {', '.join(g['deuda_sin_uso'])}")
    if g["no_verificados"]:
        out.append(f"**No verificados (no Python, 2e):** {', '.join(g['no_verificados'])}")
    if g["no_analizados"]:
        out.append(f"**Archivos Python no analizables:** {len(g['no_analizados'])}")
    return "\n".join(out) + "\n"


def deuda_yaml(g: dict, caduca: str) -> str:
    """Entradas de `deuda` para las aristas no declaradas (o con deuda caducada), para revisar a mano."""
    items = [{"de": a["de"], "a": a["a"], "motivo": f"TODO: {a['imports']} imports heredados (p. ej. {a['ejemplo'][0]} → {a['ejemplo'][1]})",
              "caduca": caduca} for a in g["aristas"] if a["estado"] in ("no declarada", "deuda caducada")]
    return yaml.safe_dump({"deuda": items}, allow_unicode=True, sort_keys=False, width=200)


# ───────────────────────────── propose ─────────────────────────────

def _grupo(f: str, dividir: list[str], profundidad: int) -> str:
    parts = f.split("/")
    if len(parts) == 1:
        return "(raíz)"
    prof = profundidad
    for d in sorted(dividir, key=len, reverse=True):
        d = d.strip("/")
        if f.startswith(d + "/"):
            prof = d.count("/") + 2
            break
    prof = min(prof, len(parts) - 1)
    return "/".join(parts[:prof])


def _slug(g: str) -> str:
    import unicodedata
    g = unicodedata.normalize("NFKD", g).encode("ascii", "ignore").decode()
    s = "".join(ch if ch.isascii() and ch.isalnum() else "-" for ch in g.lower()).strip("-")
    while "--" in s:
        s = s.replace("--", "-")
    s = s or "raiz"
    return (s if s[0].isalpha() else "s-" + s)[:40]


def propose(root: Path, since: str = "12 months ago", profundidad: int = 1, dividir: list[str] | None = None,
            top_calientes: int = 10) -> dict:
    dividir = dividir or []
    files = tracked_files(root)
    if not files:
        raise MapaError("no hay archivos versionados")
    ch = churn(root, since)
    grupos: dict[str, list[str]] = collections.defaultdict(list)
    for f in files:
        grupos[_grupo(f, dividir, profundidad)].append(f)
    co_text = next(((root / p).read_text(encoding="utf-8") for p in (".github/CODEOWNERS", "CODEOWNERS", "docs/CODEOWNERS")
                    if (root / p).is_file()), "")
    co = parse_codeowners(co_text)
    raices = _raices(root, files, None)
    edges, fallidos = python_imports(root, files, raices)
    grupo_de = {f: g for g, fs in grupos.items() for f in fs}
    dep: collections.Counter = collections.Counter()
    for a, b in edges:
        ga, gb = grupo_de[a], grupo_de[b]
        if ga != gb:
            dep[(ga, gb)] += 1
    cands = []
    for g, fs in sorted(grupos.items(), key=lambda kv: -len(kv[1])):
        langs = collections.Counter(LENGUAJES.get(Path(f).suffix.lower()) for f in fs)
        langs.pop(None, None)
        owners = collections.Counter(" ".join(r.owners) for f in fs if (r := owners_for(co, f)))
        commits = sum(ch[f] for f in fs)
        calientes = []
        for f in fs:
            name = Path(f).name
            if name in LOCKFILES:
                calientes.append({"ruta": "/" + f, "motivo": "archivo de bloqueo de dependencias: conflicto textual seguro"})
        mig = sorted({str(Path(f).parent) for f in fs
                      if f.endswith(".py") and Path(f).parent.name == "versions" and "migrations" in f.split("/")})
        for d in mig:
            calientes.append({"ruta": "/" + d + "/", "motivo": "migraciones encadenadas: dos a la vez rompen la cadena sin conflicto textual"})
        cands.append({
            "grupo": g, "id": _slug(g), "archivos": len(fs), "commits": commits,
            "archivos_raiz": fs if g == "(raíz)" else [],
            "lenguajes": dict(langs.most_common(3)),
            "propietarios": dict(owners.most_common(2)),
            "depende_de": sorted({b for (a, b) in dep if a == g}),
            "excluir_sugerido": g.split("/")[0].lower() in EXCLUIR_SUGERIDO,
            "calientes": calientes,
            "top_cambio": [f for f, _ in sorted(((f, ch[f]) for f in fs if ch[f]), key=lambda x: -x[1])[:3]],
        })
    mutuas = sorted({f"{a} ↔ {b}" for (a, b) in dep if (b, a) in dep and a < b})
    return {"desde": since, "archivos": len(files),
            "candidatos": cands, "dependencias": [{"de": a, "a": b, "imports": n} for (a, b), n in sorted(dep.items())],
            "mutuas": mutuas, "no_analizados": fallidos, "top_calientes": [f for f, _ in ch.most_common(top_calientes)]}


def propose_markdown(p: dict) -> str:
    out = ["# Propuesta de segmentación (borrador, no aprobada)", "",
           f"Archivos versionados: {p['archivos']}. Cambio medido desde: {p['desde']}. "
           "Revísala, agrupa candidatos y versiona `.harness/segments.yaml` en un PR (ADR-014 rev. 2, 2a).", "",
           "| Candidato | id | Archivos | Commits | Lenguajes | Propietario (CODEOWNERS) | Depende de | Notas |",
           "|---|---|---|---|---|---|---|---|"]
    for c in p["candidatos"]:
        notas = []
        if c["excluir_sugerido"]:
            notas.append("¿excluir?")
        notas += [f"caliente: `{h['ruta']}`" for h in c["calientes"]]
        langs = ", ".join(f"{k} {v}" for k, v in c["lenguajes"].items()) or "—"
        owners = ", ".join(c["propietarios"]) or "—"
        deps = ", ".join(c["depende_de"]) or "—"
        out.append(f"| `{c['grupo']}` | `{c['id']}` | {c['archivos']} | {c['commits']} | {langs} | {owners} | {deps} | {'; '.join(notas)} |")
    out += ["", f"**Dependencias mutuas entre candidatos:** {len(p['mutuas'])}"
            + (f" — {'; '.join(p['mutuas'])}" if p["mutuas"] else ""),
            "Si hay muchas, describe la realidad con `depende_de` y lleva lo no deseado a `deuda` con caducidad (2c).",
            "", "**Archivos con más cambio:** " + (", ".join(f"`{f}`" for f in p["top_calientes"]) or "—")]
    if p["no_analizados"]:
        out.append(f"**Archivos Python no analizables:** {len(p['no_analizados'])}")
    out.append("\nSolo se analizan imports de Python; el resto de dependencias quedan sin verificar (2e).")
    return "\n".join(out) + "\n"


def propose_yaml(p: dict) -> str:
    segs, excl = [], []
    for c in p["candidatos"]:
        # Siempre ancladas con '/': `tests/` sin ancla cubriría cualquier `tests/` anidado (semántica gitignore).
        rutas = ["/" + f for f in c["archivos_raiz"]] if c["grupo"] == "(raíz)" else ["/" + c["grupo"] + "/"]
        if c["excluir_sugerido"]:
            excl.append({"rutas": rutas, "motivo": "TODO: confirmar que no contiene código de la aplicación"})
            continue
        owner = next(iter(c["propietarios"]), "").split(" ")[0]
        s = {"id": c["id"], "proposito": "TODO", "rutas": rutas,
             "propietario": owner if owner.startswith("@") else "TODO",
             "riesgo": "medio", "paralelizacion": "contrato"}
        lang = next(iter(c["lenguajes"]), None)
        if lang:
            s["lenguaje"] = lang
        ids = {x["grupo"]: x["id"] for x in p["candidatos"]}
        deps = [ids[d] for d in c["depende_de"] if d in ids]
        if deps:
            s["depende_de"] = deps
        if c["calientes"]:
            s["puntos_calientes"] = [{"rutas": [h["ruta"]], "paralelizacion": "serializada", "motivo": h["motivo"]}
                                     for h in c["calientes"]]
        segs.append(s)
    doc = {"version": 1, "segmentos": segs}
    if excl:
        doc["excluidos"] = excl
    cab = ("# BORRADOR generado por `harness segments propose`: NO es el mapa aprobado.\n"
           "# Los `TODO` hacen fallar el esquema a propósito: una persona revisa propósito, propietario, riesgo y\n"
           "# paralelización, agrupa candidatos y lleva a `deuda` las dependencias no deseadas (ADR-014 rev. 2).\n")
    return cab + yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=200)
