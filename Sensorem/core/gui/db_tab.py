# core/gui/db_tab.py
from tkinter import ttk

from ..utils.i18n import _


class DatabaseTab(ttk.Frame):
    def __init__(self, parent, log_manager):
        super().__init__(parent)
        self.log_manager = log_manager
        self._create_widgets()
        self.log_manager.info(_("Database tab initialized"))

    def _create_widgets(self):
        """Crée les widgets de l'onglet"""
        self.tree = ttk.Treeview(self, columns=('id', 'name', 'value'), show='headings')
        self.tree.heading('id', text=_('ID'))
        self.tree.heading('name', text=_('Name'))
        self.tree.heading('value', text=_('Value'))

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.import_btn = ttk.Button(
            self,
            text="Importer",
            command=self._import_data
        )

        scrollbar.pack(side="right", fill="y")
        self.tree.pack(expand=True, fill="both", padx=5, pady=5)
        self.import_btn.pack(pady=5)

    def _import_data(self):
        """Exemple de fonction d'import"""
        self.log_manager.info(_("Trying to import values"))