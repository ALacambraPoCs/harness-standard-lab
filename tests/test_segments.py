"""Mapa de segmentos (F4.2, ADR-014 rev. 2, D-083): propose y graph sobre un repositorio git real (sin red)."""
import datetime as dt
import json
import subprocess
from pathlib import Path

import pytest
import yaml

from harness_cli import cli
from harness_cli import segments as S
from harness_cli.standard import load_standard

STD = load_standard()

ARCHIVOS = {
    "app/__init__.py": "",
    "app/api/__init__.py": "",
    "app/api/rutas.py": "from app.dominio import reglas\nimport app.db.modelos\n",
    "app/dominio/__init__.py": "",
    "app/dominio/reglas.py": "from ..db import modelos\nfrom . import util\n",
    "app/dominio/util.py": "import os\n",
    "app/db/__init__.py": "",
    "app/db/modelos.py": "from app.api.rutas import x  # ciclo heredado\n",
    "app/db/migrations/versions/0001_inicial.py": "revision = '0001'\n",
    "app/roto.py": "def (:\n",
    "web/src/main.ts": "import x from './x'\n",
    "web/package-lock.json": "{}\n",
    "tests/test_x.py": "from app.api import rutas\n",
    "docs/guia.md": "# guía\n",
    "README.md": "# repo\n",
    ".github/CODEOWNERS": "* @ana\n/web/ @equipo/front\n",
}

MAPA = """version: 1
segmentos:
  - id: api
    proposito: Rutas HTTP de la aplicación.
    rutas: [/app/api/, /app/__init__.py, /app/roto.py]
    propietario: "@ana"
    lenguaje: python
    depende_de: [dominio]
    riesgo: medio
    paralelizacion: contrato
  - id: dominio
    proposito: Reglas de negocio sin E/S.
    rutas: [/app/dominio/]
    propietario: "@ana"
    depende_de: [db]
    riesgo: medio
    paralelizacion: contrato
  - id: db
    proposito: Modelos y migraciones.
    rutas: [/app/db/]
    propietario: "@ana"
    riesgo: medio
    paralelizacion: contrato
    puntos_calientes:
      - rutas: [/app/db/migrations/versions/]
        paralelizacion: serializada
        motivo: Cadena lineal de migraciones.
  - id: web
    proposito: Interfaz web en TypeScript.
    rutas: [/web/]
    propietario: "@equipo/front"
    lenguaje: typescript
    riesgo: bajo
    paralelizacion: libre
  - id: pruebas
    proposito: Pruebas del backend.
    rutas: [/tests/]
    propietario: "@ana"
    depende_de: [api]
    riesgo: bajo
    paralelizacion: libre
excluidos:
  - rutas: [/docs/, /README.md, /.github/]
    motivo: Documentación y metadatos del repositorio.
deuda:
  - de: db
    a: api
    motivo: Import heredado de rutas desde modelos.
    caduca: {caduca}
"""


def git(root, *args):
    return subprocess.run(["git", "-c", "user.email=ana@x", "-c", "user.name=Ana", *args], cwd=root, check=True,
                          capture_output=True, text=True).stdout


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"
    for rel, txt in ARCHIVOS.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(txt, encoding="utf-8")
    git(root, "init", "-q", "-b", "main")
    git(root, "add", "-A")
    git(root, "commit", "-qm", "base")
    (root / "app/api/rutas.py").write_text(ARCHIVOS["app/api/rutas.py"] + "# cambio\n", encoding="utf-8")
    git(root, "commit", "-qam", "cambio")
    (root / "no_versionado.py").write_text("import app\n", encoding="utf-8")
    return root


def con_mapa(root, caduca="2027-06-30", texto=None):
    (root / ".harness").mkdir(exist_ok=True)
    (root / ".harness/segments.yaml").write_text(texto or MAPA.replace("{caduca}", caduca), encoding="utf-8")
    return root


def test_imports_absolutos_y_relativos(repo):
    edges, fallidos = S.python_imports(repo, S.tracked_files(repo), [""])
    assert ("app/dominio/reglas.py", "app/db/modelos.py") in edges        # from ..db import modelos
    assert ("app/dominio/reglas.py", "app/dominio/util.py") in edges      # from . import util
    assert ("app/api/rutas.py", "app/db/modelos.py") in edges             # import app.db.modelos
    assert fallidos == ["app/roto.py"]


def test_propose_no_escribe(repo):
    antes = git(repo, "status", "--porcelain")
    for fmt in ("md", "yaml", "json"):
        assert cli.main(["segments", "propose", "--path", str(repo), "--dividir", "app", "--format", fmt]) == 0
    assert git(repo, "status", "--porcelain") == antes
    assert not (repo / ".harness").exists()


