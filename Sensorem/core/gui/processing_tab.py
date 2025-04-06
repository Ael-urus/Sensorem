# core/gui/processing_tab.py
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from ..utils.i18n import _, _f, translator


class ProcessingTab(ttk.Frame):
    def __init__(self, parent, log_manager):
        super().__init__(parent)
        self.log_manager = log_manager
        self._create_widgets()
        self._setup_layout()
        self.log_manager.info(_("Processing tab initialized"))

        # S'abonner aux changements de langue
        translator.add_observer(self._on_language_changed)

    def _create_widgets(self):
        """Crée tous les widgets de l'onglet"""
        self.control_frame = ttk.LabelFrame(self, text=_("Control"))
        self.trigram_label = ttk.Label(self.control_frame, text=_("Trigram:"))
        self.trigram_entry = ttk.Entry(self.control_frame, width=10)
        self.trigram_button = ttk.Button(
            self.control_frame,
            text=_("Validate"),
            command=self._validate_trigram
        )
        self.graph_frame = ttk.LabelFrame(self, text=_("Visualization"))
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
            # Utilisation de _f pour le formatage standard
            self.log_manager.info(_f("Trigram validated: {0}", trigram))
        else:
            self.log_manager.warning(_("Invalid trigram"))
            # Titre traduit pour le message d'erreur
            messagebox.showerror(_("Error"), _("The trigram must contain 3 letters"))

    def _on_language_changed(self, lang_code):
        """Met à jour les textes de l'interface après un changement de langue"""
        # Mettre à jour les textes des widgets
        self.control_frame.configure(text=_("Control"))
        self.trigram_label.configure(text=_("Trigram:"))
        self.trigram_button.configure(text=_("Validate"))
        self.graph_frame.configure(text=_("Visualization"))

    def __del__(self):
        # Se désabonner pour éviter les fuites mémoire
        translator.remove_observer(self._on_language_changed)