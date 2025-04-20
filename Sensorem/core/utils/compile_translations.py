# compile_translations.py
import subprocess
import sys
from pathlib import Path

# Ajuster sys.path pour inclure le répertoire racine
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import LOCALE_DIR

def compile_translations():
    """Compiler les fichiers .po en fichiers .mo."""
    po_files = [
        LOCALE_DIR / "en" / "LC_MESSAGES" / "messages.po",
        LOCALE_DIR / "fr" / "LC_MESSAGES" / "messages.po",
    ]
    for po_file in po_files:
        if po_file.exists():
            mo_file = po_file.with_suffix(".mo")
            print(f"Compilation de {po_file} vers {mo_file}")
            subprocess.run(["msgfmt", "-o", str(mo_file), str(po_file)], check=True)
        else:
            print(f"Fichier {po_file} introuvable, compilation ignorée")

if __name__ == "__main__":
    compile_translations()