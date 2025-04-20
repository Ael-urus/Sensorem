# processing_tab.py
import customtkinter as ctk
import re
import os
import glob
from tkinter import messagebox
import tkinter as tk
from ...utils.i18n import _
from ...utils.logger import logger

class CapteurFrame(ctk.CTkFrame):
    def __init__(self, master, capteurs_manager, is_first=False, **kwargs): # Add capteurs_manager parameter
        super().__init__(master, **kwargs)
        self.capteurs_manager = capteurs_manager # Store the CapteursManager instance
        self.nom_var = ctk.StringVar()
        self.debut_var = ctk.StringVar()
        self.is_first = is_first
        self.create_widgets()
        self.place_widgets()

    def create_widgets(self):
        self.nom_label = ctk.CTkLabel(self, text=_("Sensor Name:"))
        # Set your desired width here
        self.nom_entry = ctk.CTkEntry(self, textvariable=self.nom_var, width=120)  # Example width
        self.debut_label = ctk.CTkLabel(self, text=_("Start Line:"))
        # Set your desired width here
        self.debut_entry = ctk.CTkEntry(self, textvariable=self.debut_var, width=70)  # Example width
        if not self.is_first:
            self.delete_button = ctk.CTkButton(self, text="🗑️ " + _("Delete"), command=self.supprimer, width=70)

    def place_widgets(self):
        # Configure columns to allow expansion for entry fields (columns will expand, but entries won't fill them)
        self.grid_columnconfigure(0, weight=0) # Sensor Name Label
        self.grid_columnconfigure(1, weight=1) # Sensor Name Entry, allow column expansion
        self.grid_columnconfigure(2, weight=0) # Start Line Label
        self.grid_columnconfigure(3, weight=1) # Start Line Entry, allow column expansion
        if not self.is_first:
             self.grid_columnconfigure(4, weight=0) # Delete Button

        self.nom_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        # Removed sticky="ew" - entry width is now controlled by the 'width' parameter in create_widgets
        self.nom_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.debut_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        # Removed sticky="ew" - entry width is now controlled by the 'width' parameter in create_widgets
        self.debut_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        if not self.is_first:
            self.delete_button.grid(row=0, column=4, padx=5, pady=5, sticky="w") # Kept sticky="w" for alignment

    def supprimer(self):
        self.capteurs_manager.remove_capteur(self) # Call remove_ca

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
        self.processing_tab = processing_tab
        self.capteurs = []
        self.create_widgets()
        self.add_capteur("H_", "0", is_first=True)

    def create_widgets(self):
        # Cadre pour les boutons
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(fill="x", pady=2)  # Réduire pady

        self.add_button = ctk.CTkButton(self.button_frame, text=_("Add Sensor"), command=lambda: self.add_capteur())
        self.add_button.pack(side="left", padx=5)

        self.validate_button = ctk.CTkButton(self.button_frame, text=_("Validate Sensors"),
                                             command=self.valider_capteurs)
        self.validate_button.pack(side="left", padx=5)

        self.status_label = ctk.CTkLabel(self.button_frame, text="❌")
        self.status_label.pack(side="left", padx=5)

        # Cadre pour contenir les capteurs avec défilement
        self.capteurs_container = ctk.CTkScrollableFrame(self, height=150)
        self.capteurs_container.pack(fill="both", expand=True, pady=2)  # Réduire pady

    def add_capteur(self, nom="", debut="", is_first=False):
        # Placer les capteurs dans le conteneur avec défilement
        # Pass self (the CapteursManager instance) to CapteurFrame
        capteur = CapteurFrame(self.capteurs_container, self, is_first=is_first)

        # Removed: capteur.configure(width=580)

        # Pack the CapteurFrame
        capteur.pack(fill="x", pady=2)

        self.capteurs.append(capteur)
        if nom and debut:
            capteur.set_values(nom, debut)

        # Force an update of the layout to potentially recalculate scrollable area
        self.capteurs_container.update_idletasks()

    def remove_capteur(self, capteur):
        if capteur != self.capteurs[0]:
            self.capteurs.remove(capteur)
            capteur.destroy()
            # Also update layout after removing a sensor
            self.capteurs_container.update_idletasks()

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
        self.add_button.configure(text=_("Add Sensor"))
        self.validate_button.configure(text=_("Validate Sensors"))
        for capteur in self.capteurs:
            capteur.nom_label.configure(text=_("Sensor Name:"))
            capteur.debut_label.configure(text=_("Start Line:"))
            if not capteur.is_first:
                capteur.delete_button.configure(text=_("Delete"))

