"""Esquema de entrada de catálogo (F3.1): casos válidos e inválidos por regla."""
import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
V = Draft202012Validator(json.loads((ROOT / "schemas/catalog-entry.schema.json").read_text(encoding="utf-8")),
                         format_checker=FormatChecker())

BASE = {
    "id": "rutas-sensibles", "tipo": "hook", "version": "0.1.0", "estado": "experimental",
    "titulo": "Confirmar ediciones de rutas sensibles",
    "proposito": "Pide confirmación humana antes de que el agente edite configuración de agentes o CI.",
    "propietario": "@org/plataforma",
    "compatibilidad": {"adaptadores": ["claude-code"], "agente_min": {"claude-code": "2.1.277"}, "niveles": ["N1"]},
    "contrato": {"entradas": ["Evento PreToolUse de Edit/Write"], "salidas": ["Decisión ask o allow"], "efectos": []},
    "permisos": {"herramientas": [], "escritura": [], "red": "ninguna", "secretos": False},
    "control": {"es_control": True, "capa": "L3", "determinista": True, "hook_tipo": "command"},
    "archivos": [{"origen": "src/rutas_sensibles.py", "destino": ".claude/hooks/rutas_sensibles.py"}],
    "pruebas": [{"tipo": "unitaria", "descripcion": "Casos de rutas sensibles y no sensibles", "comando": "pytest tests"}],
    "metricas": ["Confirmaciones pedidas por semana"],
    "coste": {"contexto": "nulo", "latencia": "< 100 ms por llamada"},
    "riesgos": ["Fatiga de confirmaciones si los patrones son demasiado amplios"],
    "retirada": {"condicion": "Si el ruleset de plataforma cubre el caso sin fricción", "procedimiento": "Deprecar, quitar de settings.json"},
    "ficha": "FICHA.md",
}


def errs(doc):
    return [e.message for e in V.iter_errors(doc)]


def mut(**changes):
    d = copy.deepcopy(BASE)
    for path, value in changes.items():
        cur = d
        keys = path.split("__")
        for k in keys[:-1]:
            cur = cur[int(k)] if isinstance(cur, list) else cur[k]
        last = int(keys[-1]) if isinstance(cur, list) else keys[-1]
        if value is ...:
            del cur[last]
        else:
            cur[last] = value
    return d


def test_valido():
    assert errs(BASE) == []


def test_skill_portable_valida():
    d = mut(tipo="skill", control={"es_control": False, "capa": "L1", "determinista": False})
    d["compatibilidad"]["perfil"] = "portable"
    assert errs(d) == []


@pytest.mark.parametrize("changes", [
    {"id": "Rutas"}, {"id": "a--b"}, {"id": "-a"}, {"id": "a" * 65},
    {"version": "1.0"}, {"estado": "beta"}, {"propietario": "org"},
    {"proposito": "corto"},
    {"pruebas": []}, {"metricas": []}, {"riesgos": []},
    {"archivos__0__origen": "rutas.py"}, {"archivos__0__destino": "../fuera.py"}, {"archivos__0__destino": "/abs.py"},
    {"retirada": ...},
    {"permisos__red": "toda"},
    {"control__hook_tipo": ...},                                          # hook sin hook_tipo
    {"control__hook_tipo": "prompt"},                                     # prompt nunca es control (C9)
    {"tipo": "subagente"},                                                # control solo hook/workflow
    {"control__determinista": False},                                     # control no determinista
    {"control__capa": "L1"},                                              # control en L1
    {"estado": "estable"},                                                # sin evidencia
    {"estado": "deprecado"},                                              # sin deprecacion
    {"tipo": "skill", "control": {"es_control": False, "capa": "L1", "determinista": False}},  # skill sin perfil
])
def test_invalido(changes):
    assert errs(mut(**changes)), changes


def test_perfil_solo_en_skills():
    d = copy.deepcopy(BASE)
    d["compatibilidad"]["perfil"] = "portable"
    assert errs(d)


def test_estable_con_red_exige_revision_seguridad():
    d = mut(estado="estable", evidencia=["https://github.com/org/repo/pull/1"], permisos__red=["api.github.com"])
    assert errs(d)
    d["revision_seguridad"] = "@org/seguridad 2026-10-22"
    assert errs(d) == []
