# core/views/tabs/processing_tab.py
import customtkinter as ctk
import re
import os
import glob
from tkinter import messagebox
import tkinter as tk
from ...utils.i18n import _
import logging

logger = logging.getLogger('Sensorem')

class CapteurFrame(ctk.CTkFrame):
    def __init__(self, master, capteurs_manager, is_first=False, **kwargs):
        super().__init__(master, **kwargs)
        self.capteurs_manager = capteurs_manager
        self.nom_var = ctk.StringVar()
        self.debut_var = ctk.StringVar()
        self.is_first = is_first
        self.create_widgets()
        self.place_widgets()

    def create_widgets(self):
        self.nom_label = ctk.CTkLabel(self, text=_("Sensor Name:"))
        self.nom_entry = ctk.CTkEntry(self, textvariable=self.nom_var, width=120)
        self.nom_entry.bind("<FocusIn>", self.capteurs_manager.processing_tab.restore_file_selection)
        self.debut_label = ctk.CTkLabel(self, text=_("Start Line:"))
        self.debut_entry = ctk.CTkEntry(self, textvariable=self.debut_var, width=70)
        self.debut_entry.bind("<FocusIn>", self.capteurs_manager.processing_tab.restore_file_selection)
        if not self.is_first:
            self.delete_button = ctk.CTkButton(self, text="🗑️ " + _("Delete"), command=self.supprimer, width=70)

    def place_widgets(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_columnconfigure(3, weight=1)
        if not self.is_first:
            self.grid_columnconfigure(4, weight=0)

        self.nom_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.nom_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.debut_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.debut_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        if not self.is_first:
            self.delete_button.grid(row=0, column=4, padx=5, pady=5, sticky="w")

    def supprimer(self):
        self.capteurs_manager.remove_capteur(self)

    def get_values(self):
        return self.nom_var.get(), self.debut_var.get()

    def set_values(self, nom, debut):
        self.nom_var.set(nom)
        self.debut_var.set(debut)

    def reset(self):
        self.set_values("", "")

class CapteursManager(ctk.CTkFrame):
    def __init__(self, parent, processing_tab, **kwargs):
        super().__init__(parent, **kwargs)
        self.processing_tab = processing_tab
        self.capteurs = []
        self.create_widgets()
        self.add_capteur("H_", "0", is_first=True)

    def create_widgets(self):
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(fill="x", pady=2)
        self.add_button = ctk.CTkButton(self.button_frame, text=_("Add Sensor"), command=lambda: self.add_capteur())
        self.add_button.pack(side="left", padx=5)
        self.validate_button = ctk.CTkButton(self.button_frame, text=_("Validate Sensors"), command=self.valider_capteurs)
        self.validate_button.pack(side="left", padx=5)
        self.status_label = ctk.CTkLabel(self.button_frame, text="❌")
        self.status_label.pack(side="left", padx=5)
        self.capteurs_container = ctk.CTkScrollableFrame(self, height=150)
        self.capteurs_container.pack(fill="both", expand=True, pady=2)

    def add_capteur(self, nom="", debut="", is_first=False):
        capteur = CapteurFrame(self.capteurs_container, self, is_first=is_first)
        capteur.pack(fill="x", pady=2)
        self.capteurs.append(capteur)
        if nom and debut:
            capteur.set_values(nom, debut)
        self.capteurs_container.update_idletasks()

    def remove_capteur(self, capteur):
        if capteur != self.capteurs[0]:
            self.capteurs.remove(capteur)
            capteur.destroy()
            self.capteurs_container.update_idletasks()

    def valider_capteurs(self):
        values = [capteur.get_values() for capteur in self.capteurs]
        try:
            self.processing_tab.controller.validate_sensors(values)
            self.status_label.configure(text="✅")
        except ValueError as e:
            logger.error(str(e))
            messagebox.showerror(_("Validation Error"), str(e))
            self.status_label.configure(text="❌")
        self.processing_tab.update_pdf_button()

    def reset_capteurs(self):
        for capteur in self.capteurs[1:]:
            capteur.destroy()
        self.capteurs = [self.capteurs[0]]
        self.capteurs[0].reset()
        self.status_label.configure(text="❌")
        self.processing_tab.controller.model.reset_validations()
        self.processing_tab.update_pdf_button()

    def refresh(self):
        self.add_button.configure(text=_("Add Sensor"))
        self.validate_button.configure(text=_("Validate Sensors"))
        for capteur in self.capteurs:
            capteur.nom_label.configure(text=_("Sensor Name:"))
            capteur.debut_label.configure(text=_("Start Line:"))
            if not capteur.is_first:
                capteur.delete_button.configure(text="🗑️ " + _("Delete"))

class ProcessingTab(ctk.CTkScrollableFrame):
    def __init__(self, parent, controller, load_csv_callback):
        super().__init__(parent)
        self.configure(fg_color=("gray90", "gray13"), corner_radius=0)
        self.controller = controller
        self.load_csv_callback = load_csv_callback
        self.current_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
        logger.info(f"Chemin du dossier Sensorem : {self.current_dir}")
        if not os.path.exists(self.current_dir):
            logger.error(f"Dossier Sensorem non trouvé : {self.current_dir}")
        self.selected_file_index = None
        self._processing_selection = False
        self.create_widgets()
        self.place_widgets()
        self.afficher_liste_fichiers()
        self.after(200, self.initialiser_selection_listbox)

    def update_status_labels(self, trigram_valid, sensors_valid, units_valid, coefficients_valid):
        logger.debug(
            f"Updating status labels: trigram={trigram_valid}, sensors={sensors_valid}, units={units_valid}, coefficients={coefficients_valid}")
        self.trigramme_status.configure(text="✅" if trigram_valid else "❌")
        self.capteurs_manager.status_label.configure(text="✅" if sensors_valid else "❌")
        self.unites_status.configure(text="✅" if units_valid else "❌")
        self.coefficients_status.configure(text="✅" if coefficients_valid else "❌")

    def create_widgets(self):
        title_font = ("Roboto", 18, "bold")
        bg_color = ("gray85", "gray25")

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
        self.trigramme_entry.bind("<FocusIn>", self.restore_file_selection)
        self.trigramme_button = ctk.CTkButton(self.trigramme_frame, text=_("Validate"), command=self.valider_trigramme, width=80)
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
        self.unit_capteurs_entry.bind("<FocusIn>", self.restore_file_selection)
        self.unit_ref_label = ctk.CTkLabel(self.unites_frame, text=_("Unit (Ref Sensor):"))
        self.unit_ref_var = ctk.StringVar(value="[m/s]")
        self.unit_ref_entry = ctk.CTkEntry(self.unites_frame, textvariable=self.unit_ref_var, width=80)
        self.unit_ref_entry.bind("<FocusIn>", self.restore_file_selection)
        self.nom_ref_label = ctk.CTkLabel(self.unites_frame, text=_("Name (Ref Sensor):"))
        self.nom_ref_var = ctk.StringVar(value="Venturi")
        self.nom_ref_entry = ctk.CTkEntry(self.unites_frame, textvariable=self.nom_ref_var, width=100)
        self.nom_ref_entry.bind("<FocusIn>", self.restore_file_selection)
        self.unites_button = ctk.CTkButton(self.unites_frame, text=_("Validate Units"), command=self.valider_unites)
        self.unites_status = ctk.CTkLabel(self.unites_frame, text="❌")

        # Coefficients
        self.coefficients_title = ctk.CTkLabel(self.scrollable_frame, text=_("Coefficients"), font=title_font)
        self.coefficients_frame = ctk.CTkFrame(self.scrollable_frame, fg_color=bg_color, border_width=2)
        self.coefficients_subtitle = ctk.CTkLabel(self.coefficients_frame, text=_("Reference Sensor Conversion Coefficients"))
        self.coef_a_label = ctk.CTkLabel(self.coefficients_frame, text=_("Coefficient a:"))
        self.coef_a_var = ctk.StringVar(value="1.0")
        self.coef_a_entry = ctk.CTkEntry(self.coefficients_frame, textvariable=self.coef_a_var, width=80)
        self.coef_a_entry.bind("<FocusIn>", self.restore_file_selection)
        self.coef_b_label = ctk.CTkLabel(self.coefficients_frame, text=_("Coefficient b:"))
        self.coef_b_var = ctk.StringVar(value="0.0")
        self.coef_b_entry = ctk.CTkEntry(self.coefficients_frame, textvariable=self.coef_b_var, width=80)
        self.coef_b_entry.bind("<FocusIn>", self.restore_file_selection)
        self.coefficients_button = ctk.CTkButton(self.coefficients_frame, text=_("Validate Coefficients"), command=self.valider_coefficients)
        self.coefficients_status = ctk.CTkLabel(self.coefficients_frame, text="❌")

        # Liste des fichiers et traitement
        self.files_treatment_frame = ctk.CTkFrame(self)

        # Liste des fichiers
        self.files_list_title = ctk.CTkLabel(self, text=_("List of Files:"), font=title_font)
        self.files_list_frame = ctk.CTkFrame(self.files_treatment_frame, fg_color=bg_color)
        self.files_list_v_scrollbar = tk.Scrollbar(self.files_list_frame, orient=tk.VERTICAL)
        self.files_list_h_scrollbar = tk.Scrollbar(self.files_list_frame, orient=tk.HORIZONTAL)
        self.files_listbox = tk.Listbox(
            self.files_list_frame,
            height=10,
            width=30,
            selectmode=tk.SINGLE,
            bd=0,
            highlightthickness=0,
            bg=self.files_list_frame.cget("fg_color")[0],
            fg=ctk.CTkLabel(self).cget("text_color")[0],
            yscrollcommand=self.files_list_v_scrollbar.set,
            xscrollcommand=self.files_list_h_scrollbar.set
        )
        self.files_list_v_scrollbar.config(command=self.files_listbox.yview)
        self.files_list_h_scrollbar.config(command=self.files_listbox.xview)
        self.files_listbox.grid(row=0, column=0, sticky="nsew")
        self.files_list_v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.files_list_h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.files_list_frame.grid_columnconfigure(0, weight=1)
        self.files_list_frame.grid_rowconfigure(0, weight=1)
        self.files_listbox.bind("<<ListboxSelect>>", self.on_file_select)

        # Traitement
        self.treatment_title = ctk.CTkLabel(self, text=_("File Processing:"), font=title_font)
        self.treatment_frame = ctk.CTkFrame(self.files_treatment_frame, fg_color=bg_color)
        self.treatment_v_scrollbar = ctk.CTkScrollbar(self.treatment_frame, orientation="vertical")
        self.treatment_h_scrollbar = ctk.CTkScrollbar(self.treatment_frame, orientation="horizontal")
        self.treatment_text = ctk.CTkTextbox(
            self.treatment_frame,
            height=150,
            state="disabled",
            yscrollcommand=self.treatment_v_scrollbar.set,
            xscrollcommand=self.treatment_h_scrollbar.set
        )
        self.treatment_v_scrollbar.configure(command=self.treatment_text.yview)
        self.treatment_h_scrollbar.configure(command=self.treatment_text.xview)
        self.treatment_text.grid(row=0, column=0, sticky="nsew")
        self.treatment_v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.treatment_h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.treatment_frame.grid_columnconfigure(0, weight=1)
        self.treatment_frame.grid_rowconfigure(0, weight=1)

        # Graphiques
        self.graph_title = ctk.CTkLabel(self, text=_("Graphs"), font=title_font)
        self.graph_frame = ctk.CTkFrame(self, fg_color=bg_color)
        self.graph1_frame = ctk.CTkFrame(self.graph_frame, border_width=2, width=300, height=300)
        self.graph2_frame = ctk.CTkFrame(self.graph_frame, border_width=2, width=300, height=300)
        self.graph1_label = ctk.CTkLabel(self.graph1_frame, text=_("Graph 1 Placeholder"))
        self.graph2_label = ctk.CTkLabel(self.graph2_frame, text=_("Graph 2 Placeholder"))

    def place_widgets(self):
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        padding_top = 2
        padding_bottom = 2
        padding_x = 10

        self.scrollable_frame.grid_columnconfigure(0, weight=1, minsize=250)
        self.scrollable_frame.grid_columnconfigure(1, weight=2, minsize=600)
        self.scrollable_frame.grid_columnconfigure(2, weight=1, minsize=450)
        self.scrollable_frame.grid_columnconfigure(3, weight=1, minsize=350)

        self.trigramme_title.grid(row=0, column=0, padx=padding_x, pady=(padding_top, 2), sticky="w")
        self.trigramme_frame.grid(row=1, column=0, padx=padding_x, pady=(2, padding_bottom), sticky="nw")
        self.trigramme_label.grid(row=0, column=0, padx=5, pady=5)
        self.trigramme_entry.grid(row=0, column=1, padx=5, pady=5)
        self.trigramme_button.grid(row=1, column=0, padx=5, pady=5)
        self.trigramme_status.grid(row=1, column=1, padx=5, pady=5)

        self.capteurs_title.grid(row=0, column=1, padx=padding_x, pady=(padding_top, 2), sticky="w")
        self.capteurs_manager.grid(row=1, column=1, padx=padding_x, pady=(2, padding_bottom), sticky="nsew")

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

        self.coefficients_title.grid(row=0, column=3, padx=padding_x, pady=(padding_top, 2), sticky="w")
        self.coefficients_frame.grid(row=1, column=3, padx=padding_x, pady=(2, padding_bottom), sticky="nw")
        self.coefficients_subtitle.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        self.coef_a_label.grid(row=1, column=0, padx=5, pady=5)
        self.coef_a_entry.grid(row=1, column=1, padx=5, pady=5)
        self.coef_b_label.grid(row=2, column=0, padx=5, pady=5)
        self.coef_b_entry.grid(row=2, column=1, padx=5, pady=5)
        self.coefficients_button.grid(row=3, column=0, padx=5, pady=5)
        self.coefficients_status.grid(row=3, column=1, padx=5, pady=5)

        self.files_list_title.grid(row=2, column=0, padx=padding_x, pady=(padding_top, 2), sticky="w")
        self.treatment_title.grid(row=2, column=0, padx=(300, padding_x), pady=(padding_top, 2), sticky="w")
        self.files_treatment_frame.grid(row=3, column=0, padx=padding_x, pady=(2, padding_bottom), sticky="nsew")
        self.files_treatment_frame.columnconfigure(0, weight=1)
        self.files_treatment_frame.columnconfigure(1, weight=2)
        self.files_list_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.treatment_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        self.graph_title.grid(row=4, column=0, padx=padding_x, pady=(padding_top, 2), sticky="w")
        self.graph_frame.grid(row=5, column=0, padx=padding_x, pady=(2, padding_bottom), sticky="nsew")
        self.graph_frame.grid_columnconfigure((0, 1), weight=1)
        self.graph1_frame.grid(row=0, column=0, padx=10, sticky="nsew")
        self.graph2_frame.grid(row=0, column=1, padx=10, sticky="nsew")
        self.graph1_label.pack(pady=130)
        self.graph2_label.pack(pady=130)

    def afficher_liste_fichiers(self):
        self.files_listbox.delete(0, tk.END)
        for fichier in self.controller.list_csv_files():
            self.files_listbox.insert(tk.END, fichier)
        if not self.files_listbox.get(0, tk.END):
            logger.warning(_("No CSV files found in directory: {}").format(self.current_dir))

    def initialiser_selection_listbox(self):
        logger.debug(_("Initializing listbox selection"))
        if self.files_listbox.size() > 0:
            self.files_listbox.select_set(0)
            self.files_listbox.activate(0)
            self.selected_file_index = 0
            self.after(50, lambda: self.on_file_select(None))
        else:
            logger.debug(_("No files to select"))

    def restore_file_selection(self, event=None):
        logger.debug(_("Restoring selection: index={}").format(self.selected_file_index))
        if self._processing_selection:
            logger.debug(_("Restoration blocked: _processing_selection is True"))
            return
        if self.selected_file_index is not None and self.files_listbox.size() > self.selected_file_index:
            self._processing_selection = True
            try:
                current_selection = self.files_listbox.curselection()
                if current_selection != (self.selected_file_index,):
                    self.files_listbox.select_set(self.selected_file_index)
                    self.files_listbox.activate(self.selected_file_index)
                    logger.debug(_("Selection restored to index {}").format(self.selected_file_index))
            finally:
                self._processing_selection = False
        else:
            logger.debug(_("No selection to restore or invalid index"))

    def nom_fichier_selectionne(self):
        logger.debug(_("Checking selected file"))
        selected_indices = self.files_listbox.curselection()
        if not selected_indices and self.selected_file_index is not None:
            logger.debug(_("Returning to previous selection: index={}").format(self.selected_file_index))
            return self.files_listbox.get(self.selected_file_index)
        if not selected_indices:
            logger.warning(_("No file selected in the list"))
            messagebox.showwarning(_("No Selection"), _("Please select a file from the list."))
            return None
        self.selected_file_index = selected_indices[0]
        selected_file = self.files_listbox.get(self.selected_file_index)
        logger.debug(_("File selected: {}").format(selected_file))
        return selected_file

    def on_file_select(self, event):
        logger.debug(_("Event triggered: selection"))
        if self._processing_selection:
            logger.debug(_("Event blocked: _processing_selection is True"))
            return
        self._processing_selection = True
        try:
            selected_file = self.nom_fichier_selectionne()
            if selected_file:
                logger.info(_("File selected: {}").format(selected_file))
                try:
                    self.load_csv_callback(selected_file)  # Passer le nom du fichier
                    resultat = _("File loaded successfully: {}").format(selected_file)
                    self.treatment_text.configure(state="normal")
                    self.treatment_text.delete("1.0", "end")
                    self.treatment_text.insert("1.0", resultat)
                    self.treatment_text.configure(state="disabled")
                except Exception as e:
                    logger.error(_("Error loading file: {}").format(str(e)))
                    messagebox.showerror(_("Error"), _("Error loading file: {}").format(str(e)))
            else:
                logger.debug(_("No file selected for processing"))
        finally:
            self._processing_selection = False
            logger.debug(_("Selection event completed"))

    def valider_trigramme(self):
        try:
            self.controller.validate_trigram(self.trigramme_var.get())
            self.trigramme_status.configure(text="✅")
        except ValueError as e:
            logger.error(str(e))
            messagebox.showerror(_("Validation Error"), str(e))
            self.trigramme_var.set("Bbu")
            self.trigramme_status.configure(text="❌")
        self.update_pdf_button()

    def valider_unites(self):
        try:
            self.controller.validate_units(
                self.unit_capteurs_var.get().strip(),
                self.unit_ref_var.get().strip(),
                self.nom_ref_var.get().strip()
            )
            self.unites_status.configure(text="✅")
        except ValueError as e:
            logger.error(str(e))
            messagebox.showerror(_("Validation Error"), str(e))
            self.unites_status.configure(text="❌")
        self.update_pdf_button()

    def valider_coefficients(self):
        try:
            self.controller.validate_coefficients(
                self.coef_a_var.get().strip(),
                self.coef_b_var.get().strip()
            )
            self.coefficients_status.configure(text="✅")
        except ValueError as e:
            logger.error(str(e))
            messagebox.showerror(_("Validation Error"), str(e))
            self.coefficients_status.configure(text="❌")
        self.update_pdf_button()

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
        self.afficher_liste_fichiers()