class ProcessingTab(ctk.CTkScrollableFrame):
    """Onglet Processing avec trigramme, capteurs, unités, coefficients, liste de fichiers et graphiques."""

    def __init__(self, parent, load_csv_callback):
        # Configurer le cadre avec une hauteur adaptée
        super().__init__(parent)

        # Configuration pour un meilleur scrolling
        self.configure(
            fg_color=("gray90", "gray13"),  # Couleur de fond uniforme
            corner_radius=0  # Sans coins arrondis pour éviter les effets visuels
        )

        self.load_csv_callback = load_csv_callback
        self.state = {
            "trigramme_valide": False,
            "capteurs_valides": False,
            "unites_valides": False,
            "coefficients_valides": False
        }
        # Chemin vers le dossier Sensorem (remonter 4 niveaux)
        self.current_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
        logger.info(f"Chemin du dossier Sensorem : {self.current_dir}")
        if not os.path.exists(self.current_dir):
            logger.error(f"Dossier Sensorem non trouvé : {self.current_dir}")
        self.create_widgets()
        self.place_widgets()
        self.afficher_liste_fichiers()
        self.initialiser_selection_listbox()

    def set_state(self, key, value):
        self.state[key] = value
        self.update_status_labels()

    def get_state(self, key):
        return self.state.get(key)

    def create_widgets(self):
        # Appliquer un style cohérent à tous les widgets
        title_font = ("Roboto", 16, "bold")
        bg_color = ("gray85", "gray25")  # (mode clair, mode sombre)

        # Canvas pour défilement horizontal et vertical
        self.canvas = ctk.CTkCanvas(self)
        self.h_scrollbar = ctk.CTkScrollbar(self, orientation="horizontal", command=self.canvas.xview)
        self.v_scrollbar = ctk.CTkScrollbar(self, orientation="vertical", command=self.canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(self.canvas)
        self.canvas.configure(xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Trigramme
        self.trigramme_title = ctk.CTkLabel(self.scrollable_frame, text=_("Trigram"), font=title_font)
        self.trigramme_frame = ctk.CTkFrame(self.scrollable_frame, fg_color=bg_color)
        self.trigramme_label = ctk.CTkLabel(self.trigramme_frame, text=_("Name (Trigram):"))
        self.trigramme_var = ctk.StringVar(value="Bbu")
        self.trigramme_entry = ctk.CTkEntry(self.trigramme_frame, textvariable=self.trigramme_var, width=80)
        self.trigramme_button = ctk.CTkButton(self.trigramme_frame, text=_("Validate"), command=self.valider_trigramme,
                                              width=80)
        self.trigramme_status = ctk.CTkLabel(self.trigramme_frame, text="❌")

        # Capteurs
        self.capteurs_title = ctk.CTkLabel(self.scrollable_frame, text=_("Sensors"), font=title_font)
        self.capteurs_manager = CapteursManager(self.scrollable_frame, self, fg_color=bg_color)

        # Unités
        self.unites_title = ctk.CTkLabel(self.scrollable_frame, text=_("Units"), font=title_font)
        self.unites_frame = ctk.CTkFrame(self.scrollable_frame, fg_color=bg_color)
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
        self.coefficients_title = ctk.CTkLabel(self.scrollable_frame, text=_("Coefficients"), font=title_font)
        self.coefficients_frame = ctk.CTkFrame(self.scrollable_frame, fg_color=bg_color, border_width=2)
        self.coefficients_subtitle = ctk.CTkLabel(self.coefficients_frame,
                                                  text=_("Reference Sensor Conversion Coefficients"))
        self.coef_a_label = ctk.CTkLabel(self.coefficients_frame, text=_("Coefficient a:"))
        self.coef_a_var = ctk.StringVar(value="1.0")
        self.coef_a_entry = ctk.CTkEntry(self.coefficients_frame, textvariable=self.coef_a_var, width=80)
        self.coef_b_label = ctk.CTkLabel(self.coefficients_frame, text=_("Coefficient b:"))
        self.coef_b_var = ctk.StringVar(value="0.0")
        self.coef_b_entry = ctk.CTkEntry(self.coefficients_frame, textvariable=self.coef_b_var, width=80)
        self.coefficients_button = ctk.CTkButton(self.coefficients_frame, text=_("Validate Coefficients"),
                                                 command=self.valider_coefficients)
        self.coefficients_status = ctk.CTkLabel(self.coefficients_frame, text="❌")

        # Liste des fichiers et traitement
        self.files_treatment_frame = ctk.CTkFrame(self)

        # --- List of Files Section with Scrollbars ---
        self.files_list_title = ctk.CTkLabel(self, text=_("List of Files:"), font=title_font)
        self.files_list_frame = ctk.CTkFrame(self.files_treatment_frame, fg_color=bg_color) # Parent frame for listbox and scrollbars

        # Create scrollbars for the Listbox
        self.files_list_v_scrollbar = tk.Scrollbar(self.files_list_frame, orient=tk.VERTICAL)
        self.files_list_h_scrollbar = tk.Scrollbar(self.files_list_frame, orient=tk.HORIZONTAL)

        # Create the Listbox
        self.files_listbox = tk.Listbox(
            self.files_list_frame, # Place inside the frame
            height=10, # Your specified height
            width=10,  # Your specified width
            selectmode=tk.SINGLE,
            bd=0,
            highlightthickness=0,
            bg=self.files_list_frame.cget("fg_color")[0],
            fg=ctk.CTkLabel(self).cget("text_color")[0],
            yscrollcommand=self.files_list_v_scrollbar.set, # Link vertical scrollbar
            xscrollcommand=self.files_list_h_scrollbar.set  # Link horizontal scrollbar
        )

        # Configure the scrollbars to command the Listbox's view
        self.files_list_v_scrollbar.config(command=self.files_listbox.yview)
        self.files_list_h_scrollbar.config(command=self.files_listbox.xview)

        # Place the Listbox and its scrollbars within files_list_frame using grid
        # This layout places the listbox, vertical scrollbar to its right, and horizontal scrollbar below
        self.files_listbox.grid(row=0, column=0, sticky="nsew")
        self.files_list_v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.files_list_h_scrollbar.grid(row=1, column=0, sticky="ew")

        # Configure grid weights for the files_list_frame to make the listbox expand
        self.files_list_frame.grid_columnconfigure(0, weight=1)
        self.files_list_frame.grid_rowconfigure(0, weight=1)

        self.files_listbox.bind("<<ListboxSelect>>", self.on_file_select)
        # --- End List of Files Section ---


        # --- Processing File Section with Scrollbars ---
        self.treatment_title = ctk.CTkLabel(self, text=_("File Processing:"), font=title_font)
        self.treatment_frame = ctk.CTkFrame(self.files_treatment_frame, fg_color=bg_color) # Parent frame for textbox and scrollbars

        # Create CTk scrollbars for the CTkTextbox
        self.treatment_v_scrollbar = ctk.CTkScrollbar(self.treatment_frame, orientation="vertical")
        self.treatment_h_scrollbar = ctk.CTkScrollbar(self.treatment_frame, orientation="horizontal")

        # Create the CTkTextbox
        self.treatment_text = ctk.CTkTextbox(
            self.treatment_frame, # Place inside the frame
            height=150, # Your specified height
            width=400,  # Your specified width
            state="disabled",
            yscrollcommand=self.treatment_v_scrollbar.set, # Link vertical scrollbar
            xscrollcommand=self.treatment_h_scrollbar.set  # Link horizontal scrollbar
        )

        # Configure the scrollbars to command the Textbox's view
        self.treatment_v_scrollbar.configure(command=self.treatment_text.yview)
        self.treatment_h_scrollbar.configure(command=self.treatment_text.xview)

        # Place the Textbox and its scrollbars within treatment_frame using grid
        # This layout places the textbox, vertical scrollbar to its right, and horizontal scrollbar below
        self.treatment_text.grid(row=0, column=0, sticky="nsew")
        self.treatment_v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.treatment_h_scrollbar.grid(row=1, column=0, sticky="ew")

        # Configure grid weights for the treatment_frame to make the textbox expand
        self.treatment_frame.grid_columnconfigure(0, weight=1)
        self.treatment_frame.grid_rowconfigure(0, weight=1)
        # --- End Processing File Section ---


        # Graphiques
        self.graph_title = ctk.CTkLabel(self, text=_("Graphs"), font=title_font)
        self.graph_frame = ctk.CTkFrame(self, fg_color=bg_color)
        self.graph1_frame = ctk.CTkFrame(self.graph_frame, border_width=2, width=300, height=300)
        self.graph2_frame = ctk.CTkFrame(self.graph_frame, border_width=2, width=300, height=300)
        self.graph1_label = ctk.CTkLabel(self.graph1_frame, text=_("Graph 1 Placeholder"))
        self.graph2_label = ctk.CTkLabel(self.graph2_frame, text=_("Graph 2 Placeholder"))

    def place_widgets(self):
        # Canvas pour défilement horizontal et vertical
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")

        # Configuration du grid pour permettre l'expansion
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Assurer que le canvas se redimensionne correctement avec le contenu
        self.scrollable_frame.bind("<Configure>",
                                   lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Uniformiser les espacements pour tous les éléments
        padding_top = 5
        padding_bottom = 5
        padding_x = 10

        # Colonnes pour trigramme, capteurs, unités, coefficients
        # Corrected typo: Use self.scrollable_frame.grid_columnconfigure
        self.scrollable_frame.grid_columnconfigure(0, weight=1, minsize=250)  # Trigram column
        self.scrollable_frame.grid_columnconfigure(1, weight=2,
                                                   minsize=600)  # Sensors column (increased weight and minsize)
        self.scrollable_frame.grid_columnconfigure(2, weight=1, minsize=450)  # Units column
        self.scrollable_frame.grid_columnconfigure(3, weight=1, minsize=350)  # Coefficients column

        # Trigramme
        self.trigramme_title.grid(row=0, column=0, padx=padding_x, pady=(padding_top, 2), sticky="w")
        self.trigramme_frame.grid(row=1, column=0, padx=padding_x, pady=(2, padding_bottom), sticky="nw")
        self.trigramme_label.grid(row=0, column=0, padx=5, pady=5)
        self.trigramme_entry.grid(row=0, column=1, padx=5, pady=5)
        self.trigramme_button.grid(row=1, column=0, padx=5, pady=5)
        self.trigramme_status.grid(row=1, column=1, padx=5, pady=5)

        # Capteurs
        self.capteurs_title.grid(row=0, column=1, padx=padding_x, pady=(padding_top, 2), sticky="w")
        self.capteurs_manager.grid(row=1, column=1, padx=padding_x, pady=(2, padding_bottom), sticky="nsew")

        # Unités
        self.unites_title.grid(row=0, column=2, padx=padding_x, pady=(padding_top, 2), sticky="w")
        self.unites_frame.grid(row=1, column=2, padx=padding_x, pady=(2, padding_bottom), sticky="nw")
        self.unit_capteurs_label.grid(row=0, column=0, padx=5, pady=5)
        self.unit_capteurs_entry.grid(row=0, column=1, padx=5, pady=5)
        self.unit_ref_label.grid(row=1, column=0, padx=5, pady=5)
        self.unit_ref_entry.grid(row=1, column=1, padx=5, pady=5)
        self.nom_ref_label.grid(row=2, column=0, padx=5, pady=5)
        self.nom_ref_entry.grid(row=2, column=1, padx=5, pady=5)
        self.unites_button.grid(row=3, column=0, padx=5, pady=5)
        self.unites_status.grid(row=3, column=1, padx=5, pady=5)

        # Coefficients
        self.coefficients_title.grid(row=0, column=3, padx=padding_x, pady=(padding_top, 2), sticky="w")
        self.coefficients_frame.grid(row=1, column=3, padx=padding_x, pady=(2, padding_bottom), sticky="nw")
        self.coefficients_subtitle.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        self.coef_a_label.grid(row=1, column=0, padx=5, pady=5)
        self.coef_a_entry.grid(row=1, column=1, padx=5, pady=5)
        self.coef_b_label.grid(row=2, column=0, padx=5, pady=5)
        self.coef_b_entry.grid(row=2, column=1, padx=5, pady=5)
        self.coefficients_button.grid(row=3, column=0, padx=5, pady=5)
        self.coefficients_status.grid(row=3, column=1, padx=5, pady=5)

        # Liste des fichiers et traitement - with scrollbars handled in create_widgets
        self.files_list_title.grid(row=2, column=0, padx=padding_x, pady=(padding_top, 2), sticky="w")
        self.treatment_title.grid(row=2, column=0, padx=(300, padding_x), pady=(padding_top, 2),
                                  sticky="w")  # Note: This placement might need adjustment

        # Cadre contenant les deux sections
        self.files_treatment_frame.grid(row=3, column=0, padx=padding_x, pady=(2, padding_bottom), sticky="nsew")
        self.files_treatment_frame.columnconfigure(0, weight=1)
        self.files_treatment_frame.columnconfigure(1, weight=2)

        # Section des fichiers (Listbox and scrollbars placed within files_list_frame using grid in create_widgets)
        self.files_list_frame.grid(row=0, column=0, padx=5, pady=5,
                                   sticky="nsew")  # Place the frame containing the listbox and scrollbars

        # Section de traitement (Textbox and scrollbars placed within treatment_frame using grid in create_widgets)
        self.treatment_frame.grid(row=0, column=1, padx=5, pady=5,
                                  sticky="nsew")  # Place the frame containing the textbox and scrollbars

        # Graphiques - avec espacements uniformes
        self.graph_title.grid(row=4, column=0, padx=padding_x, pady=(padding_top, 2), sticky="w")
        self.graph_frame.grid(row=5, column=0, padx=padding_x, pady=(2, padding_bottom), sticky="nsew")
        self.graph_frame.grid_columnconfigure((0, 1), weight=1)
        self.graph1_frame.grid(row=0, column=0, padx=10, sticky="nsew")
        self.graph2_frame.grid(row=0, column=1, padx=10, sticky="nsew")
        self.graph1_label.pack(pady=130)
        self.graph2_label.pack(pady=130)

    def afficher_liste_fichiers(self):
        # Use tk.END for Listbox delete and insert
        self.files_listbox.delete(0, tk.END) # Clear the listbox
        for fichier in glob.glob(os.path.join(self.current_dir, "*.csv")):
            self.files_listbox.insert(tk.END, os.path.basename(fichier)) # Insert items at the end

        # No need to configure state for tk.Listbox for selection

        if not self.files_listbox.get(0, tk.END): # Check if listbox is empty
            logger.warning(_("No CSV files found in directory: {}").format(self.current_dir))


    def initialiser_selection_listbox(self):
        if self.files_listbox.size() > 0: # Check if listbox has items
            self.files_listbox.select_set(0) # Select the first item (index 0)
            self.files_listbox.activate(0) # Activate the first item (optional, but can help focus)
            self.on_file_select(None) # Trigger the selection handler

    def nom_fichier_selectionne(self):
        selected_indices = self.files_listbox.curselection() # Get tuple of selected indices
        if not selected_indices:
            messagebox.showwarning(_("No Selection"), _("Please select a file from the list."))
            return None
        # Get the item at the selected index
        selected_file_name = self.files_listbox.get(selected_indices[0])
        return selected_file_name

    def on_file_select(self, event):
        selected_file = self.nom_fichier_selectionne()
        if selected_file:
            logger.info(_("File selected: {}").format(selected_file))
            resultat = self.traitement_fichier(selected_file)
            self.treatment_text.configure(state="normal")
            self.treatment_text.delete("0.0", "end")
            self.treatment_text.insert("0.0", resultat)
            self.treatment_text.configure(state="disabled")

    def traitement_fichier(self, fichier):
        try:
            resultat = f"Processing file: {fichier}\n"
            # À implémenter avec FonctionsCSV et FonctionsSignal
            return resultat
        except Exception as e:
            erreur = _("Error processing file: {}").format(str(e))
            logger.error(erreur)
            return erreur

    def valider_trigramme(self):
        trigramme = self.trigramme_var.get()
        if len(trigramme) != 3 or not trigramme.isalpha():
            logger.error(_("Trigram must be exactly 3 letters."))
            messagebox.showerror(_("Validation Error"), _("Trigram must be exactly 3 letters."))
            self.trigramme_var.set("Bbu")
            self.set_state("trigramme_valide", False)
        else:
            logger.info(_("Trigram validated: {}").format(trigramme))
            self.set_state("trigramme_valide", True)
        self.update_pdf_button()

    def valider_unites(self):
        unit = self.unit_capteurs_var.get().strip()
        unit_ref = self.unit_ref_var.get().strip()
        nom_ref = self.nom_ref_var.get().strip()
        if not unit or not unit_ref or not nom_ref:
            logger.error(_("Units and reference name must be provided."))
            messagebox.showerror(_("Validation Error"), _("Units and reference name must be provided."))
            self.set_state("unites_valides", False)
        else:
            logger.info(_("Units validated: Sensor: {}, Ref: {}, Ref Name: {}").format(unit, unit_ref, nom_ref))
            self.set_state("unites_valides", True)
        self.update_pdf_button()

    def valider_coefficients(self):
        try:
            coef_a = float(self.coef_a_var.get().strip())
            coef_b = float(self.coef_b_var.get().strip())
            if coef_a == 0:
                logger.error(_("Coefficient a cannot be zero."))
                messagebox.showerror(_("Validation Error"), _("Coefficient a cannot be zero."))
                self.set_state("coefficients_valides", False)
            else:
                logger.info(_("Coefficients validated: a={}, b={}").format(coef_a, coef_b))
                self.set_state("coefficients_valides", True)
        except ValueError:
            logger.error(_("Coefficients must be valid numbers."))
            messagebox.showerror(_("Validation Error"), _("Coefficients must be valid numbers."))
            self.set_state("coefficients_valides", False)
        self.update_pdf_button()

    def update_status_labels(self):
        self.trigramme_status.configure(text="✅" if self.state["trigramme_valide"] else "❌")
        self.unites_status.configure(text="✅" if self.state["unites_valides"] else "❌")
        self.coefficients_status.configure(text="✅" if self.state["coefficients_valides"] else "❌")
        self.capteurs_manager.status_label.configure(text="✅" if self.state["capteurs_valides"] else "❌")

    def update_pdf_button(self):
        pass  # À implémenter plus tard

    def refresh(self):
        self.trigramme_title.configure(text=_("Trigram"))
        self.trigramme_label.configure(text=_("Name (Trigram):"))
        self.trigramme_button.configure(text=_("Validate"))
        self.capteurs_title.configure(text=_("Sensors"))
        self.unit_capteurs_label.configure(text=_("Unit (Sensor):"))
        self.unit_ref_label.configure(text=_("Unit (Ref Sensor):"))
        self.nom_ref_label.configure(text=_("Name (Ref Sensor):"))
        self.unites_title.configure(text=_("Units"))
        self.unites_button.configure(text=_("Validate Units"))
        self.coefficients_title.configure(text=_("Coefficients"))
        self.coefficients_subtitle.configure(text=_("Reference Sensor Conversion Coefficients"))
        self.coef_a_label.configure(text=_("Coefficient a:"))
        self.coef_b_label.configure(text=_("Coefficient b:"))
        self.coefficients_button.configure(text=_("Validate Coefficients"))
        self.files_list_title.configure(text=_("List of Files:"))
        self.treatment_title.configure(text=_("File Processing:"))
        self.graph_title.configure(text=_("Graphs"))
        self.graph1_label.configure(text=_("Graph 1 Placeholder"))
        self.graph2_label.configure(text=_("Graph 2 Placeholder"))
        self.capteurs_manager.refresh()