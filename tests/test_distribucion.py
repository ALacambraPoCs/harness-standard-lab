"""Distribución por copia versionada (ADR-017): harness components add/sync/remove/list y deriva."""
import json
import shutil
from pathlib import Path

import pytest
import yaml

from harness_cli import distribucion as D
from harness_cli.standard import load_standard

ROOT = Path(__file__).resolve().parents[1]
SETTINGS_BASE = ROOT / "template/adapters/claude-code/.claude/settings.json"


@pytest.fixture
def std(tmp_path):
    """Copia del estándar con su catálogo, para poder simular versiones nuevas."""
    s = tmp_path / "estandar"
    for d in ("standard", "schemas", "catalog"):
        shutil.copytree(ROOT / d, s / d)
    return load_standard(s)


@pytest.fixture
def inst(tmp_path):
    r = tmp_path / "inst"
    (r / ".claude").mkdir(parents=True)
    shutil.copy(SETTINGS_BASE, r / ".claude/settings.json")
    return r


def settings(r):
    return json.loads((r / ".claude/settings.json").read_text(encoding="utf-8"))


def bump(std, cid, version, edit=None):
    entry = next((std.root / "catalog").glob(f"*/{cid}/componente.yaml"))
    data = yaml.safe_load(entry.read_text(encoding="utf-8"))
    data["version"] = version
    entry.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    if edit:
        p = entry.parent / edit
        p.write_text(p.read_text(encoding="utf-8") + "\n<!-- cambio -->\n", encoding="utf-8")


def test_add_con_dependencias_y_lock(std, inst):
    log = D.add(inst, std, ["cerrar-tarea"])
    assert log[0].startswith("verificador: instalado") and log[1].startswith("cerrar-tarea: instalado")
    lock = D.leer_lock(inst)
    assert set(lock["componentes"]) == {"verificador", "cerrar-tarea"}
    assert (inst / ".claude/skills/cerrar-tarea/SKILL.md").is_file() and (inst / ".claude/agents/verificador.md").is_file()
    assert all(D.deriva(inst, e) == [] for e in lock["componentes"].values())


def test_add_hook_fusiona_settings_sin_perder_reglas(std, inst):
    antes = settings(inst)
    D.add(inst, std, ["verificar-al-terminar"])
    s = settings(inst)
    assert s["permissions"] == antes["permissions"]
    assert s["hooks"]["Stop"][0]["hooks"][0]["type"] == "command"
    D.remove(inst, std, ["verificar-al-terminar"])
    assert settings(inst) == antes and not (inst / ".claude/hooks/verificar_al_terminar.py").exists()


def test_add_dos_veces_es_idempotente(std, inst):
    D.add(inst, std, ["verificar-al-terminar"])
    s1, l1 = settings(inst), D.leer_lock(inst)
    assert "ya instalado" in D.add(inst, std, ["verificar-al-terminar"])[0]
    assert settings(inst) == s1 and D.leer_lock(inst) == l1


def test_no_sobrescribe_archivo_no_gestionado(std, inst):
    (inst / ".claude/agents").mkdir(parents=True)
    (inst / ".claude/agents/verificador.md").write_text("mío\n")
    with pytest.raises(D.DistribucionError, match="no lo gestiona"):
        D.add(inst, std, ["verificador"])
    assert (inst / ".claude/agents/verificador.md").read_text() == "mío\n"


def test_componente_inexistente(std, inst):
    with pytest.raises(D.DistribucionError, match="no existe en el catálogo"):
        D.add(inst, std, ["no-existe"])


def test_sync_actualiza_si_no_hay_cambios_locales(std, inst):
    D.add(inst, std, ["verificador"])
    bump(std, "verificador", "0.2.0", edit="src/verificador.md")
    assert "actualizado 0.1.0 → 0.2.0" in D.sync(inst, std)[0]
    assert "<!-- cambio -->" in (inst / ".claude/agents/verificador.md").read_text()
    assert D.deriva(inst, D.leer_lock(inst)["componentes"]["verificador"]) == []


def test_sync_se_detiene_con_cambios_locales(std, inst):
    D.add(inst, std, ["verificador"])
    (inst / ".claude/agents/verificador.md").write_text("modificado\n")
    bump(std, "verificador", "0.2.0")
    with pytest.raises(D.DistribucionError, match="cambios locales"):
        D.sync(inst, std)
    assert (inst / ".claude/agents/verificador.md").read_text() == "modificado\n"


def test_sync_al_dia(std, inst):
    D.add(inst, std, ["verificador"])
    assert D.sync(inst, std) == ["verificador 0.1.0: al día"]


def test_remove_protege_modificados_y_dependencias(std, inst):
    D.add(inst, std, ["cerrar-tarea"])
    with pytest.raises(D.DistribucionError, match="lo necesita cerrar-tarea"):
        D.remove(inst, std, ["verificador"])
    (inst / ".claude/skills/cerrar-tarea/SKILL.md").write_text("cambio\n")
    with pytest.raises(D.DistribucionError, match="modificado"):
        D.remove(inst, std, ["cerrar-tarea"])


def test_remove_varios_a_la_vez(std, inst):
    D.add(inst, std, ["cerrar-tarea"])
    D.remove(inst, std, ["cerrar-tarea", "verificador"])
    assert D.leer_lock(inst)["componentes"] == {}


def test_crlf_no_es_deriva(std, inst):
    D.add(inst, std, ["verificador"])
    p = inst / ".claude/agents/verificador.md"
    p.write_bytes(p.read_bytes().replace(b"\n", b"\r\n"))
    assert D.deriva(inst, D.leer_lock(inst)["componentes"]["verificador"]) == []


def test_listado(std, inst):
    D.add(inst, std, ["verificador"])
    bump(std, "verificador", "0.3.0")
    rows = "\n".join(D.listado(inst, std))
    assert "desactualizado (catálogo 0.3.0)" in rows and "cerrar-tarea" in rows and "disponible" in rows


def test_catalogo_viaja_en_el_paquete():
    import tomllib
    cfg = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert cfg["tool"]["hatch"]["build"]["targets"]["wheel"]["force-include"]["catalog"] == "harness_cli/_standard/catalog"
