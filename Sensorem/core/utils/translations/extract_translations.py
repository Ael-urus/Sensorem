# extract_translations.py
import os
import sys
import polib
import re
import logging

# Ajuster sys.path pour inclure le répertoire racine du projet
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from .po_utils import POUtils
from .constants import LOCALE_DIR, PO_FILE, SUPPORTED_LANGS
from .logger_config import setup_logger

logger = setup_logger("ExtractTranslations")


def extract_translations(source_dir, output_file=None):
    """
    Extrait les chaînes de traduction du code source et génère des fichiers PO.

    Args:
        source_dir (str): Répertoire contenant le code source à analyser.
        output_file (str, optional): Non utilisé, gardé pour compatibilité.
                                    Les fichiers PO sont générés en fonction de la config.

    Returns:
        bool: True si l'extraction s'est bien déroulée, False sinon.
    """
    logger.info(f"Extracting translations from {source_dir}")

    try:
        po_utils = POUtils()
        po = polib.POFile()

        # Compteur pour les résultats
        total_strings = 0

        # Logique d'extraction des chaînes
        for root, _, files in os.walk(source_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                            # Recherche des différentes formes de chaînes à traduire
                            patterns = [
                                r'_\(["\'](.*?)["\']\)',  # _("string")
                                r'_lazy\(["\'](.*?)["\']\)',  # _lazy("string")
                                r'gettext\(["\'](.*?)["\']\)',  # gettext("string")
                                r'ngettext\(["\'](.*?)["\']\,',  # ngettext("string", ...)
                                r'pgettext\(["\'].*?["\']\, ["\'](.*?)["\']\)'  # pgettext("context", "string")
                            ]

                            for pattern in patterns:
                                strings = re.findall(pattern, content)
                                for string in strings:
                                    if string and string.strip():  # Ignorer les chaînes vides
                                        entry = polib.POEntry(
                                            msgid=string,
                                            msgstr=""
                                        )
                                        po.append(entry)
                                        total_strings += 1

                    except Exception as e:
                        logger.warning(f"Error processing file {file_path}: {e}")

        # Supprimer les doublons
        po = po_utils.remove_duplicates(po)

        # Enregistrer pour chaque langue supportée
        success = True
        for lang in SUPPORTED_LANGS:
            try:
                # Vérifier si le fichier existe déjà
                po_file_path = PO_FILE(lang)
                po_dir = os.path.dirname(po_file_path)

                # Créer le répertoire si nécessaire
                if not os.path.exists(po_dir):
                    os.makedirs(po_dir)
                    logger.info(f"Created directory: {po_dir}")

                # Si le fichier existe, fusionner avec l'existant
                if os.path.exists(po_file_path):
                    existing_po = polib.pofile(po_file_path)

                    # Mettre à jour les entrées existantes
                    for entry in po:
                        if entry.msgid in [e.msgid for e in existing_po]:
                            continue  # Conserver l'entrée existante
                        existing_po.append(entry)

                    # Enregistrer le fichier fusionné
                    existing_po.save(po_file_path)
                    logger.info(f"Updated PO file for {lang}: {po_file_path}")
                else:
                    # Enregistrer un nouveau fichier
                    po.save(po_file_path)
                    logger.info(f"Created new PO file for {lang}: {po_file_path}")

            except Exception as e:
                logger.error(f"Error saving PO file for {lang}: {e}")
                success = False

        logger.info(f"Extracted {total_strings} unique strings for translation")
        return success

    except Exception as e:
        logger.error(f"Error during translation extraction: {e}")
        return False


if __name__ == "__main__":
    source_dir = project_root
    extract_translations(source_dir)