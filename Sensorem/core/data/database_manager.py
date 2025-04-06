# Exemple d'onglet Base de données (db_tab.py)
import tkinter as tk
from tkinter import ttk


class DatabaseTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._create_widgets()

    def _create_widgets(self):
        self.tree = ttk.Treeview(self, columns=('ID', 'Nom', 'Valeur'))
        self.tree.heading('#0', text='Capteur')
        self.tree.heading('ID', text='ID')
        self.tree.pack(expand=True, fill=tk.BOTH)

        self.import_btn = ttk.Button(
            self,
            text="Importer données",
            command=self._import_data
        )
        self.import_btn.pack()

    def _import_data(self):
        # Logique d'importation
        pass