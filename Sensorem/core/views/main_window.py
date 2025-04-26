# core/views/main_window.py
import customtkinter as ctk
from tkinter import ttk
from core.views.tabs.db_tab import DatabaseTab
from core.views.tabs.logs_tab import LogsTab
from core.views.tabs.processing_tab import ProcessingTab
from core.utils.i18n import _
import logging

logger = logging.getLogger('Sensorem')

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")
padding_top = 10
padding_x = 10
padding_bottom = 10

class MainWindow(ctk.CTk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title(_("Sensorem - Sensor Signal Processing"))
        self.geometry("1500x900")
        self.resizable(True, True)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.create_widgets()
        self.place_widgets()
        self.controller.set_view(self)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        # Frame pour les widgets du haut (sélecteur de langue et bouton Quit)
        self.top_frame = ctk.CTkFrame(self)
        self.language_var = ctk.StringVar(value="Français")
        self.language_menu = ctk.CTkOptionMenu(
            self.top_frame,
            values=["Français", "English"],
            variable=self.language_var,
            command=lambda _: self.controller.change_language(self.language_var.get())
        )
        self.quit_button = ctk.CTkButton(self.top_frame, text=_("Quit"), command=self.on_closing)
        self.tab_view = None
        self.tabs = {}
        self.setup_tabs()

    def place_widgets(self):
        # Placer le top_frame avec pack
        self.top_frame.grid(row=0, column=0, sticky="ew", padx=padding_x, pady=(padding_top, 2))
        # Sélecteur de langue à gauche
        self.language_menu.pack(side="left", padx=5)
        # Bouton Quit à droite, avec un padx pour aligner avec le tab_view
        self.quit_button.pack(side="right", padx=(0, padding_x))  # padding_x correspond au padx du tab_view

    def setup_tabs(self):
        logger.debug("Setting up tabs")
        self.tab_view = ctk.CTkTabview(self, width=1500, height=900, anchor="nw")
        self.tab_view.grid_columnconfigure(0, weight=1)
        self.tab_view.grid_rowconfigure(0, weight=1)
        for tab_name in self.controller.tab_names:
            logger.debug(f"Adding tab: {tab_name}")
            self.tab_view.add(tab_name)
        self.tab_view.grid(row=1, column=0, padx=padding_x, pady=(2, padding_bottom), sticky="nsew")
        self.tabs = {
            _("Processing"): ProcessingTab(self.tab_view.tab(_("Processing")), self.controller, self.controller.load_csv),
            _("Database"): DatabaseTab(self.tab_view.tab(_("Database"))),
            _("Logs"): LogsTab(self.tab_view.tab(_("Logs")))
        }
        logger.debug("Tabs initialized: {}".format(list(self.tabs.keys())))
        for tab_name, tab in self.tabs.items():
            logger.debug(f"Configuring tab content: {tab_name}")
            tab.pack(fill="both", expand=True)

    def refresh_ui(self):
        logger.debug("Refreshing UI")
        self.title(_("Sensorem - Sensor Signal Processing"))
        self.language_menu.configure(values=[_("Français"), _("English")])
        self.language_var.set(_("Français") if self.language_var.get() == "Français" else _("English"))
        self.quit_button.configure(text=_("Quit"))
        for tab_name, tab in self.tabs.items():
            logger.debug(f"Refreshing tab: {tab_name}")
            tab.refresh()

    def on_closing(self):
        logger.info("Application closed by user")
        self.quit()