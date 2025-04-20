#core/utils/extract_translations.py
import os
import subprocess
import sys
from pathlib import Path

# Ajuster sys.path pour inclure le répertoire racine
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import BASE_DIR, LOCALE_DIR

# Définir les chemins relatifs
POT_FILE = LOCALE_DIR / "messages.pot"
PO_FILES = [
    LOCALE_DIR / "en" / "LC_MESSAGES" / "messages.po",
    LOCALE_DIR / "fr" / "LC_MESSAGES" / "messages.po",
]

def extract_translations():
    """Extraire les chaînes traduisibles dans messages.pot."""
    print(f"Extraction des chaînes vers {POT_FILE}")
    # Scanner récursivement les fichiers .py dans core/
    core_dir = BASE_DIR / "core"
    python_files = list(core_dir.rglob("*.py"))
    if not python_files:
        raise FileNotFoundError("Aucun fichier .py trouvé dans core/")
    subprocess.run([
        "xgettext",
        "--from-code=UTF-8",
        "-d", "messages",
        "-o", str(POT_FILE),
        "-p", str(LOCALE_DIR),
        *map(str, python_files)
    ], check=True)

def update_po_files():
    """Mettre à jour les fichiers .po à partir de messages.pot."""
    for po_file in PO_FILES:
        print(f"Mise à jour de {po_file}")
        po_file.parent.mkdir(parents=True, exist_ok=True)
        if not po_file.exists():
            # Créer un fichier .po vide
            with open(po_file, "w", encoding="utf-8") as f:
                f.write('msgid ""\nmsgstr ""\n')
        subprocess.run([
            "msgmerge",
            "--update",
            "--backup=none",
            str(po_file),
            str(POT_FILE)
        ], check=True)

if __name__ == "__main__":
    LOCALE_DIR.mkdir(parents=True, exist_ok=True)
    extract_translations()
    update_po_files()
    input()