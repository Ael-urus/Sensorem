#core/views/tabs/logs_tab.py
import customtkinter as ctk
from ...utils.i18n import _

class LogsTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.logs_text = ctk.CTkTextbox(self, height=300)
        self.logs_text.pack(padx=10, pady=10, fill="both", expand=True)

    def refresh(self):
        pass  # Pas de texte à traduire dans logs_text