# core/gui/db_tab.py
from tkinter import ttk
from Sensorem.core.utils.i18n import _, translator

class DatabaseTab(ttk.Frame):
    def __init__(self, parent, log_manager):
        super().__init__(parent)
        self.log_manager = log_manager
        self._create_widgets()
        self.log_manager.info(_("Database tab initialized"))

        # S'abonner aux changements de langue
        translator.add_observer(self._on_language_changed)

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
            text=_("Import"),  # Utiliser une clé de traduction
            command=self._import_data
        )

        scrollbar.pack(side="right", fill="y")
        self.tree.pack(expand=True, fill="both", padx=5, pady=5)
        self.import_btn.pack(pady=5)

    def _import_data(self):
        """Exemple de fonction d'import"""
        self.log_manager.info(_("Trying to import values"))

    def _on_language_changed(self, lang_code):
        """Met à jour les textes de l'interface après un changement de langue"""
        # Mettre à jour les entêtes de colonnes
        self.tree.heading('id', text=_('ID'))
        self.tree.heading('name', text=_('Name'))
        self.tree.heading('value', text=_('Value'))

        # Mettre à jour le bouton
        self.import_btn.configure(text=_("Import"))

    def __del__(self):
        # Se désabonner pour éviter les fuites mémoire
        translator.remove_observer(self._on_language_changed)