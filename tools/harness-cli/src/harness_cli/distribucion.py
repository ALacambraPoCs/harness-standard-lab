"""Distribución de componentes del catálogo a una instancia por copia versionada (ADR-017).

- El catálogo es el que viaja con la CLI (`<raíz del estándar>/catalog`): fijar la CLI fija el catálogo.
- `.harness/components.lock` registra lo instalado: versión, origen, SHA-256 de cada archivo y el
  fragmento de configuración fusionado. Es la base para detectar deriva (HS-CMP-009).
- Nunca se sobrescribe ni se borra un archivo modificado en local o no gestionado.
"""
from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import yaml

from . import __version__
from .standard import Standard, semver

LOCK = ".harness/components.lock"
SETTINGS = ".claude/settings.json"
LOCK_FORMAT = 1


class DistribucionError(Exception):
    pass


@dataclass
class Componente:
    id: str
    dir: Path
    data: dict


def _sha(p: Path) -> str:
    """SHA-256 con finales de línea normalizados (CRLF → LF): `core.autocrlf` en Windows no es deriva."""
    return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def catalogo(std: Standard) -> dict[str, Componente]:
    base = std.root / "catalog"
    out = {}
    for entry in sorted(base.glob("*/*/componente.yaml")) if base.is_dir() else []:
        data = yaml.safe_load(entry.read_text(encoding="utf-8"))
        out[data["id"]] = Componente(data["id"], entry.parent, data)
    return out


def leer_lock(root: Path) -> dict:
    p = root / LOCK
    if not p.is_file():
        return {"formato": LOCK_FORMAT, "componentes": {}}
    data = json.loads(p.read_text(encoding="utf-8"))
    if data.get("formato") != LOCK_FORMAT or not isinstance(data.get("componentes"), dict):
        raise DistribucionError(f"{LOCK} no tiene un formato reconocido (formato {LOCK_FORMAT}).")
    return data


def escribir_lock(root: Path, lock: dict) -> None:
    p = root / LOCK
    p.parent.mkdir(parents=True, exist_ok=True)
    lock["componentes"] = dict(sorted(lock["componentes"].items()))
    p.write_text(json.dumps(lock, indent=2, ensure_ascii=False, sort_keys=False) + "\n", encoding="utf-8")


# ─────────────── fusión de settings.json (solo añade) ───────────────
def _merge(dst, src):
    """Fusiona `src` en `dst` añadiendo claves y elementos de lista que falten (igualdad estructural)."""
    if isinstance(dst, dict) and isinstance(src, dict):
        for k, v in src.items():
            dst[k] = _merge(dst[k], v) if k in dst else copy.deepcopy(v)
        return dst
    if isinstance(dst, list) and isinstance(src, list):
        for item in src:
            if item not in dst:
                dst.append(copy.deepcopy(item))
        return dst
    if dst != src:
        raise DistribucionError(f"conflicto de configuración: valor existente {dst!r} distinto del requerido {src!r}")
    return dst


def _unmerge(dst, src):
    """Quita de `dst` lo que aportó `src` (elementos de lista idénticos; claves que quedan vacías)."""
    if isinstance(dst, dict) and isinstance(src, dict):
        for k, v in src.items():
            if k in dst:
                dst[k] = _unmerge(dst[k], v)
                if dst[k] in ({}, []):
                    del dst[k]
        return dst
    if isinstance(dst, list) and isinstance(src, list):
        return [x for x in dst if x not in src]
    return dst


def _contiene(dst, src) -> bool:
    if isinstance(src, dict):
        return isinstance(dst, dict) and all(k in dst and _contiene(dst[k], v) for k, v in src.items())
    if isinstance(src, list):
        return isinstance(dst, list) and all(any(_contiene(d, s) for d in dst) for s in src)
    return dst == src


def _settings(root: Path) -> dict:
    p = root / SETTINGS
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


def _guardar_settings(root: Path, data: dict) -> None:
    p = root / SETTINGS
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# ─────────────── operaciones ───────────────
def _resolver(cat: dict[str, Componente], ids: list[str]) -> list[Componente]:
    orden: list[Componente] = []

    def visita(i: str, camino: tuple[str, ...]):
        if i in camino:
            raise DistribucionError(f"dependencia circular: {' → '.join(camino + (i,))}")
        if i not in cat:
            raise DistribucionError(f"`{i}` no existe en el catálogo de esta CLI ({__version__}).")
        for d in cat[i].data.get("dependencias") or []:
            visita(d, camino + (i,))
        if cat[i] not in orden:
            orden.append(cat[i])

    for i in ids:
        visita(i, ())
    return orden


def deriva(root: Path, entrada: dict) -> list[str]:
    """Problemas de un componente instalado frente a su registro en el lock."""
    out = []
    for f in entrada.get("archivos", []):
        p = root / f["destino"]
        if not p.is_file():
            out.append(f"falta {f['destino']}")
        elif _sha(p) != f["sha256"]:
            out.append(f"{f['destino']} modificado en local")
    frag = entrada.get("claude_settings")
    if frag:
        try:
            ok = _contiene(_settings(root), frag)
        except json.JSONDecodeError:
            ok = False
        if not ok:
            out.append(f"falta en {SETTINGS} la configuración que aporta el componente")
    return out


