# add_language.py
import os
import sys
import polib

# Ajuster sys.path pour inclure le répertoire racine du projet
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.utils.translations.po_utils import POUtils
from core.utils.translations.constants import SUPPORTED_LANGS, SOURCE_LANG
from core.utils.translations.logger_config import setup_logger

def add_language(lang):
    logger = setup_logger("AddLanguage")
    if lang in SUPPORTED_LANGS:
        logger.warning(f"Language {lang} already exists")
        return False
    SUPPORTED_LANGS.append(lang)
    logger.info(f"Added new language: {lang}")
    po_utils = POUtils()
    po = po_utils.load_or_create_po(lang)
    po_utils.save_po(po, lang)
    update_all_languages()
    return True

def update_all_languages():
    logger = setup_logger("UpdateLanguages")
    po_utils = POUtils()
    logger.info("Updating all languages...")
    source_po = po_utils.load_or_create_po(SOURCE_LANG)
    source_msgids = {entry.msgid: entry.msgstr for entry in source_po}

    for lang in SUPPORTED_LANGS:
        if lang == SOURCE_LANG:
            continue
        po = po_utils.load_or_create_po(lang)
        existing_msgids = {entry.msgid: entry for entry in po}
        new_entries = 0
        updated_entries = 0
        need_translation = 0

        # Ajouter ou mettre à jour les entrées
        for msgid, source_msgstr in source_msgids.items():
            if msgid not in existing_msgids:
                entry = polib.POEntry(msgid=msgid, msgstr="Need Tr")
                po.append(entry)
                new_entries += 1
                need_translation += 1
            else:
                entry = existing_msgids[msgid]
                # Ne pas écraser les traductions existantes sauf si elles sont "Need Tr" ou vides
                if entry.msgstr in ["", "Need Tr"]:
                    if lang != SOURCE_LANG:
                        entry.msgstr = "Need Tr"
                        updated_entries += 1
                        need_translation += 1
                # Ajouter des commentaires pour la traçabilité
                if not entry.occurrences:
                    entry.occurrences = [(f"../{lang}_source", 1)]

        # Supprimer les entrées obsolètes
        po[:] = [entry for entry in po if entry.msgid in source_msgids]

        po_utils.save_po(po, lang)
        logger.info(f"Added {new_entries} new entries and updated {updated_entries} existing entries for language {lang}")
        if need_translation > 0:
            logger.warning(f"{need_translation} entries still need translation in {lang}")

if __name__ == "__main__":
    lang = input("Enter the new language code (e.g., fr): ")
    add_language(lang)