"""Pruebas del componente despliegue-pages (F5.6-A, D-072). Sin red: la URL se simula."""
import datetime as dt
import importlib.util
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from harness_cli.checker import run_check
from harness_cli.standard import load_standard

SRC = Path(__file__).resolve().parents[1] / "src"
ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "tests" / "fixtures" / "conforming" / "n1-endurecido"

spec = importlib.util.spec_from_file_location("despliegue", SRC / "despliegue.py")
D = importlib.util.module_from_spec(spec)
spec.loader.exec_module(D)


def git(root, *args):
    return subprocess.run(["git", "-c", "user.email=a@x", "-c", "user.name=A", *args], cwd=root, check=True,
                          capture_output=True, text=True).stdout.strip()


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"
    (root / "site/css").mkdir(parents=True)
    (root / "site/index.html").write_text("<h1>v1</h1>", encoding="utf-8")
    (root / "site/css/a.css").write_text("h1{}", encoding="utf-8")
    (root / "src.py").write_text("raise SystemExit('no se ejecuta')", encoding="utf-8")
    git(root, "init", "-q", "-b", "main")
    git(root, "add", "-A")
    git(root, "commit", "-qm", "v1")
    v1 = git(root, "rev-parse", "HEAD")
    (root / "site/index.html").write_text("<h1>v2</h1>", encoding="utf-8")
    git(root, "commit", "-qam", "v2")
    return root, v1, git(root, "rev-parse", "HEAD")


def test_construir_extrae_el_commit_y_escribe_version(repo, tmp_path):
    root, v1, v2 = repo
    out = tmp_path / "_site"
    assert D.construir(str(root), v1, "site", str(out)) == 2
    assert (out / "index.html").read_text() == "<h1>v1</h1>"          # el contenido del commit, no del árbol
    assert (out / "css/a.css").exists() and not (out / "src.py").exists()
    assert (out / "version.txt").read_text().strip() == v1


@pytest.mark.parametrize("prep,error", [
    (lambda r: (r / "site/version.txt").write_text("x"), "su propio version.txt"),
    (lambda r: (r / "site/enlace").symlink_to("/etc/passwd"), None),
])
def test_construir_rechaza_o_ignora(repo, tmp_path, prep, error):
    root, _, _ = repo
    prep(root)
    git(root, "add", "-A")
    git(root, "commit", "-qm", "x")
    sha = git(root, "rev-parse", "HEAD")
    if error:
        with pytest.raises(D.Error, match=error):
            D.construir(str(root), sha, "site", str(tmp_path / "_site"))
    else:
        D.construir(str(root), sha, "site", str(tmp_path / "_site"))
        assert not (tmp_path / "_site/enlace").exists()                 # los enlaces simbólicos no se copian


def test_construir_sin_sitio(repo, tmp_path):
    root, v1, _ = repo
    with pytest.raises(D.Error):
        D.construir(str(root), v1, "no-existe", str(tmp_path / "_site"))
    with pytest.raises(D.Error, match="SHA no válido"):
        D.construir(str(root), "HEAD", "site", str(tmp_path / "_site"))


def test_preparar(repo):
    root, v1, v2 = repo
    url = "https://o.github.io/r/"
    p = D.preparar(str(root), "o/r", "", "refs/heads/main", v2, "", fetch=lambda u: v1)
    assert p == {"objetivo": v2, "anterior": v1, "url": url}
    p = D.preparar(str(root), "o/r", v1, "refs/heads/main", v2, "", fetch=lambda u: v2)   # rollback manual
    assert p["objetivo"] == v1 and p["anterior"] == v2
    assert D.preparar(str(root), "o/r", "", "refs/heads/main", v2, "", fetch=lambda u: None)["anterior"] == ""
    assert D.preparar(str(root), "o/r", "", "refs/heads/main", v2, "", fetch=lambda u: "f" * 40)["anterior"] == ""
    assert D.default_url("O/o.github.io") == "https://o.github.io/"


