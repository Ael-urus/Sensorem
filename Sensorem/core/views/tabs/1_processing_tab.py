# core/gui/processing_tab.py
import os
import re
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # Gardé si vous l'utilisez directement ici
from typing import List, Tuple, Optional, TYPE_CHECKING

# Importez les widgets personnalisés depuis leur nouveau fichier
from Sensorem.core.views.sensor_widgets import CapteurFrame, CapteursManager

# local
from Sensorem.core.utils.i18n import _, _f

# Pour type hinting sans import circulaire
if TYPE_CHECKING:
    from Sensorem.core.controllers.processing_controller import ProcessingController


# --- Classes CapteurFrame et CapteursManager (à garder ici ou dans util.py) ---
# (Copiez vos classes CapteurFrame et CapteursManager ici si elles ne sont pas dans util.py)
class CapteurFrame(ttk.Frame): # Exemple simplifié
    def __init__(self, master, is_first=False):
        super().__init__(master)
        self.nom_var = tk.StringVar()
        self.debut_var = tk.StringVar()
        # ... (reste de votre code CapteurFrame) ...
        self.nom_entry = ttk.Entry(self, textvariable=self.nom_var, width=10)
        self.debut_entry = ttk.Entry(self, textvariable=self.debut_var, width=10)
        self.nom_label = ttk.Label(self, text=_("Name") + " :")
        self.debut_label = ttk.Label(self, text=_("Start") + " :")
        self.nom_label.grid(row=0, column=0)
        self.nom_entry.grid(row=0, column=1)
        self.debut_label.grid(row=0, column=2)
        self.debut_entry.grid(row=0, column=3)
        if not is_first:
            self.delete_button = ttk.Button(self, text=_("Remove"), command=self.supprimer)
            self.delete_button.grid(row=0, column=4)

    def supprimer(self):
        if hasattr(self.master, 'remove_capteur'):
             self.master.remove_capteur(self)

    def get_values(self):
        return self.nom_var.get(), self.debut_var.get()

class CapteursManager(ttk.Frame): # Exemple simplifié
    def __init__(self, master):
        super().__init__(master)
        self.capteurs = []
        # ... (reste de votre code CapteursManager) ...
        ttk.Button(self, text=_("Add sensor"), command=self.add_capteur).pack(anchor="w")
        self.add_capteur("H_", "0", True) # Ajoute le capteur initial

    def add_capteur(self, nom="", debut="", is_first=False):
        capteur = CapteurFrame(self, is_first)
        capteur.pack(anchor="w", pady=2)
        self.capteurs.append(capteur)
        if nom: capteur.nom_var.set(nom)
        if debut: capteur.debut_var.set(debut)

    def remove_capteur(self, capteur):
        if capteur in self.capteurs and not capteur.is_first: # Ne pas supprimer le premier
            self.capteurs.remove(capteur)
            capteur.destroy()

    def get_capteurs_info(self):
        return [c.get_values() for c in self.capteurs]

    def reset_capteurs(self): # Optionnel: si nécessaire
        for c in reversed(self.capteurs):
             if not c.is_first:
                 self.remove_capteur(c)
        # Réinitialiser le premier capteur si besoin
        # self.capteurs[0].nom_var.set("H_")
        # self.capteurs[0].debut_var.set("0")

