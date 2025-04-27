# main_translations.py
import logging
import sys
import os

# Ajuster sys.path pour inclure le répertoire racine du projet
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.utils.translations.extract_translations import extract_translations
from core.utils.translations.validate_translations import validate_translations
from core.utils.translations.compile_translations import compile_translations
from core.utils.translations.add_language import add_language, update_all_languages
from core.utils.translations.logger_config import setup_logger


def main():
    logger = setup_logger("MainTranslations")
    logger.info("Starting translation management...")

    actions = {
        "1": ("extract", extract_translations, "Extract translation keys from source code"),
        "2": ("validate", lambda: validate_translations(interactive=True), "Validate translation files"),
        "3": ("compile", compile_translations, "Compile translations to MO files"),
        "4": ("add-lang", lambda: add_language(input("Enter the new language code (e.g., fr): ")),
              "Add a new language"),
        "5": ("update-langs", update_all_languages, "Update all languages"),
        "6": ("all", run_all, "Run all steps (extract, validate, compile, update-langs)"),
        "7": ("exit", lambda: logger.info("Exiting translation management"), "Exit the program"),
        "9": ("check", check_translations, "Check translations and summarize corrections needed")
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
                action_func()
            except Exception as e:
                logger.error(f"Error during {action_name}: {e}")
        else:
            logger.warning("Invalid choice. Please select a valid option.")


def run_all():
    logger = setup_logger("MainTranslations")
    logger.info("Running all steps...")
    try:
        extract_translations()
        validate_translations(interactive=True)
        compile_translations()
        update_all_languages()
    except Exception as e:
        logger.error(f"Error during run_all: {e}")


def check_translations():
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


if __name__ == "__main__":
    main()