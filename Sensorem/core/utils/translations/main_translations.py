# main_translations.py
import logging
import sys
import os
import time
import argparse

# Ajuster sys.path pour inclure le répertoire racine du projet
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.utils.translations.extract_translations import extract_translations
from core.utils.translations.validate_translations import validate_translations
from core.utils.translations.compile_translations import compile_translations
from core.utils.translations.add_language import add_language, update_all_languages
from core.utils.translations.logger_config import setup_logger
from core.utils.translations.constants import SOURCE_DIR, LOCALE_DIR, SUPPORTED_LANGS


def main():
    # Parser pour les arguments en ligne de commande
    parser = argparse.ArgumentParser(description="Outil de gestion des traductions pour Sensorem")
    parser.add_argument('--extract', action='store_true', help="Extraire les chaînes à traduire")
    parser.add_argument('--validate', action='store_true', help="Valider les fichiers de traduction")
    parser.add_argument('--compile', action='store_true', help="Compiler les traductions en fichiers MO")
    parser.add_argument('--add-lang', metavar='LANG', help="Ajouter une nouvelle langue (ex: es)")
    parser.add_argument('--update', action='store_true', help="Mettre à jour toutes les langues")
    parser.add_argument('--check', action='store_true',
                        help="Vérifier les traductions et résumer les corrections nécessaires")
    parser.add_argument('--all', action='store_true',
                        help="Exécuter toutes les étapes (extract, validate, compile, update)")
    parser.add_argument('--verbose', '-v', action='count', default=0, help="Augmenter la verbosité des logs")
    parser.add_argument('--source-dir', metavar='DIR', default=SOURCE_DIR,
                        help=f"Répertoire source (défaut: {SOURCE_DIR})")

    args = parser.parse_args()

    # Configurer le logger
    logger = setup_logger("MainTranslations", verbose_level=args.verbose)
    logger.info("Starting translation management...")

    # Si aucun argument n'est spécifié, afficher le menu interactif
    if not any([args.extract, args.validate, args.compile, args.add_lang, args.update, args.check, args.all]):
        interactive_menu(args.source_dir, logger)
        return

    # Traiter les arguments de la ligne de commande
    if args.all:
        start_time = time.time()
        success = run_all(args.source_dir)
        elapsed_time = time.time() - start_time
        logger.info(f"All operations completed in {elapsed_time:.2f} seconds")
        sys.exit(0 if success else 1)

    # Exécuter les opérations individuelles
    if args.extract:
        success = extract_translations(args.source_dir)
        if not success:
            sys.exit(1)

    if args.validate:
        success = validate_translations(interactive=True)
        if not success:
            sys.exit(1)

    if args.compile:
        success = compile_translations()
        if not success:
            sys.exit(1)

    if args.add_lang:
        success = add_language(args.add_lang)
        if not success:
            sys.exit(1)

    if args.update:
        success = update_all_languages()
        if not success:
            sys.exit(1)

    if args.check:
        check_translations()


def interactive_menu(source_dir, logger):
    """Affiche un menu interactif pour la gestion des traductions."""
    actions = {
        "1": ("extract", lambda: extract_translations(source_dir),
              "Extract translation keys from source code"),
        "2": ("validate", lambda: validate_translations(interactive=True),
              "Validate translation files"),
        "3": ("compile", compile_translations,
              "Compile translations to MO files"),
        "4": ("add-lang", lambda: add_language(input("Enter the new language code (e.g., fr): ")),
              "Add a new language"),
        "5": ("update-langs", update_all_languages,
              "Update all languages"),
        "6": ("all", lambda: run_all(source_dir),
              "Run all steps (extract, validate, compile, update-langs)"),
        "7": ("exit", lambda: logger.info("Exiting translation management"),
              "Exit the program"),
        "8": ("stats", show_translation_stats,
              "Show translation statistics"),
        "9": ("check", check_translations,
              "Check translations and summarize corrections needed")
    }

    while True:
        print("\n=== Translation Management Menu ===")
        print("Available actions:")
        for key, (_, _, desc) in sorted(actions.items()):
            print(f"{key}. {desc}")
        choice = input("Enter the number of the action to perform: ").strip()

        if choice in actions:
            action_name, action_func, _ = actions[choice]
            logger.info(f"Executing action: {action_name}")
            try:
                if action_name == "exit":
                    action_func()
                    break
                start_time = time.time()
                result = action_func()
                elapsed_time = time.time() - start_time
                logger.info(f"Action '{action_name}' completed in {elapsed_time:.2f} seconds")
                if result is False:  # Si le résultat est explicitement False
                    logger.warning(f"Action '{action_name}' reported failure")
            except Exception as e:
                logger.error(f"Error during {action_name}: {e}")
        else:
            logger.warning("Invalid choice. Please select a valid option.")