# --- Classe Principale de la Vue ---
class ProcessingTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.controller: Optional['ProcessingController'] = None # Référence au contrôleur
        self._create_widgets()

    def set_controller(self, controller: 'ProcessingController'):
        """Injecte le contrôleur et connecte les commandes."""
        self.controller = controller
        # Connecter les commandes des boutons au contrôleur
        self.validate_trigram_btn['command'] = self.controller.handle_validate_trigram
        self.validate_units_btn['command'] = self.controller.handle_validate_units
        self.validate_capteurs_btn['command'] = self.controller.handle_validate_sensors
        self.pdf_button['command'] = self.controller.handle_generate_pdf
        # Connecter la sélection dans la liste de fichiers (si nécessaire)
        self.file_list.bind('<<ListboxSelect>>', self._on_file_select)

    def _on_file_select(self, event=None):
        """Gère la sélection d'un fichier dans la liste."""
        # Peut-être lancer le traitement automatiquement ou activer un bouton "Process"
        if self.controller:
             # Exemple: Lancer le traitement à la sélection
             # self.controller.process_selected_file()
             pass # Ou juste notifier le controller : self.controller.selected_file_changed()

    def _create_widgets(self):
        # Frame supérieur pour les formulaires
        form_frame = ttk.Frame(self)
        form_frame.pack(fill="x", pady=5, padx=5)

        # --- Configuration Grid & Séparateurs ---
        # (Identique à votre version précédente)
        ttk.Separator(form_frame, orient="vertical").grid(row=0, column=3, rowspan=5, sticky="ns", padx=5)
        ttk.Separator(form_frame, orient="vertical").grid(row=0, column=6, rowspan=5, sticky="ns", padx=5)
        ttk.Separator(form_frame, orient="vertical").grid(row=0, column=9, rowspan=5, sticky="ns", padx=5)

        # --- Partie 1 : Trigramme ---
        ttk.Label(form_frame, text=_("Trigram:")).grid(row=0, column=0, sticky="w", padx=(5,0))
        self.trigram_entry = ttk.Entry(form_frame, width=6)
        self.trigram_entry.grid(row=0, column=1, padx=5, pady=2)
        # Le bouton est créé, mais la commande est définie dans set_controller
        self.validate_trigram_btn = ttk.Button(form_frame, text=_("Validate"))
        self.validate_trigram_btn.grid(row=0, column=2, padx=5)

        # --- Partie 2 : Unités ---
        ttk.Label(form_frame, text=_("Unit (Sensor) :")).grid(row=0, column=4, sticky="w")
        self.unit_entry = ttk.Entry(form_frame, width=6)
        self.unit_entry.grid(row=0, column=5, padx=5, pady=2)
        ttk.Label(form_frame, text=_("Unit (Reference) :")).grid(row=1, column=4, sticky="w")
        self.unit_ref_entry = ttk.Entry(form_frame, width=6)
        self.unit_ref_entry.grid(row=1, column=5, padx=5, pady=2)
        ttk.Label(form_frame, text=_("Reference Name :")).grid(row=2, column=4, sticky="w")
        self.nom_ref_entry = ttk.Entry(form_frame, width=10)
        self.nom_ref_entry.grid(row=2, column=5, padx=5, pady=2)
        self.validate_units_btn = ttk.Button(form_frame, text=_("Validate Units"))
        self.validate_units_btn.grid(row=3, column=5, padx=5, pady=5)

        # --- Partie 3 : Capteurs ---
        self.capteurs_frame = CapteursManager(form_frame)
        self.capteurs_frame.grid(row=0, column=7, rowspan=4, padx=10, sticky="nsew")
        form_frame.rowconfigure(0, weight=1) # Pour l'expansion verticale si besoin
        self.validate_capteurs_btn = ttk.Button(form_frame, text=_("Validate Sensors"))
        self.validate_capteurs_btn.grid(row=4, column=7, sticky="se", pady=5, padx=10)

        # --- Partie 4 : Coefficients ---
        ttk.Label(form_frame, text=_("Conversion Coeff. 1:")).grid(row=0, column=10, sticky="w")
        self.coeff1_entry = ttk.Entry(form_frame, width=8)
        self.coeff1_entry.grid(row=0, column=11, padx=5, pady=2)
        ttk.Label(form_frame, text=_("Conversion Coeff. 2:")).grid(row=1, column=10, sticky="w")
        self.coeff2_entry = ttk.Entry(form_frame, width=8)
        self.coeff2_entry.grid(row=1, column=11, padx=5, pady=2, sticky="w")

        # --- Section Fichiers & Processing (avec Grid) ---
        list_output_frame = ttk.Frame(self)
        list_output_frame.pack(fill="both", expand=True, pady=5, padx=5)
        list_output_frame.columnconfigure(0, weight=1)
        list_output_frame.columnconfigure(1, weight=1)
        list_output_frame.rowconfigure(1, weight=1)

        ttk.Label(list_output_frame, text=_("Files list:")).grid(row=0, column=0, sticky="w", padx=5, pady=(0,2))
        self.file_list = tk.Listbox(list_output_frame, height=8, exportselection=False) # exportselection=False important
        self.file_list.grid(row=1, column=0, sticky="nsew", padx=(5, 2), pady=(0, 5))
        # Ajouter une scrollbar à la Listbox
        scrollbar_list = ttk.Scrollbar(list_output_frame, orient="vertical", command=self.file_list.yview)
        scrollbar_list.grid(row=1, column=0, sticky="nse", padx=(5, 2), pady=(0,5)) # Grid à côté
        self.file_list.configure(yscrollcommand=scrollbar_list.set)


        ttk.Label(list_output_frame, text=_("Processing output:")).grid(row=0, column=1, sticky="w", padx=5, pady=(0,2))
        self.output_text = tk.Text(list_output_frame, height=8, wrap="none")
        self.output_text.grid(row=1, column=1, sticky="nsew", padx=(2, 5), pady=(0, 5))
        # Ajouter une scrollbar à la Text Area
        scrollbar_text_y = ttk.Scrollbar(list_output_frame, orient="vertical", command=self.output_text.yview)
        scrollbar_text_y.grid(row=1, column=1, sticky="nse", padx=(2,5), pady=(0,5)) # Grid à côté
        scrollbar_text_x = ttk.Scrollbar(list_output_frame, orient="horizontal", command=self.output_text.xview)
        scrollbar_text_x.grid(row=2, column=1, sticky="sew", padx=(2,5), pady=(0,5)) # Grid en dessous
        self.output_text.configure(yscrollcommand=scrollbar_text_y.set, xscrollcommand=scrollbar_text_x.set)

        # --- Section Graphiques ---
        graph_frame = ttk.Frame(self)
        graph_frame.pack(fill="x", expand=False, padx=5, pady=5)
        self.graph1_frame = ttk.Frame(graph_frame, relief="sunken", borderwidth=1, height=150)
        self.graph2_frame = ttk.Frame(graph_frame, relief="sunken", borderwidth=1, height=150)
        # Vous intégrerez vos FigureCanvasTkAgg ici
        ttk.Label(self.graph1_frame, text=_("Graph 1 Area")).pack(expand=True) # Placeholder
        ttk.Label(self.graph2_frame, text=_("Graph 2 Area")).pack(expand=True) # Placeholder
        self.graph1_frame.pack(side="left", expand=True, fill="both", padx=(0, 2))
        self.graph2_frame.pack(side="left", expand=True, fill="both", padx=(2, 0))

        # --- Bouton PDF ---
        self.pdf_button = ttk.Button(self, text=_("Generate PDF"))
        self.pdf_button.pack(anchor="e", padx=10, pady=(5, 10))


    # --- Méthodes pour que le Contrôleur lise l'état de la Vue ---

    def get_trigram(self) -> str:
        return self.trigram_entry.get()

    def get_unit_values(self) -> Tuple[str, str, str]:
        return self.unit_entry.get().strip(), self.unit_ref_entry.get().strip(), self.nom_ref_entry.get().strip()

    def get_sensor_info(self) -> List[Tuple[str, str]]:
        return self.capteurs_frame.get_capteurs_info()

    def get_coefficients(self) -> Tuple[str, str]:
        # Ajouter validation/conversion en nombre si nécessaire ici ou dans le contrôleur
        return self.coeff1_entry.get(), self.coeff2_entry.get()

    def get_selected_file_from_list(self) -> Optional[str]:
        """Retourne le nom du fichier sélectionné ou None."""
        selection_indices = self.file_list.curselection()
        if selection_indices:
            return self.file_list.get(selection_indices[0])
        return None

    # --- Méthodes pour que le Contrôleur mette à jour la Vue ---

    def show_error(self, title: str, message: str):
        messagebox.showerror(title, message, parent=self) # parent=self pour la modalité

    def show_info(self, title: str, message: str):
        messagebox.showinfo(title, message, parent=self)

    def update_output_text(self, text: str):
        """Efface et met à jour la zone de texte de sortie."""
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert('1.0', text)

    def clear_trigram_input(self, default_text: str = ""):
        """Efface le champ trigramme et insère un texte par défaut."""
        self.trigram_entry.delete(0, tk.END)
        self.trigram_entry.insert(0, default_text)

    def set_pdf_button_state(self, enabled: bool):
        """Active ou désactive le bouton PDF."""
        state = tk.NORMAL if enabled else tk.DISABLED
        self.pdf_button.configure(state=state)

    def update_file_list(self, files: List[str]):
         """Met à jour la liste des fichiers affichés."""
         self.file_list.delete(0, tk.END)
         for file in files:
             self.file_list.insert(tk.END, file)

    # Ajoutez d'autres méthodes set/get ou d'update si nécessaire
    # Par exemple, pour désactiver des champs après validation:
    # def set_trigram_entry_state(self, enabled: bool):
    #     state = tk.NORMAL if enabled else tk.DISABLED
    #     self.trigram_entry.configure(state=state)