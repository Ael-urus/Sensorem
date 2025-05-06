# core/views/components/capteurs_manager.py
import customtkinter as ctk
import tkinter as tk
from ...utils.i18n import _
from .capteur_frame import CapteurFrame
import logging

logger = logging.getLogger('Sensorem')

# Define standard fonts and padding constants
STANDARD_FONT = ("Roboto", 12)
PADDING_FRAME_X = 5
PADDING_FRAME_Y = 5
PADDING_WIDGET_X = 5
PADDING_WIDGET_Y = 5


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
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=PADDING_FRAME_X, pady=PADDING_FRAME_Y)
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
                    raise ValueError(
                        "Le nom du capteur et la ligne de début doivent être non vides, et la ligne doit être un nombre")
            self.status_label.configure(text="✅", text_color="green")
            logger.info("Capteurs validés avec succès")
        except ValueError as e:
            logger.error(f"Erreur de validation des capteurs : {str(e)}")
            tk.messagebox.showerror("Erreur de validation", str(e))
            self.status_label.configure(text="❌", text_color="red")

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