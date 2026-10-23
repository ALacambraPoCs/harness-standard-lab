import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from app import total  # noqa: E402


class TotalTest(unittest.TestCase):
    def test_total(self):
        self.assertEqual(total([(2, 1.5), (1, 3.0)]), 6.0)

    def test_cantidad_negativa(self):
        with self.assertRaisesRegex(ValueError, "línea 2"):
            total([(1, 2.0), (-3, 1.0)])

    def test_precio_negativo(self):
        with self.assertRaisesRegex(ValueError, "línea 2"):
            total([(1, 2.0), (3, -1.0)])


if __name__ == "__main__":
    unittest.main()
