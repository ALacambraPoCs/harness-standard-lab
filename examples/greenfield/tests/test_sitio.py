import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import generar_sitio  # noqa: E402


class SitioTest(unittest.TestCase):
    def test_sitio_al_dia(self):
        self.assertEqual((ROOT / "site" / "index.html").read_text(encoding="utf-8"), generar_sitio.generar(),
                         "site/index.html no está al día: ejecuta python3 scripts/generar_sitio.py")

    def test_sin_version_propia(self):
        self.assertFalse((ROOT / "site" / "version.txt").exists(), "version.txt lo escribe el despliegue")


if __name__ == "__main__":
    unittest.main()
