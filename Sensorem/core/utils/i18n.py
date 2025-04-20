# core/utils/i18n.py

import gettext
import os
import sys
from pathlib import Path

# Ajuster sys.path pour inclure le répertoire racine
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import LOCALE_DIR

# Définir _ comme repli initial
_ = lambda x: x

def set_language(lang):
    """Configurer la langue pour les traductions."""
    global _
    #print(f"Tentative de chargement de la langue : {lang}, LOCALE_DIR : {LOCALE_DIR}")
    mo_file = LOCALE_DIR / lang / "LC_MESSAGES" / "messages.mo"
    #print(f"Fichier .mo existe : {mo_file.exists()}")
    try:
        translation = gettext.translation(
            "messages",
            localedir=LOCALE_DIR,
            languages=[lang],
            fallback=False
        )
        _ = translation.gettext
        globals()["_"] = _  # Mettre à jour la variable globale
        # Mettre à jour _ dans tous les modules chargés
        for module in sys.modules.values():
            if hasattr(module, '_'):
                module._ = _
        catalog = translation._catalog
        #print(f"Langue chargée : {lang}, catalogue :")
        for msgid, msgstr in catalog.items():
            if msgid and msgstr:  # Ignorer l'en-tête vide
                #print(f"  msgid: '{msgid}' -> msgstr: '{msgstr}'")
                pass
    except Exception as e:
        #print(f"Erreur lors du chargement de la langue {lang} : {e}")
        _ = lambda x: x
        globals()["_"] = _

def _f(string, **kwargs):
    """Formater une chaîne traduite."""
    return _(string).format(**kwargs)

# Initialiser avec la langue par défaut
set_language("en")