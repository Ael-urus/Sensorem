# core/utils/logger.py
import logging

logger = logging.getLogger("SensoremUI")
logger.setLevel(logging.INFO)

class TextboxHandler(logging.Handler):
    def __init__(self, textbox):
        super().__init__()
        self.textbox = textbox

    def emit(self, record):
        msg = self.format(record)
        self.textbox.insert("end", msg + "\n")
        self.textbox.see("end")

def setup_ui_logger(textbox):
    """Configurer le logger pour écrire dans la boîte de texte."""
    handler = TextboxHandler(textbox)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.handlers = []  # Supprimer les anciens handlers
    logger.addHandler(handler)