"""Integridad de las fichas de archivo (standard/04-archivos) frente a roles.yaml."""
import re
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from harness_cli.standard import load_standard

ROOT = Path(__file__).resolve().parents[1]
FICHAS = sorted(p for p in (ROOT / "standard" / "04-archivos").glob("*.md") if not p.name.startswith("_"))
SECCIONES = ["Propósito", "Contenido requerido", "Contenido excluido", "Formato y convenciones",
             "Ejemplo canónico", "Validaciones", "Criterios de aceptación", "Ciclo de vida y evolución"]


def _frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, "falta frontmatter"
    return yaml.safe_load(m.group(1)), text[m.end():]


def test_fichas_validas_y_coherentes_con_roles():
    std = load_standard()
    import json
    schema = json.loads((ROOT / "schemas" / "ficha.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    for f in FICHAS:
        fm, body = _frontmatter(f.read_text(encoding="utf-8"))
        errs = [e.message for e in validator.iter_errors(fm)]
        assert not errs, f"{f.name}: {errs}"
        for rol in [fm["rol"], *fm.get("roles_adicionales", [])]:
            assert rol in std.roles, f"{f.name}: rol {rol} no existe en roles.yaml"
            assert std.roles[rol]["ficha"] == f"standard/04-archivos/{f.name}", \
                f"roles.yaml#{rol}.ficha debe apuntar a {f.name}"
        for dep in fm["dependencias"]:
            assert dep in std.roles, f"{f.name}: dependencia {dep} no es un rol"
        for req in fm["requisitos"]:
            assert req.startswith("pendiente:") or req in std.requirements, f"{f.name}: {req} inexistente"
        for sec in SECCIONES:
            assert re.search(rf"^## {re.escape(sec)}\s*$", body, re.M), f"{f.name}: falta sección '{sec}'"
        assert (ROOT / fm["ejemplo_canonico"]).exists(), f"{f.name}: no existe {fm['ejemplo_canonico']}"


def test_fichas_declaradas_en_roles_existen():
    std = load_standard()
    for rol, spec in std.roles.items():
        if not spec["ficha"].startswith("pendiente:"):
            assert (ROOT / spec["ficha"]).is_file(), f"roles.yaml#{rol}: ficha {spec['ficha']} no existe"
