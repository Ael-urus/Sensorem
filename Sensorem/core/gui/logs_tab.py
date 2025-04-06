# core/gui/logs_tab.py
import tkinter as tk
from tkinter import ttk

from ..utils.i18n import _


class LogsTab(ttk.Frame):
    def __init__(self, parent, log_manager):
        super().__init__(parent)
        self.log_manager = log_manager
        self._create_widgets()
        self._setup_logging()
        self.log_manager.info(_("Processing tab initialized"))

    def _create_widgets(self):
        """Crée les widgets de l'onglet"""
        self.log_text = tk.Text(
            self,
            wrap=tk.WORD,
            state='disabled',
            font=('Consolas', 10)
        )

        scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.log_text.yview  # Fixed from self.tree.yview
        )
        self.log_text.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.log_text.pack(expand=True, fill="both", padx=5, pady=5)

    def _setup_logging(self):
        """Configure la sortie des logs"""
        self.log_manager.add_output(self.log_text)