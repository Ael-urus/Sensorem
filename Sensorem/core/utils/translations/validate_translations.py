import sys
import os
import polib

# Ajuster sys.path pour inclure le répertoire racine du projet
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from .po_utils import POUtils
from .constants import SUPPORTED_LANGS, SOURCE_LANG
from .logger_config import setup_logger

def validate_translations(interactive=False, base_path=None):
    logger = setup_logger("Validator")
    logger.info("Validating translation files...")

    po_utils = POUtils(base_path=base_path)
    all_valid = True
    corrections = []

    for lang in SUPPORTED_LANGS:
        logger.info(f"Validating language: {lang}")
        po = po_utils.load_or_create_po(lang)
        po = po_utils.remove_duplicates(po)

        for entry in po:
            # Vérifier les incohérences dans la langue source
            if lang == SOURCE_LANG and entry.msgstr != entry.msgid:
                # Exceptions pour les noms de langues
                if entry.msgid in ["English", "Français"]:
                    continue
                corrections.append({
                    "lang": lang,
                    "msgid": entry.msgid,
                    "old_msgstr": entry.msgstr,
                    "new_msgstr": entry.msgid,
                    "type": "source_lang_mismatch"
                })
            # Vérifier les entrées non traduites dans les langues non sources
            elif lang != SOURCE_LANG and (entry.msgstr == "" or entry.msgstr == "Need Tr"):
                corrections.append({
                    "lang": lang,
                    "msgid": entry.msgid,
                    "old_msgstr": entry.msgstr,
                    "new_msgstr": "Need Tr",
                    "type": "missing_translation"
                })

        # Vérifier les spécificateurs de format
        format_issues = po_utils.validate_format_specifiers(po)
        if format_issues:
            format_corrections = po_utils.get_format_specifier_corrections(po)
            corrections.extend(format_corrections)

        po_utils.save_po(po, lang)

    if corrections and interactive:
        print("\n=== Proposed Corrections ===")
        for i, correction in enumerate(corrections, 1):
            print(f"Correction {i}:")
            print(f"  Language: {correction['lang']}")
            print(f"  Msgid: {correction['msgid']}")
            print(f"  Old Msgstr: {correction['old_msgstr']}")
            print(f"  New Msgstr: {correction['new_msgstr']}")
            print(f"  Type: {correction['type']}")
            print()

        while True:
            response = input("Apply these corrections? (y/n/all): ").lower()
            if response in ["y", "n", "all"]:
                break
            print("Invalid input. Please enter 'y', 'n', or 'all'.")

        if response == "y":
            for correction in corrections:
                po = po_utils.load_or_create_po(correction["lang"])
                for entry in po:
                    if entry.msgid == correction["msgid"]:
                        entry.msgstr = correction["new_msgstr"]
                        logger.info(f"Applied correction: '{correction['msgid']}' -> '{correction['new_msgstr']}' in {correction['lang']}")
                po_utils.save_po(po, correction["lang"])
        elif response == "n":
            logger.info("Corrections skipped by user.")
            all_valid = False
        elif response == "all":
            logger.info("Applying all corrections without further prompts.")
            for correction in corrections:
                po = po_utils.load_or_create_po(correction["lang"])
                for entry in po:
                    if entry.msgid == correction["msgid"]:
                        entry.msgstr = correction["new_msgstr"]
                        logger.info(f"Applied correction: '{correction['msgid']}' -> '{correction['new_msgstr']}' in {correction['lang']}")
                po_utils.save_po(po, correction["lang"])

    elif corrections:
        logger.info(f"Found {len(corrections)} corrections (non-interactive mode)")
        all_valid = False

    return all_valid, corrections

if __name__ == "__main__":
    valid, corrections = validate_translations(interactive=True)
    if not valid:
        print("Validation completed with issues.")
    elif corrections:
        print("Validation completed with corrections applied.")
    else:
        print("Validation completed successfully with no issues.")