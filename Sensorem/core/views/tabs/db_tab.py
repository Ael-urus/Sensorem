# core/views/tabs/db_tab.py
import customtkinter as ctk
from ...utils.i18n import _

class DatabaseTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.label = ctk.CTkLabel(self, text=_("Welcome to the Database tab"))
        self.label.pack(pady=20)

    def refresh(self):
        self.label.configure(text=_("Welcome to the Database tab"))