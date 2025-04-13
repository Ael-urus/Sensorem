# core/gui/logs_tab.py
import tkinter as tk
from tkinter import ttk

from Sensorem.core.utils.i18n import _


class LogsTab(ttk.Frame):
    def __init__(self, parent, log_manager):
        super().__init__(parent)
        self.log_manager = log_manager
        self._create_widgets()
        self._setup_logging()
        self.log_manager.info(_("Logs tab initialized"))

    def _create_widgets(self):
        """Crée les widgets de l'onglet"""
        # Créer un cadre pour contenir le texte et la barre de défilement
        text_frame = ttk.Frame(self)
        text_frame.pack(expand=True, fill="both", padx=5, pady=5)

        # Créer le widget Text avec une police monospace pour meilleur alignement
        self.log_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            state='disabled',
            font=('Consolas', 10),
            background='white'
        )

        # Configurer les tags de couleur pour les différents niveaux de log
        for level, color in self.log_manager.colors.items():
            self.log_text.tag_configure(level, foreground=color)

        # Ajouter une barre de défilement
        scrollbar = ttk.Scrollbar(
            text_frame,
            orient="vertical",
            command=self.log_text.yview
        )
        self.log_text.configure(yscrollcommand=scrollbar.set)

        # Disposition
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # Ajouter des boutons pour contrôler les logs
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", padx=5, pady=5)

        clear_button = ttk.Button(
            button_frame,
            text=_("Clear logs"),
            command=self._clear_logs
        )
        clear_button.pack(side=tk.RIGHT, padx=5)

    def _setup_logging(self):
        """Configure la sortie des logs"""
        self.log_manager.add_output(self.log_text)

    def _clear_logs(self):
        """Efface tous les logs du widget Text"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.log_manager.info(_("Logs cleared"))