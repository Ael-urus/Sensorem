# processing_tab.py
import customtkinter as ctk
import re
from tkinter import messagebox
from ...utils.i18n import _
from ...utils.logger import logger

class CapteurFrame(ctk.CTkFrame):
    """Cadre pour la saisie des informations d'un capteur."""
    def __init__(self, master, is_first=False, **kwargs):
        super().__init__(master, **kwargs)
        self.nom_var = ctk.StringVar()
        self.debut_var = ctk.StringVar()
        self.is_first = is_first
        self.create_widgets()
        self.place_widgets()

    def create_widgets(self):
        self.nom_label = ctk.CTkLabel(self, text=_("Sensor Name:"))
        self.nom_entry = ctk.CTkEntry(self, textvariable=self.nom_var, width=100)
        self.debut_label = ctk.CTkLabel(self, text=_("Start Line:"))
        self.debut_entry = ctk.CTkEntry(self, textvariable=self.debut_var, width=100)
        if not self.is_first:
            self.delete_button = ctk.CTkButton(self, text=_("Delete"), command=self.supprimer, width=80)

    def place_widgets(self):
        self.nom_label.grid(row=0, column=0, padx=5, pady=5)
        self.nom_entry.grid(row=0, column=1, padx=5, pady=5)
        self.debut_label.grid(row=0, column=2, padx=5, pady=5)
        self.debut_entry.grid(row=0, column=3, padx=5, pady=5)
        if not self.is_first:
            self.delete_button.grid(row=0, column=4, padx=5, pady=5)

    def supprimer(self):
        self.master.remove_capteur(self)

    def get_values(self):
        return self.nom_var.get(), self.debut_var.get()

    def set_values(self, nom, debut):
        self.nom_var.set(nom)
        self.debut_var.set(debut)

    def reset(self):
        self.set_values("", "")

class CapteursManager(ctk.CTkFrame):
    """Gestionnaire de capteurs."""
    def __init__(self, parent, processing_tab, **kwargs):
        super().__init__(parent, **kwargs)
        self.processing_tab = processing_tab  # Référence à ProcessingTab
        self.capteurs = []
        self.create_widgets()
        self.add_capteur("H_", "0", is_first=True)

    def create_widgets(self):
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(fill="x", pady=5)
        self.add_button = ctk.CTkButton(self.button_frame, text=_("Add Sensor"), command=lambda: self.add_capteur())
        self.add_button.pack(side="left", padx=5)
        self.validate_button = ctk.CTkButton(self.button_frame, text=_("Validate Sensors"), command=self.valider_capteurs)
        self.validate_button.pack(side="left", padx=5)
        self.status_label = ctk.CTkLabel(self.button_frame, text="❌")
        self.status_label.pack(side="left", padx=5)

    def add_capteur(self, nom="", debut="", is_first=False):
        capteur = CapteurFrame(self, is_first=is_first)
        capteur.pack(pady=2)
        self.capteurs.append(capteur)
        if nom and debut:
            capteur.set_values(nom, debut)

    def remove_capteur(self, capteur):
        if capteur != self.capteurs[0]:
            self.capteurs.remove(capteur)
            capteur.destroy()

    def valider_capteurs(self):
        try:
            values = [capteur.get_values() for capteur in self.capteurs]
            if any(not nom or not debut for nom, debut in values):
                raise ValueError(_("All sensors must have a name and start line."))
            for nom, debut in values:
                if not re.match(r'^[a-zA-Z0-9_]+$', nom):
                    raise ValueError(_("Sensor name '{}' is invalid.").format(nom))
                if not debut.isdigit():
                    raise ValueError(_("Start line '{}' must be a number.").format(debut))
            logger.info(_("Sensors validated successfully: {}").format(
                ", ".join(f"{nom} (start: {debut})" for nom, debut in values)
            ))
            self.processing_tab.set_state("capteurs_valides", True)
            self.status_label.configure(text="✅")
        except ValueError as e:
            logger.error(str(e))
            messagebox.showerror(_("Validation Error"), str(e))
            self.processing_tab.set_state("capteurs_valides", False)
            self.status_label.configure(text="❌")
        self.processing_tab.update_pdf_button()

    def reset_capteurs(self):
        for capteur in self.capteurs[1:]:
            capteur.destroy()
        self.capteurs = [self.capteurs[0]]
        self.capteurs[0].reset()
        self.processing_tab.set_state("capteurs_valides", False)
        self.status_label.configure(text="❌")
        self.processing_tab.update_pdf_button()

    def refresh(self):
        """Rafraîchir les traductions sans recréer les boutons."""
        self.add_button.configure(text=_("Add Sensor"))
        self.validate_button.configure(text=_("Validate Sensors"))
        for capteur in self.capteurs:
            capteur.nom_label.configure(text=_("Sensor Name:"))
            capteur.debut_label.configure(text=_("Start Line:"))
            if not capteur.is_first:
                capteur.delete_button.configure(text=_("Delete"))

