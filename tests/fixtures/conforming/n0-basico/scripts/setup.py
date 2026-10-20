"""Setup idempotente y no interactivo: comprueba la versión de Python."""
import sys

if sys.version_info < (3, 10):
    sys.exit("Se requiere Python >= 3.10")
print("setup ok")