def run_all(source_dir):
    """Exécute toutes les étapes du processus de traduction."""
    logger = setup_logger("MainTranslations")
    logger.info("Running all steps...")
    success = True

    try:
        # Étape 1: Extraction
        if not extract_translations(source_dir):
            logger.error("Failed at extraction step")
            success = False

        # Étape 2: Validation (non interactive en mode batch)
        valid, _ = validate_translations(interactive=False)
        if not valid:
            logger.warning("Validation reported issues, but continuing with next steps")

        # Étape 3: Compilation
        if not compile_translations():
            logger.error("Failed at compilation step")
            success = False

        # Étape 4: Mise à jour
        if not update_all_languages():
            logger.error("Failed at update step")
            success = False

        if success:
            logger.info("All steps completed successfully")
        else:
            logger.warning("Some steps failed, see above for details")

        return success

    except Exception as e:
        logger.error(f"Error during run_all: {e}")
        return False


def check_translations():
    """Vérifie les traductions et résume les corrections nécessaires."""
    logger = setup_logger("CheckTranslations")
    # Réduire la verbosité des logs
    logging.getLogger("POUtils").setLevel(logging.WARNING)
    logging.getLogger("Validator").setLevel(logging.WARNING)
    logger.info("Checking translations for issues...")

    valid, corrections = validate_translations(interactive=False)

    if not corrections:
        print("\n=== Translation Check Summary ===")
        print("No issues found. All translations are valid.")
    else:
        print("\n=== Translation Check Summary ===")
        print(f"Found {len(corrections)} issues requiring corrections:")
        for i, correction in enumerate(corrections, 1):
            print(f"\nIssue {i}:")
            print(f"  Language: {correction['lang']}")
            print(f"  Msgid: {correction['msgid']}")
            print(f"  Current Msgstr: {correction['old_msgstr']}")
            print(f"  Suggested Msgstr: {correction['new_msgstr']}")
            print(f"  Issue Type: {correction['type']}")
        print("\nTo apply these corrections, run option 2 (validate) or 6 (all).")


def show_translation_stats():
    """Affiche des statistiques sur l'état des traductions."""
    import polib
    from core.utils.translations.constants import PO_FILE, SUPPORTED_LANGS

    print("\n=== Translation Statistics ===")
    print(f"Supported languages: {', '.join(SUPPORTED_LANGS)}")

    stats = {}
    total_strings = 0

    # Collect statistics for each language
    for lang in SUPPORTED_LANGS:
        po_path = PO_FILE(lang)
        if os.path.exists(po_path):
            try:
                po = polib.pofile(po_path)
                total = len(po)
                translated = len(po.translated_entries())
                fuzzy = len(po.fuzzy_entries())
                untranslated = len(po.untranslated_entries())

                if total > total_strings:
                    total_strings = total

                stats[lang] = {
                    'total': total,
                    'translated': translated,
                    'fuzzy': fuzzy,
                    'untranslated': untranslated,
                    'percent': (translated / total * 100) if total > 0 else 0
                }
            except Exception as e:
                print(f"Error reading {po_path}: {e}")

    # Display statistics table
    print("\nLanguage   Total    Translated    Fuzzy    Untranslated    Completion")
    print("-------------------------------------------------------------------------")
    for lang in sorted(stats.keys()):
        stat = stats[lang]
        print(
            f"{lang:<9}  {stat['total']:<8}  {stat['translated']:<12}  {stat['fuzzy']:<8}  {stat['untranslated']:<14}  {stat['percent']:.1f}%")

    print(f"\nTotal unique strings across all languages: {total_strings}")

    return True


if __name__ == "__main__":
    main()