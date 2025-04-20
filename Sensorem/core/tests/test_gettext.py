# core/tests/test_gettext.py
import os
import sys

# Ajouter le répertoire racine au PYTHONPATH
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.utils.i18n import set_language

# Tester pour le français
set_language("fr")
from core.utils.i18n import _  # Importer _ après set_language
print("Français:")
print(f"Sensorem - Sensor Signal Processing -> {_('Sensorem - Sensor Signal Processing')}")
print(f"Processing -> {_('Processing')}")
print(f"Database -> {_('Database')}")

# Tester pour l'anglais
set_language("en")
from core.utils.i18n import _  # Importer _ après set_language
print("\nAnglais:")
print(f"Sensorem - Sensor Signal Processing -> {_('Sensorem - Sensor Signal Processing')}")
print(f"Processing -> {_('Processing')}")
print(f"Database -> {_('Database')}")