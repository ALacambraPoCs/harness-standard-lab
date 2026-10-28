"""Genera site/index.html (sitio estático que despliega `despliegue-pages`, F5.6).

El despliegue no ejecuta código del commit: el HTML se genera aquí y se versiona. `tests/test_sitio.py`
falla si el archivo versionado no coincide con lo que genera este script (`check` lo detecta).
Uso: python3 scripts/generar_sitio.py [--check]
"""
import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from app import total  # noqa: E402

LINEAS = [(2, 1.5), (1, 3.0)]
DESCUENTO = 10


def generar() -> str:
    filas = "\n".join(f"      <tr><td>{q}</td><td>{p:.2f}</td></tr>" for q, p in LINEAS)
    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>harness-example-greenfield</title>
</head>
<body>
  <h1>harness-example-greenfield</h1>
  <p>Ejemplo de <code>total()</code> con descuento del {DESCUENTO} %:</p>
  <table>
    <thead><tr><th>Cantidad</th><th>Precio</th></tr></thead>
    <tbody>
{filas}
    </tbody>
  </table>
  <p>Total: <strong id="total">{html.escape(f"{total(LINEAS, DESCUENTO):.2f}")}</strong></p>
  <p>Versión desplegada: <code id="version">(cargando)</code></p>
  <script>
    fetch("version.txt", {{cache: "no-store"}}).then(r => r.text())
      .then(t => {{ document.getElementById("version").textContent = t.trim().slice(0, 12); }})
      .catch(() => {{ document.getElementById("version").textContent = "desconocida"; }});
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    destino = ROOT / "site" / "index.html"
    if "--check" in sys.argv:
        sys.exit(0 if destino.read_text(encoding="utf-8") == generar() else "site/index.html no está al día: ejecuta scripts/generar_sitio.py")
    destino.parent.mkdir(exist_ok=True)
    destino.write_text(generar(), encoding="utf-8")
    print(f"escrito {destino.relative_to(ROOT)}")
