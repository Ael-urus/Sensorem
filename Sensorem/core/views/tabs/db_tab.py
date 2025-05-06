# core/views/tabs/db_tab.py
import customtkinter as ctk
from core.utils.i18n import _

class DatabaseTab(ctk.CTkScrollableFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(fg_color=("gray90", "gray13"), corner_radius=0)
        self.create_widgets()
        self.place_widgets()

    def create_widgets(self):
        self.label = ctk.CTkLabel(self, text=_("Welcome to the Database tab"))
        self.label.grid(row=0, column=0, padx=10, pady=10)

    def place_widgets(self):
        pass

    def refresh(self):
        self.label.configure(text=_("Welcome to the Database tab"))