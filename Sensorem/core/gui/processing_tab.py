# core/gui/processing_tab.py
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from ..utils.i18n import _


class ProcessingTab(ttk.Frame):
    def __init__(self, parent, log_manager):
        super().__init__(parent)
        self.log_manager = log_manager
        self._create_widgets()
        self._setup_layout()
        self.log_manager.info(_("Initialized Processing Tab"))

    def _create_widgets(self):
        """Crée tous les widgets de l'onglet"""
        self.control_frame = ttk.LabelFrame(self, text=_("Control"), padding=10)
        self.trigram_label = ttk.Label(self.control_frame, text=_("Trigramme:"))
        self.trigram_entry = ttk.Entry(self.control_frame, width=10)
        self.trigram_button = ttk.Button(
            self.control_frame,
            text=_("Validate"),
            command=self._validate_trigram
        )
        self.graph_frame = ttk.LabelFrame(self, text=_("Visualization"), padding=10)
        self.canvas_raw = tk.Canvas(self.graph_frame, bg='white', height=300)
        self.canvas_processed = tk.Canvas(self.graph_frame, bg='white', height=300)

    def _setup_layout(self):
        """Configure le layout des widgets"""
        self.control_frame.pack(fill="x", padx=5, pady=5)
        self.trigram_label.grid(row=0, column=0, padx=5)
        self.trigram_entry.grid(row=0, column=1, padx=5)
        self.trigram_button.grid(row=0, column=2, padx=5)
        self.graph_frame.pack(fill="both", expand=True, padx=5, pady=5)
        self.canvas_raw.pack(fill="both", expand=True, pady=5)
        self.canvas_processed.pack(fill="both", expand=True, pady=5)

    def _validate_trigram(self):
        """Valide le trigramme saisi"""
        trigram = self.trigram_entry.get()
        if len(trigram) == 3 and trigram.isalpha():
            self.log_manager.info(f"{_('Trigramme validé:')} {trigram}")
        else:
            self.log_manager.warning(_("Invalid trigram"))
            messagebox.showerror("Erreur", _("The trigram must contain 3 letters"))