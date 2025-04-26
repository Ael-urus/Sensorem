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

# Define standard fonts
STANDARD_FONT = ("Roboto", 12)
LISTBOX_FONT = ("Roboto", 13)  # Augmenté à 13 pour correspondre visuellement à ctk.CTkLabel
TITLE_FONT = ("Roboto", 18, "bold")
SUBTITLE_FONT = ("Roboto", 14, "bold")

# Define padding constants
PADDING_SECTION_Y = 20  # Vertical padding between main sections
PADDING_FRAME_X = 5     # Horizontal padding around frames within sections
PADDING_FRAME_Y = 5     # Vertical padding around frames within sections (nouveau)
PADDING_WIDGET_X = 5    # Horizontal padding around widgets within frames
PADDING_WIDGET_Y = 5    # Vertical padding around widgets within frames


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
        self.nom_label = ctk.CTkLabel(self, text=_("Sensor Name:"), font=STANDARD_FONT, wraplength=100)
        self.nom_entry = ctk.CTkEntry(self, textvariable=self.nom_var, width=100, font=STANDARD_FONT)
        self.nom_entry.bind("<FocusIn>", self.capteurs_manager.processing_tab.restore_file_selection)
        self.debut_label = ctk.CTkLabel(self, text=_("Start Line:"), font=STANDARD_FONT)
        self.debut_entry = ctk.CTkEntry(self, textvariable=self.debut_var, width=100, font=STANDARD_FONT)
        self.debut_entry.bind("<FocusIn>", self.capteurs_manager.processing_tab.restore_file_selection)
        if not self.is_first:
            self.delete_button = ctk.CTkButton(self, text="🗑️ " + _("Delete"), command=self.supprimer, width=70, font=STANDARD_FONT)

    def place_widgets(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_columnconfigure(3, weight=1)
        if not self.is_first:
            self.grid_columnconfigure(4, weight=0)

        self.nom_label.grid(row=0, column=0, padx=(PADDING_WIDGET_X, PADDING_WIDGET_X), pady=PADDING_WIDGET_Y, sticky="w")
        self.nom_entry.grid(row=0, column=1, padx=(0, PADDING_WIDGET_X), pady=PADDING_WIDGET_Y, sticky="w")
        self.debut_label.grid(row=0, column=2, padx=(PADDING_WIDGET_X, PADDING_WIDGET_X), pady=PADDING_WIDGET_Y, sticky="w")
        self.debut_entry.grid(row=0, column=3, padx=(0, PADDING_WIDGET_X), pady=PADDING_WIDGET_Y, sticky="w")
        if not self.is_first:
            self.delete_button.grid(row=0, column=4, padx=PADDING_WIDGET_X, pady=PADDING_WIDGET_Y, sticky="w")


    def supprimer(self):
        self.capteurs_manager.remove_capteur(self)

    def get_values(self):
        return self.nom_var.get(), self.debut_var.get()

    def set_values(self, nom, debut):
        self.nom_var.set(nom)
        self.debut_var.set(debut)

    def reset(self):
        self.set_values("", "")

    def refresh(self):
        self.nom_label.configure(text=_("Sensor Name:"))
        self.debut_label.configure(text=_("Start Line:"))
        if not self.is_first:
            self.delete_button.configure(text="🗑️ " + _("Delete"))


class CapteursManager(ctk.CTkFrame):
    def __init__(self, parent, processing_tab, **kwargs):
        super().__init__(parent, **kwargs)
        self.processing_tab = processing_tab
        self.capteurs = []
        self.create_widgets()
        self.add_capteur("H_1", "5", is_first=True)

    def create_widgets(self):
        # Frame pour les boutons
        self.button_frame = ctk.CTkFrame(self, width=400, fg_color="transparent")
        self.button_frame.pack(fill="x", padx=PADDING_FRAME_X, pady=(PADDING_FRAME_Y, 0))
        self.add_button = ctk.CTkButton(self.button_frame, text=_("Add Sensor"), command=lambda: self.add_capteur(), font=STANDARD_FONT, width=120)
        self.add_button.pack(side="left", padx=(PADDING_WIDGET_X, PADDING_WIDGET_X))
        self.validate_button = ctk.CTkButton(self.button_frame, text=_("Validate Sensors"), command=self.valider_capteurs, font=STANDARD_FONT, width=120)
        self.validate_button.pack(side="left", padx=PADDING_WIDGET_X)
        self.status_label = ctk.CTkLabel(self.button_frame, text="❌", font=STANDARD_FONT)
        self.status_label.pack(side="left", padx=PADDING_WIDGET_X)

        # Frame pour contenir le Canvas et les barres de défilement
        self.scroll_container = ctk.CTkFrame(self, fg_color="transparent")
        self.scroll_container.pack(fill="both", expand=True, padx=PADDING_FRAME_X, pady=(0, PADDING_FRAME_Y))

        # Canvas pour le contenu défilant
        self.canvas = tk.Canvas(self.scroll_container, highlightthickness=0, width=400)
        self.v_scrollbar = ctk.CTkScrollbar(self.scroll_container, orientation="vertical", command=self.canvas.yview)
        self.h_scrollbar = ctk.CTkScrollbar(self.scroll_container, orientation="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        # Frame interne pour contenir les CapteurFrame
        self.capteurs_container = ctk.CTkFrame(self.canvas, fg_color="transparent", width=400)
        self.canvas_frame_id = self.canvas.create_window((0, 0), window=self.capteurs_container, anchor="nw")

        # Configuration de la grille pour le scroll_container
        self.scroll_container.grid_columnconfigure(0, weight=1)
        self.scroll_container.grid_rowconfigure(0, weight=1)
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=PADDING_FRAME_X, pady=PADDING_FRAME_Y)  # Ajout de padding pour la bordure
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        # Lier la mise à jour de la région de défilement
        self.capteurs_container.bind("<Configure>", self.update_scrollregion)
        self.canvas.bind("<Configure>", self.update_canvas_width)

    def update_scrollregion(self, event=None):
        self.canvas.configure(scrollregion=(0, 0, self.capteurs_container.winfo_reqwidth(), self.capteurs_container.winfo_reqheight()))

    def update_canvas_width(self, event=None):
        canvas_width = max(self.canvas.winfo_width(), self.capteurs_container.winfo_reqwidth(), 400)
        self.canvas.itemconfig(self.canvas_frame_id, width=canvas_width)

    def add_capteur(self, nom="", debut="", is_first=False):
        capteur = CapteurFrame(self.capteurs_container, self, is_first=is_first)
        row_num = len(self.capteurs)
        capteur.grid(row=row_num, column=0, padx=PADDING_FRAME_X, pady=PADDING_FRAME_Y, sticky="ew")
        self.capteurs.append(capteur)
        if nom or debut:
            capteur.set_values(nom, debut)
        self.update_scrollregion()

    def remove_capteur(self, capteur):
        if capteur != self.capteurs[0]:
            self.capteurs.remove(capteur)
            capteur.destroy()
            for i, remaining_capteur in enumerate(self.capteurs):
                remaining_capteur.grid(row=i, column=0, padx=PADDING_FRAME_X, pady=PADDING_FRAME_Y, sticky="ew")
            self.update_scrollregion()

    def valider_capteurs(self):
        values = [capteur.get_values() for capteur in self.capteurs]
        try:
            for nom, debut in values:
                if not nom or not debut.isdigit():
                    raise ValueError(_("Sensor name and start line must be non-empty and start line must be a number"))
            self.status_label.configure(text="✅")
            self.processing_tab.update_status_labels(
                self.processing_tab.trigramme_status.cget("text") == "✅",
                True,
                self.processing_tab.unites_status.cget("text") == "✅",
                self.processing_tab.coefficients_status.cget("text") == "✅"
            )
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
        self.update_scrollregion()

    def refresh(self):
        self.add_button.configure(text=_("Add Sensor"))
        self.validate_button.configure(text=_("Validate Sensors"))
        self.status_label.configure(text=self.status_label.cget("text"))
        for capteur in self.capteurs:
            capteur.refresh()
        self.update_scrollregion()


class ProcessingTab(ctk.CTkScrollableFrame):
    def __init__(self, parent, controller, load_csv_callback):
        super().__init__(parent)
        self.configure(fg_color=("gray90", "gray13"), corner_radius=0)
        self.controller = controller
        self.load_csv_callback = load_csv_callback
        self.current_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, os.pardir))
        logger.info(f"Chemin du dossier Sensorem : {self.current_dir}")
        if not os.path.exists(self.current_dir):
            logger.error(f"Dossier Sensorem non trouvé : {self.current_dir}")
        self.selected_file_index = None
        self.current_selected_file = None
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
        bg_color = ("gray85", "gray25")

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=0, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.content_frame.grid_columnconfigure(0, weight=2)
        self.content_frame.grid_columnconfigure(1, weight=5)
        self.content_frame.grid_columnconfigure(2, weight=2)
        self.content_frame.grid_columnconfigure(3, weight=2)

        # Trigramme Section
        self.trigramme_title = ctk.CTkLabel(self.content_frame, text=_("Trigram"), font=TITLE_FONT)
        self.trigramme_frame = ctk.CTkFrame(self.content_frame, fg_color=bg_color, border_width=2)
        self.trigramme_label = ctk.CTkLabel(self.trigramme_frame, text=_("Name (Trigram):"), font=STANDARD_FONT, wraplength=120)
        self.trigramme_var = ctk.StringVar(value="Bbu")
        self.trigramme_entry = ctk.CTkEntry(self.trigramme_frame, textvariable=self.trigramme_var, width=80, font=STANDARD_FONT)
        self.trigramme_entry.bind("<FocusIn>", self.restore_file_selection)
        self.trigramme_button = ctk.CTkButton(self.trigramme_frame, text=_("Validate"), command=self.valider_trigramme, font=STANDARD_FONT)
        self.trigramme_status = ctk.CTkLabel(self.trigramme_frame, text="❌", font=STANDARD_FONT)

        # Capteurs Section
        self.capteurs_title = ctk.CTkLabel(self.content_frame, text=_("Sensors"), font=TITLE_FONT)
        self.capteurs_manager = CapteursManager(self.content_frame, self, fg_color=bg_color, border_width=2)

        # Unités Section
        self.unites_title = ctk.CTkLabel(self.content_frame, text=_("Units"), font=TITLE_FONT)
        self.unites_frame = ctk.CTkFrame(self.content_frame, fg_color=bg_color, border_width=2)
        self.unit_capteurs_label = ctk.CTkLabel(self.unites_frame, text=_("Unit (Sensor):"), font=STANDARD_FONT, wraplength=120)
        self.unit_capteurs_var = ctk.StringVar(value="[V]")
        self.unit_capteurs_entry = ctk.CTkEntry(self.unites_frame, textvariable=self.unit_capteurs_var, width=80, font=STANDARD_FONT)
        self.unit_capteurs_entry.bind("<FocusIn>", self.restore_file_selection)
        self.unit_ref_label = ctk.CTkLabel(self.unites_frame, text=_("Unit (Ref Sensor):"), font=STANDARD_FONT, wraplength=120)
        self.unit_ref_var = ctk.StringVar(value="[m/s]")
        self.unit_ref_entry = ctk.CTkEntry(self.unites_frame, textvariable=self.unit_ref_var, width=80, font=STANDARD_FONT)
        self.unit_ref_entry.bind("<FocusIn>", self.restore_file_selection)
        self.nom_ref_label = ctk.CTkLabel(self.unites_frame, text=_("Name (Ref Sensor):"), font=STANDARD_FONT, wraplength=120)
        self.nom_ref_var = ctk.StringVar(value="Venturi")
        self.nom_ref_entry = ctk.CTkEntry(self.unites_frame, textvariable=self.nom_ref_var, width=100, font=STANDARD_FONT)
        self.nom_ref_entry.bind("<FocusIn>", self.restore_file_selection)
        self.unites_button = ctk.CTkButton(self.unites_frame, text=_("Validate Units"), command=self.valider_unites, font=STANDARD_FONT)
        self.unites_status = ctk.CTkLabel(self.unites_frame, text="❌", font=STANDARD_FONT)

        # Coefficients Section
        self.coefficients_title = ctk.CTkLabel(self.content_frame, text=_("Coefficients"), font=TITLE_FONT)
        self.coefficients_frame = ctk.CTkFrame(self.content_frame, fg_color=bg_color, border_width=2)
        self.coefficients_subtitle = ctk.CTkLabel(self.coefficients_frame, text=_("Reference Sensor Conversion Coefficients"), font=SUBTITLE_FONT, wraplength=180)
        self.coef_a_label = ctk.CTkLabel(self.coefficients_frame, text=_("Coefficient a:"), font=STANDARD_FONT, wraplength=120)
        self.coef_a_var = ctk.StringVar(value="1.0")
        self.coef_a_entry = ctk.CTkEntry(self.coefficients_frame, textvariable=self.coef_a_var, width=80, font=STANDARD_FONT)
        self.coef_a_entry.bind("<FocusIn>", self.restore_file_selection)
        self.coef_b_label = ctk.CTkLabel(self.coefficients_frame, text=_("Coefficient b:"), font=STANDARD_FONT, wraplength=120)
        self.coef_b_var = ctk.StringVar(value="0.0")
        self.coef_b_entry = ctk.CTkEntry(self.coefficients_frame, textvariable=self.coef_b_var, width=80, font=STANDARD_FONT)
        self.coef_b_entry.bind("<FocusIn>", self.restore_file_selection)
        self.coefficients_button = ctk.CTkButton(self.coefficients_frame, text=_("Validate Coefficients"), command=self.valider_coefficients, font=STANDARD_FONT)
        self.coefficients_status = ctk.CTkLabel(self.coefficients_frame, text="❌", font=STANDARD_FONT)

        # Files List and Treatment Section
        self.files_treatment_title = ctk.CTkLabel(self.content_frame, text=_("Files and Processing"), font=TITLE_FONT)
        self.files_treatment_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.files_list_subtitle = ctk.CTkLabel(self.files_treatment_frame, text=_("Available Files:"), font=SUBTITLE_FONT)
        self.files_list_frame = ctk.CTkFrame(self.files_treatment_frame, fg_color=bg_color)
        self.files_list_v_scrollbar = ctk.CTkScrollbar(self.files_list_frame, orientation="vertical")
        self.files_list_h_scrollbar = ctk.CTkScrollbar(self.files_list_frame, orientation="horizontal")
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
            xscrollcommand=self.files_list_h_scrollbar.set,
            font=LISTBOX_FONT  # Utilisation de LISTBOX_FONT
        )
        self.files_list_v_scrollbar.configure(command=self.files_listbox.yview)
        self.files_list_h_scrollbar.configure(command=self.files_listbox.xview)
        self.treatment_text_subtitle = ctk.CTkLabel(self.files_treatment_frame, text=_("Processing Output:"), font=SUBTITLE_FONT)
        self.treatment_frame = ctk.CTkFrame(self.files_treatment_frame, fg_color=bg_color)
        self.treatment_v_scrollbar = ctk.CTkScrollbar(self.treatment_frame, orientation="vertical")
        self.treatment_h_scrollbar = ctk.CTkScrollbar(self.treatment_frame, orientation="horizontal")
        self.treatment_text = ctk.CTkTextbox(
            self.treatment_frame,
            height=150,
            state="disabled",
            yscrollcommand=self.treatment_v_scrollbar.set,
            xscrollcommand=self.treatment_h_scrollbar.set,
            font=STANDARD_FONT
        )
        self.treatment_v_scrollbar.configure(command=self.treatment_text.yview)
        self.treatment_h_scrollbar.configure(command=self.treatment_text.xview)

        # Graphiques Section
        self.graph_title = ctk.CTkLabel(self.content_frame, text=_("Graphs"), font=TITLE_FONT)
        self.graph_frame = ctk.CTkFrame(self.content_frame, fg_color=bg_color)
        self.graph1_frame = ctk.CTkFrame(self.graph_frame, border_width=2, corner_radius=8)
        self.graph2_frame = ctk.CTkFrame(self.graph_frame, border_width=2, corner_radius=8)
        self.graph1_label = ctk.CTkLabel(self.graph1_frame, text=_("Graph 1 Placeholder"), font=STANDARD_FONT)
        self.graph2_label = ctk.CTkLabel(self.graph2_frame, text=_("Graph 2 Placeholder"), font=STANDARD_FONT)

    def place_widgets(self):
        self.content_frame.grid(row=0, column=0, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        top_row_idx = 0

        self.trigramme_title.grid(row=top_row_idx, column=0, padx=PADDING_FRAME_X, pady=(PADDING_SECTION_Y, 2), sticky="w")
        self.trigramme_frame.grid(row=top_row_idx + 1, column=0, padx=PADDING_FRAME_X, pady=(0, PADDING_SECTION_Y), sticky="nsew")
        self.capteurs_title.grid(row=top_row_idx, column=1, padx=PADDING_FRAME_X, pady=(PADDING_SECTION_Y, 2), sticky="w")
        self.capteurs_manager.grid(row=top_row_idx + 1, column=1, padx=PADDING_FRAME_X, pady=(0, PADDING_SECTION_Y), sticky="nsew")
        self.unites_title.grid(row=top_row_idx, column=2, padx=PADDING_FRAME_X, pady=(PADDING_SECTION_Y, 2), sticky="w")
        self.unites_frame.grid(row=top_row_idx + 1, column=2, padx=PADDING_FRAME_X, pady=(0, PADDING_SECTION_Y), sticky="nsew")
        self.coefficients_title.grid(row=top_row_idx, column=3, padx=PADDING_FRAME_X, pady=(PADDING_SECTION_Y, 2), sticky="w")
        self.coefficients_frame.grid(row=top_row_idx + 1, column=3, padx=PADDING_FRAME_X, pady=(0, PADDING_SECTION_Y), sticky="nsew")

        row_idx_after_top_sections = top_row_idx + 2

        # Trigramme Frame
        self.trigramme_frame.grid_columnconfigure(0, weight=0)
        self.trigramme_frame.grid_columnconfigure(1, weight=1)
        self.trigramme_frame.grid_columnconfigure(2, weight=0)
        self.trigramme_label.grid(row=0, column=0, padx=(PADDING_WIDGET_X, PADDING_WIDGET_X), pady=PADDING_FRAME_Y, sticky="w")
        self.trigramme_entry.grid(row=0, column=1, padx=(0, PADDING_WIDGET_X), pady=PADDING_FRAME_Y, sticky="w")
        self.trigramme_button.grid(row=1, column=0, padx=(PADDING_WIDGET_X, PADDING_WIDGET_X), pady=PADDING_FRAME_Y, sticky="w")
        self.trigramme_status.grid(row=1, column=1, padx=(0, PADDING_WIDGET_X), pady=PADDING_FRAME_Y, sticky="w")

        # Unités Frame
        self.unites_frame.grid_columnconfigure(0, weight=0)
        self.unites_frame.grid_columnconfigure(1, weight=1)
        self.unites_frame.grid_columnconfigure(2, weight=0)
        self.unit_capteurs_label.grid(row=0, column=0, padx=(PADDING_WIDGET_X, PADDING_WIDGET_X), pady=PADDING_FRAME_Y, sticky="w")
        self.unit_capteurs_entry.grid(row=0, column=1, padx=(0, PADDING_FRAME_X), pady=PADDING_FRAME_Y, sticky="w")
        self.unit_ref_label.grid(row=1, column=0, padx=(PADDING_WIDGET_X, PADDING_WIDGET_X), pady=PADDING_FRAME_Y, sticky="w")
        self.unit_ref_entry.grid(row=1, column=1, padx=(0, PADDING_FRAME_X), pady=PADDING_FRAME_Y, sticky="w")
        self.nom_ref_label.grid(row=2, column=0, padx=(PADDING_WIDGET_X, PADDING_WIDGET_X), pady=PADDING_FRAME_Y, sticky="w")
        self.nom_ref_entry.grid(row=2, column=1, padx=(0, PADDING_FRAME_X), pady=PADDING_FRAME_Y, sticky="w")
        self.unites_button.grid(row=3, column=0, padx=(PADDING_WIDGET_X, PADDING_WIDGET_X), pady=PADDING_FRAME_Y, sticky="w")
        self.unites_status.grid(row=3, column=1, padx=(0, PADDING_FRAME_X), pady=PADDING_FRAME_Y, sticky="w")

        # Coefficients Frame
        self.coefficients_frame.grid_columnconfigure(0, weight=0)
        self.coefficients_frame.grid_columnconfigure(1, weight=1)
        self.coefficients_frame.grid_columnconfigure(2, weight=0)
        self.coefficients_subtitle.grid(row=0, column=0, columnspan=2, padx=PADDING_WIDGET_X, pady=PADDING_FRAME_Y, sticky="w")
        self.coef_a_label.grid(row=1, column=0, padx=(PADDING_WIDGET_X, PADDING_WIDGET_X), pady=PADDING_FRAME_Y, sticky="w")
        self.coef_a_entry.grid(row=1, column=1, padx=(0, PADDING_FRAME_X), pady=PADDING_FRAME_Y, sticky="w")
        self.coef_b_label.grid(row=2, column=0, padx=(PADDING_WIDGET_X, PADDING_WIDGET_X), pady=PADDING_FRAME_Y, sticky="w")
        self.coef_b_entry.grid(row=2, column=1, padx=(0, PADDING_FRAME_X), pady=PADDING_FRAME_Y, sticky="w")
        self.coefficients_button.grid(row=3, column=0, padx=(PADDING_WIDGET_X, PADDING_WIDGET_X), pady=PADDING_FRAME_Y, sticky="w")
        self.coefficients_status.grid(row=3, column=1, padx=(0, PADDING_FRAME_X), pady=PADDING_FRAME_Y, sticky="w")

        # Files List and Treatment Section
        self.files_treatment_title.grid(row=row_idx_after_top_sections, column=0, padx=PADDING_FRAME_X, pady=(PADDING_SECTION_Y, 2), sticky="w", columnspan=4)
        self.files_treatment_frame.grid(row=row_idx_after_top_sections + 1, column=0, columnspan=4, padx=PADDING_FRAME_X, pady=(0, PADDING_SECTION_Y),
                                        sticky="nsew")
        self.files_treatment_frame.columnconfigure(0, weight=1, uniform="file_process_group")
        self.files_treatment_frame.columnconfigure(1, weight=2, uniform="file_process_group")
        self.files_treatment_frame.rowconfigure(1, weight=1)
        self.files_list_subtitle.grid(row=0, column=0, padx=PADDING_WIDGET_X, pady=PADDING_WIDGET_Y, sticky="w")
        self.files_list_frame.grid(row=1, column=0, padx=PADDING_WIDGET_X, pady=PADDING_WIDGET_Y, sticky="nsew")
        self.treatment_text_subtitle.grid(row=0, column=1, padx=PADDING_WIDGET_X, pady=PADDING_WIDGET_Y, sticky="w")
        self.treatment_frame.grid(row=1, column=1, padx=PADDING_WIDGET_X, pady=PADDING_WIDGET_Y, sticky="nsew")
        self.files_list_frame.grid_columnconfigure(0, weight=1)
        self.files_list_frame.grid_rowconfigure(0, weight=1)
        self.files_listbox.grid(row=0, column=0, sticky="nsew")
        self.files_list_v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.files_list_h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.files_listbox.bind("<<ListboxSelect>>", self.on_file_select)
        self.treatment_frame.grid_columnconfigure(0, weight=1)
        self.treatment_frame.grid_rowconfigure(0, weight=1)
        self.treatment_text.grid(row=0, column=0, sticky="nsew")
        self.treatment_v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.treatment_h_scrollbar.grid(row=1, column=0, sticky="ew")

        # Graphiques Section
        self.graph_title.grid(row=row_idx_after_top_sections + 2, column=0, padx=PADDING_FRAME_X, pady=(PADDING_SECTION_Y, 2), sticky="w", columnspan=4)
        self.graph_frame.grid(row=row_idx_after_top_sections + 3, column=0, columnspan=4, padx=PADDING_FRAME_X, pady=(0, PADDING_SECTION_Y), sticky="nsew")
        self.graph_frame.grid_columnconfigure(0, weight=1, uniform="graph_group")
        self.graph_frame.grid_columnconfigure(1, weight=1, uniform="graph_group")
        self.graph1_frame.grid(row=0, column=0, padx=PADDING_WIDGET_X, pady=PADDING_WIDGET_Y, sticky="nsew")
        self.graph2_frame.grid(row=0, column=1, padx=PADDING_WIDGET_X, pady=PADDING_WIDGET_Y, sticky="nsew")
        self.graph1_label.pack(expand=True, fill="both")
        self.graph2_label.pack(expand=True, fill="both")

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
            self.current_selected_file = self.files_listbox.get(0)
            self.after(100, lambda: self.on_file_select(None))
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
                if current_selection and current_selection[0] != self.selected_file_index:
                    self.files_listbox.selection_clear(0, tk.END)
                if not current_selection or current_selection[0] != self.selected_file_index:
                    self.files_listbox.select_set(self.selected_file_index)
                    self.files_listbox.activate(self.selected_file_index)
                    self.files_listbox.see(self.selected_file_index)
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
            if self.selected_file_index < self.files_listbox.size():
                return self.files_listbox.get(self.selected_file_index)
            else:
                self.selected_file_index = None
                logger.warning(_("Previous selected index is no longer valid."))
                return None
        if not selected_indices:
            logger.warning(_("No file selected in the list"))
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
                if selected_file != self.current_selected_file:
                    self.current_selected_file = selected_file
                    try:
                        self.load_csv_callback(selected_file)
                        resultat = _("File loaded successfully: {}").format(selected_file)
                        self.treatment_text.configure(state="normal")
                        self.treatment_text.delete("1.0", "end")
                        self.treatment_text.insert("1.0", resultat)
                        self.treatment_text.configure(state="disabled")
                        self.update_status_labels(False, False, False, False)
                        self.reset_units_coefficients()
                    except Exception as e:
                        logger.error(_("Error loading file: {}").format(str(e)))
                        messagebox.showerror(_("Error"), _("Error loading file: {}").format(str(e)))
                        self.treatment_text.configure(state="normal")
                        self.treatment_text.delete("1.0", "end")
                        self.treatment_text.insert("1.0", _("Error loading file: {}").format(str(e)))
                        self.treatment_text.configure(state="disabled")
                        self.update_status_labels(False, False, False, False)
        finally:
            self._processing_selection = False
            logger.debug(_("Selection event completed"))

    def reset_units_coefficients(self):
        self.unit_capteurs_var.set("[V]")
        self.unit_ref_var.set("[m/s]")
        self.nom_ref_var.set("Venturi")
        self.unites_status.configure(text="❌")
        self.coef_a_var.set("1.0")
        self.coef_b_var.set("0.0")
        self.coefficients_status.configure(text="❌")

    def valider_trigramme(self):
        try:
            trigram = self.trigramme_var.get().strip()
            if not re.match(r"^[A-Za-z0-9_]{1,5}$", trigram):
                raise ValueError(_("Trigram must be 1-5 characters long and contain only letters, numbers, or underscores"))
            self.trigramme_status.configure(text="✅")
            self.update_status_labels(
                True,
                self.capteurs_manager.status_label.cget("text") == "✅",
                self.unites_status.cget("text") == "✅",
                self.coefficients_status.cget("text") == "✅"
            )
        except ValueError as e:
            logger.error(str(e))
            messagebox.showerror(_("Validation Error"), str(e))
            self.trigramme_var.set("Bbu")
            self.trigramme_status.configure(text="❌")
        self.update_pdf_button()

    def valider_unites(self):
        try:
            unit_capteur = self.unit_capteurs_var.get().strip()
            unit_ref = self.unit_ref_var.get().strip()
            nom_ref = self.nom_ref_var.get().strip()
            if not (unit_capteur and unit_ref and nom_ref):
                raise ValueError(_("All unit fields must be non-empty"))
            self.unites_status.configure(text="✅")
            self.update_status_labels(
                self.trigramme_status.cget("text") == "✅",
                self.capteurs_manager.status_label.cget("text") == "✅",
                True,
                self.coefficients_status.cget("text") == "✅"
            )
        except ValueError as e:
            logger.error(str(e))
            messagebox.showerror(_("Validation Error"), str(e))
            self.unites_status.configure(text="❌")
        self.update_pdf_button()

    def valider_coefficients(self):
        try:
            coef_a = self.coef_a_var.get().strip()
            coef_b = self.coef_b_var.get().strip()
            float(coef_a)
            float(coef_b)
            self.coefficients_status.configure(text="✅")
            self.update_status_labels(
                self.trigramme_status.cget("text") == "✅",
                self.capteurs_manager.status_label.cget("text") == "✅",
                self.unites_status.cget("text") == "✅",
                True
            )
        except ValueError as e:
            logger.error(str(e))
            messagebox.showerror(_("Validation Error"), str(e))
            self.coefficients_status.configure(text="❌")
        self.update_pdf_button()

    def update_pdf_button(self):
        if (self.trigramme_status.cget("text") == "✅" and
            self.capteurs_manager.status_label.cget("text") == "✅" and
            self.unites_status.cget("text") == "✅" and
            self.coefficients_status.cget("text") == "✅"):
            logger.info(_("All validations passed. PDF generation enabled."))
        else:
            logger.info(_("Validations pending. PDF generation disabled."))
        pass

    def refresh(self):
        self.trigramme_title.configure(text=_("Trigram"))
        self.trigramme_label.configure(text=_("Name (Trigram):"))
        self.trigramme_button.configure(text=_("Validate"))
        self.trigramme_status.configure(text=self.trigramme_status.cget("text"))
        self.capteurs_title.configure(text=_("Sensors"))
        self.capteurs_manager.refresh()
        self.capteurs_manager.status_label.configure(text=self.capteurs_manager.status_label.cget("text"))
        self.unites_title.configure(text=_("Units"))
        self.unit_capteurs_label.configure(text=_("Unit (Sensor):"))
        self.unit_ref_label.configure(text=_("Unit (Ref Sensor):"))
        self.nom_ref_label.configure(text=_("Name (Ref Sensor):"))
        self.unites_button.configure(text=_("Validate Units"))
        self.unites_status.configure(text=self.unites_status.cget("text"))
        self.coefficients_title.configure(text=_("Coefficients"))
        self.coefficients_subtitle.configure(text=_("Reference Sensor Conversion Coefficients"))
        self.coef_a_label.configure(text=_("Coefficient a:"))
        self.coef_b_label.configure(text=_("Coefficient b:"))
        self.coefficients_button.configure(text=_("Validate Coefficients"))
        self.coefficients_status.configure(text=self.coefficients_status.cget("text"))
        self.files_treatment_title.configure(text=_("Files and Processing"))
        self.files_list_subtitle.configure(text=_("Available Files:"))
        self.treatment_text_subtitle.configure(text=_("Processing Output:"))
        self.graph_title.configure(text=_("Graphs"))
        self.graph1_label.configure(text=_("Graph 1 Placeholder"))
        self.graph2_label.configure(text=_("Graph 2 Placeholder"))
        self.afficher_liste_fichiers()
        if self.selected_file_index is not None and self.selected_file_index < self.files_listbox.size():
            self.files_listbox.select_set(self.selected_file_index)
            self.files_listbox.activate(self.selected_file_index)
            self.files_listbox.see(self.selected_file_index)