def test_preparar_rechaza_otra_rama_y_sha_ajeno(repo):
    root, v1, v2 = repo
    with pytest.raises(D.Error, match="rama por defecto"):
        D.preparar(str(root), "o/r", "", "refs/heads/feature", v2, "", fetch=lambda u: None)
    git(root, "switch", "-qc", "otra")
    (root / "site/index.html").write_text("sin revisar", encoding="utf-8")
    git(root, "commit", "-qam", "fuera de main")
    ajeno = git(root, "rev-parse", "HEAD")
    with pytest.raises(D.Error, match="historia de la rama por defecto"):
        D.preparar(str(root), "o/r", ajeno, "refs/heads/main", v2, "", fetch=lambda u: None)
    with pytest.raises(D.Error, match="40 caracteres"):
        D.preparar(str(root), "o/r", "main", "refs/heads/main", v2, "", fetch=lambda u: None)


def test_verificar_reintenta_y_agota():
    vistos = iter([None, "a" * 40, "b" * 40])
    assert D.verificar("u", "b" * 40, 100, 0, fetch=lambda u: next(vistos), sleep=lambda s: None)
    assert not D.verificar("u", "b" * 40, 0, 0, fetch=lambda u: "a" * 40, sleep=lambda s: None)


def test_aviso_distingue_los_casos():
    a = "a" * 40
    assert "revertido" in D.aviso("o/r", "run", "b" * 40, a, "success")
    assert "no se ha podido completar" in D.aviso("o/r", "run", "b" * 40, a, "failure")
    assert "no se ha revertido" in D.aviso("o/r", "run", "b" * 40, "", "skipped")


def test_workflow_permisos_minimos():
    wf = yaml.safe_load((SRC / "despliegue-pages.yml").read_text(encoding="utf-8"))
    assert wf["permissions"] == {"contents": "read"}
    on = wf.get("on", wf.get(True))
    assert set(on) == {"push", "workflow_dispatch"} and on["push"]["branches"] == ["main"]
    assert wf["concurrency"]["cancel-in-progress"] is False
    for name, job in wf["jobs"].items():
        perms = job["permissions"]
        writes = {k for k, v in perms.items() if v == "write"}
        if name in ("desplegar", "revertir"):
            assert writes == {"pages", "id-token"} and job["environment"]["name"] == "github-pages"
            assert [s["uses"].split("@")[0] for s in job["steps"]] == ["actions/deploy-pages"]
        elif name == "avisar":
            assert writes == {"issues"}
        else:
            assert writes == set(), name
    texto = (SRC / "despliegue-pages.yml").read_text(encoding="utf-8")
    assert "${{ inputs.sha }}" not in texto.split("run:")[1:] and "SHA_MANUAL: ${{ inputs.sha }}" in texto
    assert texto.count("python3 -I base/.harness/despliegue/despliegue.py") == 6


def test_workflow_cumple_las_reglas_de_ci(tmp_path):
    root = tmp_path / "repo"
    shutil.copytree(BASE, root)
    m = root / ".harness/manifest.yaml"
    m.write_text(m.read_text(encoding="utf-8").replace("version: 0.5.0", "version: 0.9.0"), encoding="utf-8")
    shutil.copy(SRC / "despliegue-pages.yml", root / ".github/workflows/despliegue-pages.yml")
    reglas = {"ci.parseable", "ci.no-pr-target", "ci.no-untrusted-interpolation", "ci.permissions",
              "ci.model-readonly", "ci.pinned", "ci.merge-group"}
    res = run_check(root, standard=load_standard(), today=dt.date(2026, 10, 28), only_rules=reglas)
    assert [(f.rule, f.message) for f in res.findings if f.status == "fail"] == []


def test_runbook_cumple_hs_ci_009(tmp_path):
    root = tmp_path / "repo"
    shutil.copytree(BASE, root)
    m = root / ".harness/manifest.yaml"
    m.write_text(m.read_text(encoding="utf-8").replace("version: 0.5.0", "version: 0.9.0")
                 + "plataforma:\n  entorno_despliegue: github-pages\n", encoding="utf-8")
    regla = {"core.runbooks.rollback"}
    res = run_check(root, standard=load_standard(), today=dt.date(2026, 10, 28), only_rules=regla)
    assert [f.rule for f in res.findings if f.status == "fail"] == ["core.runbooks.rollback"]
    (root / "docs/runbooks").mkdir(parents=True)
    shutil.copy(SRC / "RUNBOOK-rollback.md", root / "docs/runbooks/rollback-pages.md")
    res = run_check(root, standard=load_standard(), today=dt.date(2026, 10, 28), only_rules=regla)
    assert [f for f in res.findings if f.status == "fail"] == []
