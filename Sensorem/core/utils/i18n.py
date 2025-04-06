# i18n.py
import gettext
from pathlib import Path
from typing import Callable, List


class Translator:
    def __init__(self):
        self.locale_dir = Path(__file__).parent.parent / 'locale'
        self.language = 'en'  # Langue par défaut
        self.observers: List[Callable[[str], None]] = []
        self.translator = gettext.translation(
            'messages',
            localedir=self.locale_dir,
            languages=[self.language],
            fallback=True
        )
        self.translator.install()

    def set_language(self, lang_code: str):
        """Change la langue de l'application et notifie les observateurs"""
        if self.language == lang_code:
            return  # Évite le rechargement inutile si la langue est la même

        self.language = lang_code
        self.translator = gettext.translation(
            'messages',
            localedir=self.locale_dir,
            languages=[lang_code],
            fallback=True
        )
        self.translator.install()

        # Notifier tous les observateurs du changement de langue
        for observer in self.observers:
            observer(lang_code)

    def add_observer(self, callback: Callable[[str], None]):
        """Ajoute un observateur qui sera notifié lors d'un changement de langue"""
        if callback not in self.observers:
            self.observers.append(callback)

    def remove_observer(self, callback: Callable[[str], None]):
        """Supprime un observateur"""
        if callback in self.observers:
            self.observers.remove(callback)

    def gettext(self, message: str) -> str:
        """Traduit un message"""
        return self.translator.gettext(message)

    def ngettext(self, singular: str, plural: str, n: int) -> str:
        """Traduit avec gestion du pluriel"""
        return self.translator.ngettext(singular, plural, n)

    def format(self, message: str, *args, **kwargs):
        """Traduit et formate un message avec des arguments"""
        translated = self.gettext(message)
        if args or kwargs:
            return translated.format(*args, **kwargs)
        return translated


# Instance globale
translator = Translator()
_ = translator.gettext


# Fonction formatée pour standardiser le formatage
def _f(message: str, *args, **kwargs):
    """Traduit et formate un message avec des arguments"""
    return translator.format(message, *args, **kwargs)