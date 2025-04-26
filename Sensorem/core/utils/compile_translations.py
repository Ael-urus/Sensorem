#!/usr/bin/env python3
# compile_translations.py
"""
Script pour compiler les fichiers de traduction .po en .mo et exécuter les tests.
Supprime les anciens fichiers .mo avant compilation pour éviter les conflits.
"""

import os
import sys
import subprocess
from pathlib import Path

# Ajuster sys.path pour inclure le répertoire racine
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Vérifier l'existence du répertoire core/
if not (BASE_DIR / 'core').exists():
    print(f"Erreur : Répertoire 'core/' introuvable dans {BASE_DIR}")
    sys.exit(1)

try:
    import logging
    logger = logging.getLogger('Sensorem')
except ImportError as e:
    print(f"Erreur : Impossible d'importer core.utils.logger : {e}")
    sys.exit(1)

LOCALE_DIR = BASE_DIR / "core" / "locale"
TEST_FILE = BASE_DIR / "tests" / "test_gettext.py"

def remove_old_mo_files():
    """Supprime les anciens fichiers .mo pour éviter les conflits."""
    try:
        for lang_dir in LOCALE_DIR.iterdir():
            if lang_dir.is_dir():
                for lc_dir in [lang_dir / 'LC_MESSAGES', lang_dir / 'LC_messages']:
                    if lc_dir.exists():
                        mo_file = lc_dir / 'messages.mo'
                        if mo_file.exists():
                            mo_file.unlink()
                            logger.info(f"Ancien fichier supprimé : {mo_file}")
    except Exception as e:
        logger.error(f"Erreur lors de la suppression des anciens fichiers .mo : {e}")
        print(f"Erreur : Impossible de supprimer les anciens fichiers .mo : {e}")
        sys.exit(1)

def compile_translations():
    """Compile les fichiers .po en .mo pour chaque langue."""
    if not LOCALE_DIR.exists():
        logger.error(f"Répertoire des traductions non trouvé : {LOCALE_DIR}")
        print(f"Erreur : Répertoire des traductions non trouvé : {LOCALE_DIR}")
        sys.exit(1)

    try:
        for lang_dir in LOCALE_DIR.iterdir():
            if lang_dir.is_dir():
                for lc_dir in [lang_dir / 'LC_MESSAGES', lang_dir / 'LC_messages']:
                    if lc_dir.exists():
                        po_file = lc_dir / 'messages.po'
                        mo_file = lc_dir / 'messages.mo'
                        if po_file.exists():
                            cmd = ["msgfmt", str(po_file), "-o", str(mo_file)]
                            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
                            if result.returncode == 0:
                                logger.info(f"Compilation réussie : {po_file} -> {mo_file}")
                                print(f"Compilation de {po_file} vers {mo_file}")
                            else:
                                logger.error(f"Erreur lors de la compilation de {po_file} : {result.stderr}")
                                print(f"Erreur : Échec de la compilation de {po_file} : {result.stderr}")
                                sys.exit(1)
    except Exception as e:
        logger.error(f"Erreur lors de la compilation des traductions : {e}")
        print(f"Erreur : Impossible de compiler les traductions : {e}")
        sys.exit(1)

def run_tests():
    """Exécute les tests de traduction."""
    if not TEST_FILE.exists():
        logger.warning(f"Fichier de test non trouvé : {TEST_FILE}. Tests ignorés.")
        print(f"Avertissement : Fichier de test non trouvé : {TEST_FILE}. Tests ignorés.")
        return

    try:
        result = subprocess.run([sys.executable, "-m", "unittest", str(TEST_FILE)], capture_output=True, text=True, check=False)
        if result.returncode == 0:
            logger.info("Tests de traduction réussis.")
            print("Succès : Tests de traduction terminés sans erreur.")
        else:
            logger.error(f"Échec des tests de traduction : {result.stdout}\n{result.stderr}")
            print(f"Erreur : Échec des tests de traduction : {result.stdout}\n{result.stderr}")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution des tests : {e}")
        print(f"Erreur : Impossible d'exécuter les tests : {e}")
        sys.exit(1)

def main():
    print("Compilation des traductions...")
    remove_old_mo_files()
    compile_translations()
    print("Exécution des tests de traduction...")
    run_tests()
    print("Succès : Compilation et tests des traductions terminés sans erreur.")

if __name__ == "__main__":
    main()