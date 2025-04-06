import gettext
from pathlib import Path

class Translator:
    def __init__(self):
        self.locale_dir = Path(__file__).parent.parent / 'locale'
        self.language = 'en'  # Langue par défaut
        self.translator = gettext.translation(
            'messages',
            localedir=self.locale_dir,
            languages=[self.language],
            fallback=True
        )
        self.translator.install()

    def set_language(self, lang_code: str):
        """Change la langue de l'application"""
        self.language = lang_code
        self.translator = gettext.translation(
            'messages',
            localedir=self.locale_dir,
            languages=[lang_code],
            fallback=True
        )
        self.translator.install()

    def gettext(self, message: str) -> str:
        """Traduit un message"""
        return self.translator.gettext(message)

    def ngettext(self, singular: str, plural: str, n: int) -> str:
        """Traduit avec gestion du pluriel"""
        return self.translator.ngettext(singular, plural, n)

# Instance globale
translator = Translator()
_ = translator.gettext