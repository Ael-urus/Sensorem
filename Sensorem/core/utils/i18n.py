# core/utils/i18n.py
import gettext
import os
import sys
from pathlib import Path
import importlib
import logging
logger = logging.getLogger('Sensorem')

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import LOCALE_DIR

_ = lambda x: x

def set_language(lang):
    """Configurer la langue pour les traductions."""
    global _
    mo_file = LOCALE_DIR / lang / "LC_MESSAGES" / "messages.mo"
    try:
        translation = gettext.translation(
            "messages",
            localedir=LOCALE_DIR,
            languages=[lang],
            fallback=False
        )
        _ = translation.gettext
        globals()["_"] = _
        for module in sys.modules.values():
            if hasattr(module, '_'):
                module._ = _
        for module_name in ["core.views.tabs.processing_tab", "core.controllers.main_controller"]:
            if module_name in sys.modules:
                logger.debug(f"Rechargement du module : {module_name}")
                importlib.reload(sys.modules[module_name])
        catalog = translation._catalog
        logger.debug(f"Langue chargée : {lang}, traductions disponibles : {list(catalog.keys())}")
        logger.debug(f"Test de traduction : 'Event triggered: selection' -> {_('Event triggered: selection')}")
    except Exception as e:
        logger.error(f"Erreur lors du chargement de la langue {lang} : {e}")
        _ = lambda x: x
        globals()["_"] = _

def _f(string, **kwargs):
    """Formater une chaîne traduite."""
    return _(string).format(**kwargs)

set_language("fr")