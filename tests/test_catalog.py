"""`harness catalog validate` (catálogo central, F3.3): reglas catalog.* sobre repositorios temporales."""
import copy
import subprocess
from pathlib import Path

import pytest
import yaml

from harness_cli.catalog import validate
from harness_cli.standard import load_standard

STD = load_standard()
PLANTILLA = (Path(__file__).resolve().parents[1] / "standard/05-componentes/_PLANTILLA-FICHA.md").read_text(encoding="utf-8")

SKILL = {
    "id": "cerrar-tarea", "tipo": "skill", "version": "0.1.0", "estado": "experimental",
    "titulo": "Cerrar una tarea según ADR-016",
    "proposito": "Guía al agente para cerrar una tarea en el PR que la completa, con done_pr y resultado.",
    "propietario": "@org/plataforma",
    "compatibilidad": {"adaptadores": ["claude-code"], "perfil": "portable", "niveles": ["N1"]},
    "contrato": {"entradas": ["Tarea T-NNNN en curso"], "salidas": ["Archivo de tarea en completed/"], "efectos": ["Edita docs/plans/"]},
    "permisos": {"herramientas": ["Read", "Edit"], "escritura": ["docs/plans/**"], "red": "ninguna", "secretos": False},
    "control": {"es_control": False, "capa": "L1", "determinista": False},
    "archivos": [{"origen": "src/SKILL.md", "destino": ".claude/skills/cerrar-tarea/SKILL.md"}],
    "pruebas": [{"tipo": "eval", "descripcion": "Cierra una tarea de ejemplo correctamente"}],
    "metricas": ["PR que fallan por tasks.done-pr"],
    "coste": {"contexto": "~100 tokens", "latencia": "nula"},
    "riesgos": ["Que el agente marque done antes de abrir el PR"],
    "retirada": {"condicion": "Si harness rellena done_pr automáticamente", "procedimiento": "Deprecar y quitar de .claude/skills/"},
    "ficha": "FICHA.md",
}
SKILL_MD = "---\nname: cerrar-tarea\ndescription: Cierra una tarea según ADR-016.\nmetadata:\n  harness-perfil: portable\n---\n\n# Cerrar\n"


def git(root, *a):
    return subprocess.run(["git", *a], cwd=root, check=True, capture_output=True, text=True).stdout.strip()


def make(root: Path, entry=None, skill_md=SKILL_MD, ficha=PLANTILLA, where="catalog/skill/cerrar-tarea"):
    d = root / where
    (d / "src").mkdir(parents=True, exist_ok=True)
    (d / "componente.yaml").write_text(yaml.safe_dump(entry or SKILL, allow_unicode=True, sort_keys=False), encoding="utf-8")
    if skill_md is not None:
        (d / "src/SKILL.md").write_text(skill_md, encoding="utf-8")
    if ficha is not None:
        (d / "FICHA.md").write_text(ficha, encoding="utf-8")
    return d


def rules(findings):
    return sorted({f.rule for f in findings if f.severity == "error"})


def test_valido(tmp_path):
    make(tmp_path)
    f, n = validate(STD, tmp_path)
    assert n == 1 and rules(f) == []


@pytest.mark.parametrize("change,rule", [
    ({"estado": "beta"}, "catalog.entry"),
    ({"id": "otra"}, "catalog.entry"),                     # id ≠ directorio (y name de la skill ≠ id)
    ({"tipo": "hook"}, "catalog.entry"),                   # tipo ≠ directorio
    ({"archivos": [{"origen": "src/NOEXISTE.md", "destino": ".claude/skills/cerrar-tarea/SKILL.md"}]}, "catalog.entry"),
    ({"archivos": [{"origen": "src/SKILL.md", "destino": ".agents/skills/cerrar-tarea/SKILL.md"}]}, "catalog.skill"),
])
def test_entrada_invalida(tmp_path, change, rule):
    e = copy.deepcopy(SKILL)
    e.update(change)
    make(tmp_path, entry=e)
    assert rule in rules(validate(STD, tmp_path)[0])


def test_ficha_incompleta(tmp_path):
    make(tmp_path, ficha="# Ficha\n\n## 1. Nombre y propósito\nx\n")
    assert "catalog.ficha" in rules(validate(STD, tmp_path)[0])


def test_ficha_ausente(tmp_path):
    make(tmp_path, ficha=None)
    assert "catalog.ficha" in rules(validate(STD, tmp_path)[0])


@pytest.mark.parametrize("md", [
    "---\nname: Cerrar\ndescription: x\n---\n",                                   # name inválido
    "---\nname: cerrar-tarea\ndescription: x\npaths: ['**']\n---\n",               # extensión en perfil portable
    "---\nname: cerrar-tarea\ndescription: x\nmetadata:\n  harness-perfil: claude-code\n---\n",  # perfil ≠ entrada
])
def test_skill_invalida(tmp_path, md):
    make(tmp_path, skill_md=md)
    assert "catalog.skill" in rules(validate(STD, tmp_path)[0])


# ─────────────── transiciones y versión (con --base) ───────────────
@pytest.fixture
def repo(tmp_path):
    make(tmp_path)
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "add", "-A")
    git(tmp_path, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "base")
    return tmp_path


def _change(repo, msg="cambio", **kw):
    e = copy.deepcopy(SKILL)
    e.update(kw)
    make(repo, entry=e, skill_md=kw.pop("_md", SKILL_MD))
    git(repo, "add", "-A")
    git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", msg)


def test_transicion_ilegal(repo):
    base = git(repo, "rev-parse", "HEAD")
    _change(repo, estado="deprecado", version="0.2.0", deprecacion={"motivo": "Sustituida por otra skill", "fecha": "2026-10-22"})
    assert "catalog.transition" in rules(validate(STD, repo, base=base)[0])


def test_transicion_legal_y_version(repo):
    base = git(repo, "rev-parse", "HEAD")
    _change(repo, estado="estable", version="0.2.0", evidencia=["https://github.com/org/repo/pull/7"])
    assert rules(validate(STD, repo, base=base)[0]) == []


def test_cambio_sin_subir_version(repo):
    base = git(repo, "rev-parse", "HEAD")
    (repo / "catalog/skill/cerrar-tarea/src/SKILL.md").write_text(SKILL_MD + "\nPaso nuevo.\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "edita")
    assert "catalog.version" in rules(validate(STD, repo, base=base)[0])


def test_catalogo_real_del_repositorio():
    root = Path(__file__).resolve().parents[1]
    f, _ = validate(STD, root)
    assert rules(f) == [], [x.message for x in f]
