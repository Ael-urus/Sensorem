import os
import sys
import polib
import re

# Ajuster sys.path pour inclure le répertoire racine du projet
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from .po_utils import POUtils


def extract_translations(source_dir, output_file):
    po_utils = POUtils()
    po = polib.POFile()

    # Logique simplifiée pour l'exemple
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.py'):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Exemple d'extraction de chaînes
                    strings = re.findall(r'_lazy\(["\'](.*?)["\']\)', content)
                    for string in strings:
                        entry = polib.POEntry(
                            msgid=string,
                            msgstr=""
                        )
                        po.append(entry)

    po = po_utils.remove_duplicates(po)
    po_utils.save_po(po, 'en')  # Exemple pour 'en'
    print(f"Translations extracted to {output_file}")


if __name__ == "__main__":
    source_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..')
    output_file = os.path.join(os.path.dirname(__file__), '..', '..', 'locale', 'en', 'LC_MESSAGES', 'messages.po')
    extract_translations(source_dir, output_file)