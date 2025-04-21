# core/utils/logger.py
import logging
from datetime import datetime

class TextboxHandler(logging.Handler):
    def __init__(self, textbox):
        super().__init__()
        self.textbox = textbox
        self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    def emit(self, record):
        if self.textbox is None or not self.textbox.winfo_exists():
            return
        try:
            msg = self.format(record)
            self.textbox.configure(state="normal")
            self.textbox.insert("end", msg + "\n")
            self.textbox.configure(state="disabled")
            self.textbox.see("end")
        except Exception:
            pass

def setup_ui_logger(textbox):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    textbox_handler = TextboxHandler(textbox)
    logger.addHandler(textbox_handler)
    return logger

logger = logging.getLogger()