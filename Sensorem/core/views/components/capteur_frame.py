# core/views/components/capteur_frame.py
import customtkinter as ctk
from ...utils.i18n import _

# Define standard fonts and padding constants
STANDARD_FONT = ("Roboto", 12)
PADDING_FRAME_X = 5
PADDING_FRAME_Y = 5
PADDING_WIDGET_X = 5
PADDING_WIDGET_Y = 5


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