def test_propose_detecta_ciclo_propietario_y_calientes(repo):
    p = S.propose(repo, dividir=["app"])
    c = {x["grupo"]: x for x in p["candidatos"]}
    assert "app/api ↔ app/db" in p["mutuas"]
    assert c["web"]["propietarios"] == {"@equipo/front": 1} or "@equipo/front" in c["web"]["propietarios"]
    assert c["app/api"]["commits"] >= 2
    assert any("migrations/versions" in h["ruta"] for h in c["app/db"]["calientes"])
    assert any(h["ruta"] == "/web/package-lock.json" for h in c["web"]["calientes"])
    assert c["docs"]["excluir_sugerido"]
    assert "no_versionado.py" not in json.dumps(p)


def test_borrador_falla_el_esquema_a_proposito(repo):
    borrador = S.propose_yaml(S.propose(repo, dividir=["app"]))
    assert "/tests/" in borrador                      # rutas ancladas
    con_mapa(repo, texto=borrador)
    mapa, errs = S.load_map(STD, repo)
    assert mapa is None and any("proposito" in e for e in errs)


def test_graph_clasifica_aristas(repo):
    g = S.graph(STD, con_mapa(repo), today=dt.date(2026, 11, 13))
    est = {(a["de"], a["a"]): a["estado"] for a in g["aristas"]}
    assert est[("api", "dominio")] == "declarada"
    assert est[("dominio", "db")] == "declarada"
    assert est[("db", "api")] == "deuda"
    assert est[("api", "db")] == "no declarada"
    assert g["mutuas"] == ["api ↔ db"]
    assert g["sin_asignar"] == 0 and g["solapados"] == 0
    assert g["no_verificados"] == ["web"] and g["no_analizados"] == ["app/roto.py"]


def test_deuda_caducada_y_sugerencia(repo):
    g = S.graph(STD, con_mapa(repo, caduca="2026-01-01"), today=dt.date(2026, 11, 13))
    assert {(a["de"], a["a"]): a["estado"] for a in g["aristas"]}[("db", "api")] == "deuda caducada"
    sug = yaml.safe_load(S.deuda_yaml(g, "2027-03-31"))["deuda"]
    assert {(d["de"], d["a"]) for d in sug} == {("api", "db"), ("db", "api")}


def test_cobertura_y_solapes(repo):
    texto = MAPA.replace("{caduca}", "2027-06-30").replace("rutas: [/tests/]", "rutas: [tests/, /app/api/rutas.py]")
    g = S.graph(STD, con_mapa(repo, texto=texto.replace("  - rutas: [/docs/, /README.md, /.github/]", "  - rutas: [/docs/]")))
    assert g["sin_asignar"] == 2                       # README.md y .github/CODEOWNERS
    assert g["solapados"] == 1                         # app/api/rutas.py en api y pruebas


def test_referencias_invalidas(repo):
    con_mapa(repo, texto=MAPA.replace("{caduca}", "2027-06-30").replace("depende_de: [db]", "depende_de: [nada]"))
    mapa, errs = S.load_map(STD, repo)
    assert mapa is None and any("`nada`" in e for e in errs)


def test_cli_graph(repo, capsys):
    assert cli.main(["segments", "graph", "--path", str(repo)]) == 2          # sin mapa
    con_mapa(repo)
    assert cli.main(["segments", "graph", "--path", str(repo), "--today", "2026-11-13"]) == 0
    out = capsys.readouterr().out
    assert "**(X)**" in out and "(D)" in out
    assert cli.main(["segments", "graph", "--path", str(repo), "--format", "json"]) == 0


def test_layout_src(tmp_path):
    root = tmp_path / "r"
    (root / "src/pkg").mkdir(parents=True)
    (root / "src/pkg/__init__.py").write_text("")
    (root / "src/pkg/a.py").write_text("from pkg import b\n")
    (root / "src/pkg/b.py").write_text("")
    git(root, "init", "-q")
    git(root, "add", "-A")
    files = S.tracked_files(root)
    edges, _ = S.python_imports(root, files, S._raices(root, files, None))
    assert ("src/pkg/a.py", "src/pkg/b.py") in edges


def test_esquema_registrado():
    assert "segments" in STD.schemas


def test_ejemplo_canonico_valido(tmp_path):
    root = tmp_path / "r"
    (root / ".harness").mkdir(parents=True)
    src = Path(__file__).resolve().parents[1] / "examples/fragmentos/segments.yaml"
    (root / ".harness/segments.yaml").write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    mapa, errs = S.load_map(STD, root)
    assert not errs and [s.id for s in mapa.segmentos] == ["api", "dominio", "db", "web", "plataforma"]
