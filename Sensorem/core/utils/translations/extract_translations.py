# extract_translations.py
import os
import sys
import polib
import re
import logging
from concurrent.futures import ThreadPoolExecutor

# Ajuster sys.path pour inclure le répertoire racine du projet
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from .po_utils import POUtils
from .constants import LOCALE_DIR, PO_FILE, SUPPORTED_LANGS, SOURCE_DIR
from .logger_config import setup_logger

logger = setup_logger("ExtractTranslations")

# Modèles de recherche pour les chaînes à traduire
TRANSLATION_PATTERNS = [
    r'_\(["\'](.*?)["\']\)',  # _("string")
    r'_lazy\(["\'](.*?)["\']\)',  # _lazy("string")
    r'gettext\(["\'](.*?)["\']\)',  # gettext("string")
    r'ngettext\(["\'](.*?)["\']\,',  # ngettext("string", ...)
    r'pgettext\(["\'].*?["\']\, ["\'](.*?)["\']\)',  # pgettext("context", "string")
    r'_\(f["\'](.*?)["\'].*?\)',  # _(f"string {var}")
    r'_tr\(["\'](.*?)["\']\)',  # _tr("string")
    r'translate\(["\'](.*?)["\']\)',  # translate("string")
]

# Précompilation des expressions régulières pour de meilleures performances
COMPILED_PATTERNS = [re.compile(pattern) for pattern in TRANSLATION_PATTERNS]


def process_file(file_path):
    """Traite un fichier pour en extraire les chaînes à traduire."""
    extracted_strings = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

            # Utiliser les patterns précompilés
            for pattern in COMPILED_PATTERNS:
                strings = pattern.findall(content)
                for string in strings:
                    if string and string.strip():  # Ignorer les chaînes vides
                        extracted_strings.append(string)

    except Exception as e:
        logger.warning(f"Error processing file {file_path}: {e}")

    return extracted_strings


def extract_translations(source_dir=SOURCE_DIR, output_file=None):
    """
    Extrait les chaînes de traduction du code source et génère des fichiers PO.

    Args:
        source_dir (str, optional): Répertoire contenant le code source à analyser.
                                    Par défaut, utilise SOURCE_DIR.
        output_file (str, optional): Non utilisé, gardé pour compatibilité.
                                    Les fichiers PO sont générés en fonction de la config.

    Returns:
        bool: True si l'extraction s'est bien déroulée, False sinon.
    """
    logger.info(f"Extracting translations from {source_dir}")

    try:
        po_utils = POUtils()
        po = polib.POFile()
        po.metadata = {
            'Project-Id-Version': 'Sensorem',
            'POT-Creation-Date': polib.POFile().metadata['POT-Creation-Date'],
            'Language': '',
            'MIME-Version': '1.0',
            'Content-Type': 'text/plain; charset=utf-8',
            'Content-Transfer-Encoding': '8bit',
        }

        # Collecter tous les fichiers Python
        python_files = []
        for root, _, files in os.walk(source_dir):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))

        if not python_files:
            logger.warning(f"No Python files found in {source_dir}")
            return False

        logger.info(f"Found {len(python_files)} Python files to process")

        # Traitement parallèle des fichiers pour de meilleures performances
        all_strings = []
        with ThreadPoolExecutor(max_workers=min(10, os.cpu_count() or 4)) as executor:
            results = list(executor.map(process_file, python_files))
            for strings in results:
                all_strings.extend(strings)

        # Créer les entrées PO
        for string in set(all_strings):  # Utiliser un set pour éliminer les doublons
            entry = polib.POEntry(
                msgid=string,
                msgstr=""
            )
            po.append(entry)

        # Supprimer les doublons (peut-être redondant avec le set, mais vérifie aussi d'autres attributs)
        po = po_utils.remove_duplicates(po)

        # Sauvegarder le fichier POT principal (template)
        pot_file = os.path.join(LOCALE_DIR, "messages.pot")
        pot_dir = os.path.dirname(pot_file)
        if not os.path.exists(pot_dir):
            os.makedirs(pot_dir)
        po.save(pot_file)
        logger.info(f"Created POT template file: {pot_file}")

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

                    # Mettre à jour les entrées existantes et conserver les traductions
                    updated_po = polib.POFile()
                    updated_po.metadata = existing_po.metadata

                    # Dictionnaire des entrées existantes pour recherche rapide
                    existing_dict = {entry.msgid: entry for entry in existing_po}

                    # Ajouter toutes les entrées du nouveau fichier POT
                    for entry in po:
                        if entry.msgid in existing_dict:
                            # Conserver la traduction existante
                            new_entry = polib.POEntry(
                                msgid=entry.msgid,
                                msgstr=existing_dict[entry.msgid].msgstr,
                                obsolete=False  # Marquer comme non obsolète
                            )
                            updated_po.append(new_entry)
                        else:
                            # Ajouter une nouvelle entrée sans traduction
                            updated_po.append(entry)

                    # Enregistrer le fichier fusionné
                    updated_po.save(po_file_path)
                    logger.info(f"Updated PO file for {lang}: {po_file_path}")
                else:
                    # Créer un nouveau fichier PO à partir du POT
                    new_po = polib.POFile()
                    new_po.metadata = po.metadata.copy()
                    new_po.metadata['Language'] = lang

                    # Copier toutes les entrées
                    for entry in po:
                        new_po.append(entry)

                    # Enregistrer un nouveau fichier
                    new_po.save(po_file_path)
                    logger.info(f"Created new PO file for {lang}: {po_file_path}")

            except Exception as e:
                logger.error(f"Error saving PO file for {lang}: {e}")
                success = False

        logger.info(f"Extracted {len(po)} unique strings for translation")
        return success

    except Exception as e:
        logger.error(f"Error during translation extraction: {e}")
        return False


if __name__ == "__main__":
    extract_translations()