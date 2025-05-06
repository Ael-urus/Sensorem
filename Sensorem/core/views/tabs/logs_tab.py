# core/views/tabs/logs_tab.py
import customtkinter as ctk
import logging
from tkinter import END
from core.utils.i18n import _

class LogHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    def emit(self, record):
        try:
            if self.text_widget.winfo_exists():  # Vérifier si le widget existe
                msg = self.format(record)
                self.text_widget.configure(state="normal")
                self.text_widget.insert(END, msg + "\n")
                self.text_widget.configure(state="disabled")
                self.text_widget.see(END)
        except Exception as e:
            print(f"Erreur dans LogHandler: {str(e)}")  # Log temporaire pour le débogage

class LogsTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.log_handler = None
        self.create_widgets()
        self.place_widgets()
        self.setup_logging()
        logging.getLogger('Sensorem').info("Initialisation of LogsTab")

    def create_widgets(self):
        self.log_text = ctk.CTkTextbox(self, height=400, state="disabled")
        self.clear_button = ctk.CTkButton(self, text=_("Clear Logs"), command=self.clear_logs)

    def place_widgets(self):
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.clear_button.pack(fill="x", padx=5, pady=5)

    def setup_logging(self):
        logger = logging.getLogger('Sensorem')
        # Supprimer tous les LogHandler existants pour éviter les doublons
        for handler in logger.handlers[:]:
            if isinstance(handler, LogHandler):
                logger.removeHandler(handler)
        self.log_handler = LogHandler(self.log_text)
        self.log_handler.setLevel(logging.DEBUG)
        logger.addHandler(self.log_handler)
        logger.debug("Logging initialisé pour LogsTab")
        logger.info("Configuration du logging pour LogsTab (2025-04-26)")

    def disable_logging(self):
        logger = logging.getLogger('Sensorem')
        if self.log_handler:
            logger.removeHandler(self.log_handler)
            self.log_handler = None
        # Supprimer tous les LogHandler restants pour plus de sûreté
        for handler in logger.handlers[:]:
            if isinstance(handler, LogHandler):
                logger.removeHandler(handler)
        logger.debug("Logging to textbox disabled")

    def enable_logging(self):
        self.setup_logging()

    def clear_logs(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", END)
        self.log_text.configure(state="disabled")
        logging.getLogger('Sensorem').info(_("Logs erased"))

    def refresh(self):
        self.clear_button.configure(text=_("Clear Logs"))
        logging.getLogger('Sensorem').info(_("LogsTab refreshed"))