class ProcessingTab(ctk.CTkScrollableFrame):
    """Onglet Processing avec trigramme, capteurs, unités et coefficients."""
    def __init__(self, parent, load_csv_callback):
        super().__init__(parent)
        self.load_csv_callback = load_csv_callback
        self.state = {
            "trigramme_valide": False,
            "capteurs_valides": False,
            "unites_valides": False,
            "coefficients_valides": False
        }
        self.create_widgets()
        self.place_widgets()

    def set_state(self, key, value):
        self.state[key] = value
        self.update_status_labels()

    def get_state(self, key):
        return self.state.get(key)

    def create_widgets(self):
        # Conteneur principal pour la disposition côte à côte
        self.main_frame = ctk.CTkFrame(self)

        # Trigramme
        self.trigramme_frame = ctk.CTkFrame(self.main_frame)
        self.trigramme_label = ctk.CTkLabel(self.trigramme_frame, text=_("Name (Trigram):"))
        self.trigramme_var = ctk.StringVar(value="Bbu")
        self.trigramme_entry = ctk.CTkEntry(self.trigramme_frame, textvariable=self.trigramme_var, width=80)
        self.trigramme_button = ctk.CTkButton(self.trigramme_frame, text=_("Validate"), command=self.valider_trigramme, width=80)
        self.trigramme_status = ctk.CTkLabel(self.trigramme_frame, text="❌")

        # Capteurs
        self.capteurs_manager = CapteursManager(self.main_frame, self)  # Passer self comme processing_tab

        # Unités
        self.unites_frame = ctk.CTkFrame(self.main_frame)
        self.unit_capteurs_label = ctk.CTkLabel(self.unites_frame, text=_("Unit (Sensor):"))
        self.unit_capteurs_var = ctk.StringVar(value="[V]")
        self.unit_capteurs_entry = ctk.CTkEntry(self.unites_frame, textvariable=self.unit_capteurs_var, width=80)
        self.unit_ref_label = ctk.CTkLabel(self.unites_frame, text=_("Unit (Ref Sensor):"))
        self.unit_ref_var = ctk.StringVar(value="[m/s]")
        self.unit_ref_entry = ctk.CTkEntry(self.unites_frame, textvariable=self.unit_ref_var, width=80)
        self.nom_ref_label = ctk.CTkLabel(self.unites_frame, text=_("Name (Ref Sensor):"))
        self.nom_ref_var = ctk.StringVar(value="Venturi")
        self.nom_ref_entry = ctk.CTkEntry(self.unites_frame, textvariable=self.nom_ref_var, width=100)
        self.unites_button = ctk.CTkButton(self.unites_frame, text=_("Validate Units"), command=self.valider_unites)
        self.unites_status = ctk.CTkLabel(self.unites_frame, text="❌")

        # Coefficients
        self.coefficients_frame = ctk.CTkFrame(self.main_frame, border_width=2)
        self.coefficients_title = ctk.CTkLabel(self.coefficients_frame, text=_("Reference Sensor Conversion Coefficients"))
        self.coef_a_label = ctk.CTkLabel(self.coefficients_frame, text=_("Coefficient a:"))
        self.coef_a_var = ctk.StringVar(value="1.0")
        self.coef_a_entry = ctk.CTkEntry(self.coefficients_frame, textvariable=self.coef_a_var, width=80)
        self.coef_b_label = ctk.CTkLabel(self.coefficients_frame, text=_("Coefficient b:"))
        self.coef_b_var = ctk.StringVar(value="0.0")
        self.coef_b_entry = ctk.CTkEntry(self.coefficients_frame, textvariable=self.coef_b_var, width=80)
        self.coefficients_button = ctk.CTkButton(self.coefficients_frame, text=_("Validate Coefficients"), command=self.valider_coefficients)
        self.coefficients_status = ctk.CTkLabel(self.coefficients_frame, text="❌")

        # CSV
        self.csv_frame = ctk.CTkFrame(self)
        self.csv_label = ctk.CTkLabel(self.csv_frame, text=_("Welcome to the Processing tab"))
        self.hello_label = ctk.CTkLabel(self.csv_frame, text=_("Hello to Sensorem"))
        self.csv_button = ctk.CTkButton(self.csv_frame, text=_("Load CSV"), command=self.load_csv_callback)

    def place_widgets(self):
        # Conteneur principal
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.main_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Trigramme
        self.trigramme_frame.grid(row=0, column=0, padx=10, pady=5, sticky="n")
        self.trigramme_label.grid(row=0, column=0, padx=5, pady=5)
        self.trigramme_entry.grid(row=0, column=1, padx=5, pady=5)
        self.trigramme_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        self.trigramme_status.grid(row=0, column=2, padx=5, pady=5)

        # Capteurs
        self.capteurs_manager.grid(row=0, column=1, padx=10, pady=5, sticky="n")

        # Unités
        self.unites_frame.grid(row=0, column=2, padx=10, pady=5, sticky="n")
        self.unit_capteurs_label.grid(row=0, column=0, padx=5, pady=5)
        self.unit_capteurs_entry.grid(row=0, column=1, padx=5, pady=5)
        self.unit_ref_label.grid(row=1, column=0, padx=5, pady=5)
        self.unit_ref_entry.grid(row=1, column=1, padx=5, pady=5)
        self.nom_ref_label.grid(row=2, column=0, padx=5, pady=5)
        self.nom_ref_entry.grid(row=2, column=1, padx=5, pady=5)
        self.unites_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        self.unites_status.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # Coefficients
        self.coefficients_frame.grid(row=0, column=3, padx=10, pady=5, sticky="n")
        self.coefficients_title.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        self.coef_a_label.grid(row=1, column=0, padx=5, pady=5)
        self.coef_a_entry.grid(row=1, column=1, padx=5, pady=5)
        self.coef_b_label.grid(row=2, column=0, padx=5, pady=5)
        self.coef_b_entry.grid(row=2, column=1, padx=5, pady=5)
        self.coefficients_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        self.coefficients_status.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # CSV
        self.csv_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.csv_label.pack(pady=10)
        self.hello_label.pack(pady=10)
        self.csv_button.pack(pady=10)

    def valider_trigramme(self):
        trigramme = self.trigramme_var.get()
        if len(trigramme) != 3 or not trigramme.isalpha():
            logger.error(_("Trigram must be exactly 3 letters."))
            messagebox.showerror(_("Validation Error"), _("Trigram must be exactly 3 letters."))
            self.trigramme_var.set("Bbu")
            self.set_state("trigramme_valide", False)
            self.trigramme_status.configure(text="❌")
        else:
            logger.info(_("Trigram validated: {}").format(trigramme))
            self.set_state("trigramme_valide", True)
            self.trigramme_status.configure(text="✅")
        self.update_pdf_button()

    def valider_unites(self):
        unit = self.unit_capteurs_var.get().strip()
        unit_ref = self.unit_ref_var.get().strip()
        nom_ref = self.nom_ref_var.get().strip()
        if not unit or not unit_ref or not nom_ref:
            logger.error(_("Units and reference name must be provided."))
            messagebox.showerror(_("Validation Error"), _("Units and reference name must be provided."))
            self.set_state("unites_valides", False)
            self.unites_status.configure(text="❌")
        else:
            logger.info(_("Units validated: Sensor: {}, Ref: {}, Ref Name: {}").format(unit, unit_ref, nom_ref))
            self.set_state("unites_valides", True)
            self.unites_status.configure(text="✅")
        self.update_pdf_button()

    def valider_coefficients(self):
        try:
            coef_a = float(self.coef_a_var.get().strip())
            coef_b = float(self.coef_b_var.get().strip())
            if coef_a == 0:
                logger.error(_("Coefficient a cannot be zero."))
                messagebox.showerror(_("Validation Error"), _("Coefficient a cannot be zero."))
                self.set_state("coefficients_valides", False)
                self.coefficients_status.configure(text="❌")
            else:
                logger.info(_("Coefficients validated: a={}, b={}").format(coef_a, coef_b))
                self.set_state("coefficients_valides", True)
                self.coefficients_status.configure(text="✅")
        except ValueError:
            logger.error(_("Coefficients must be valid numbers."))
            messagebox.showerror(_("Validation Error"), _("Coefficients must be valid numbers."))
            self.set_state("coefficients_valides", False)
            self.coefficients_status.configure(text="❌")
        self.update_pdf_button()

    def update_status_labels(self):
        self.trigramme_status.configure(text="✅" if self.state["trigramme_valide"] else "❌")
        self.unites_status.configure(text="✅" if self.state["unites_valides"] else "❌")
        self.coefficients_status.configure(text="✅" if self.state["coefficients_valides"] else "❌")
        self.capteurs_manager.status_label.configure(text="✅" if self.state["capteurs_valides"] else "❌")

    def update_pdf_button(self):
        pass  # À implémenter plus tard pour le bouton PDF

    def refresh(self):
        """Rafraîchir les traductions."""
        self.trigramme_label.configure(text=_("Name (Trigram):"))
        self.trigramme_button.configure(text=_("Validate"))
        self.unit_capteurs_label.configure(text=_("Unit (Sensor):"))
        self.unit_ref_label.configure(text=_("Unit (Ref Sensor):"))
        self.nom_ref_label.configure(text=_("Name (Ref Sensor):"))
        self.unites_button.configure(text=_("Validate Units"))
        self.coefficients_title.configure(text=_("Reference Sensor Conversion Coefficients"))
        self.coef_a_label.configure(text=_("Coefficient a:"))
        self.coef_b_label.configure(text=_("Coefficient b:"))
        self.coefficients_button.configure(text=_("Validate Coefficients"))
        self.csv_label.configure(text=_("Welcome to the Processing tab"))
        self.hello_label.configure(text=_("Hello to Sensorem"))
        self.csv_button.configure(text=_("Load CSV"))
        self.capteurs_manager.refresh()