def _instalar(root: Path, std: Standard, c: Componente, lock: dict, actualizar: bool) -> str:
    previo = lock["componentes"].get(c.id)
    if previo and not actualizar:
        return f"{c.id} {previo['version']}: ya instalado (usa `harness components sync` para actualizar)"
    if previo and deriva(root, previo):
        raise DistribucionError(f"{c.id}: hay cambios locales ({'; '.join(deriva(root, previo))}). "
                                "Restáuralos o conviértelo en un componente propio antes de actualizar.")
    if c.data.get("estado") == "retirado":
        raise DistribucionError(f"{c.id} está retirado en el catálogo.")
    gestionados = {f["destino"] for f in (previo or {}).get("archivos", [])}
    archivos = []
    for a in c.data.get("archivos") or []:
        dst = root / a["destino"]
        if dst.exists() and a["destino"] not in gestionados:
            raise DistribucionError(f"{c.id}: {a['destino']} ya existe y no lo gestiona el lock. Muévelo o bórralo antes de instalar.")
    if previo and previo.get("claude_settings"):
        _guardar_settings(root, _unmerge(_settings(root), previo["claude_settings"]))
    for f in (previo or {}).get("archivos", []):
        nuevos = {a["destino"] for a in c.data.get("archivos") or []}
        if f["destino"] not in nuevos and (root / f["destino"]).is_file():
            (root / f["destino"]).unlink()
    for a in c.data.get("archivos") or []:
        src, dst = c.dir / a["origen"], root / a["destino"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())
        archivos.append({"destino": a["destino"], "sha256": _sha(dst)})
    frag = (c.data.get("configuracion") or {}).get("claude_settings")
    if frag:
        _guardar_settings(root, _merge(_settings(root), frag))
    lock["componentes"][c.id] = {
        "tipo": c.data["tipo"], "version": c.data["version"], "estado": c.data["estado"],
        "origen": {"estandar": std.version, "cli": __version__},
        "archivos": archivos, **({"claude_settings": frag} if frag else {}),
    }
    accion = f"actualizado {previo['version']} → {c.data['version']}" if previo else f"instalado {c.data['version']}"
    aviso = " (DEPRECADO en el catálogo)" if c.data.get("estado") == "deprecado" else ""
    return f"{c.id}: {accion}{aviso}"


def add(root: Path, std: Standard, ids: list[str]) -> list[str]:
    cat, lock = catalogo(std), leer_lock(root)
    log = [_instalar(root, std, c, lock, actualizar=False) for c in _resolver(cat, ids)]
    escribir_lock(root, lock)
    return log


def sync(root: Path, std: Standard) -> list[str]:
    cat, lock = catalogo(std), leer_lock(root)
    log = []
    for i, e in list(lock["componentes"].items()):
        if i not in cat:
            log.append(f"{i}: ya no existe en el catálogo de esta CLI; se mantiene (revísalo)")
            continue
        nueva, actual = semver(cat[i].data["version"]), semver(e["version"])
        if nueva and actual and nueva > actual:
            log.append(_instalar(root, std, cat[i], lock, actualizar=True))
        elif nueva and actual and nueva < actual:
            log.append(f"{i}: la versión instalada ({e['version']}) es posterior a la del catálogo de esta CLI; actualiza la CLI")
        else:
            log.append(f"{i} {e['version']}: al día")
    escribir_lock(root, lock)
    return log


def remove(root: Path, std: Standard, ids: list[str]) -> list[str]:
    cat, lock = catalogo(std), leer_lock(root)
    log = []
    for i in ids:
        e = lock["componentes"].get(i)
        if not e:
            raise DistribucionError(f"`{i}` no está instalado.")
        dependientes = [o for o in lock["componentes"] if o != i and o not in ids and o in cat
                        and i in (cat[o].data.get("dependencias") or [])]
        if dependientes:
            raise DistribucionError(f"`{i}` lo necesita {', '.join(dependientes)}; retíralos antes.")
        mod = [d for d in deriva(root, e) if "modificado" in d]
        if mod:
            raise DistribucionError(f"{i}: {'; '.join(mod)}. No se borra un archivo modificado.")
        for f in e["archivos"]:
            (root / f["destino"]).unlink(missing_ok=True)
        if e.get("claude_settings"):
            _guardar_settings(root, _unmerge(_settings(root), e["claude_settings"]))
        del lock["componentes"][i]
        log.append(f"{i}: retirado")
    escribir_lock(root, lock)
    return log


def listado(root: Path, std: Standard) -> list[str]:
    cat, lock = catalogo(std), leer_lock(root)
    rows = []
    for i, c in sorted(cat.items()):
        e = lock["componentes"].get(i)
        if e:
            estado = "al día" if e["version"] == c.data["version"] else f"desactualizado (catálogo {c.data['version']})"
            problemas = deriva(root, e)
            rows.append(f"{i:<24} {c.data['tipo']:<10} instalado {e['version']} · {estado}" + (f" · DERIVA: {'; '.join(problemas)}" if problemas else ""))
        else:
            rows.append(f"{i:<24} {c.data['tipo']:<10} disponible {c.data['version']} ({c.data['estado']})")
    return rows
