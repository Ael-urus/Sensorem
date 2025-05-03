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
        self.top_frame.grid(row=0, column=0, sticky="ew", padx=padding_x, pady=(padding_top, 2))
        self.language_menu.pack(side="left", padx=5)
        self.quit_button.pack(side="right", padx=(0, padding_x))

    def setup_tabs(self):
        logger.debug("Setting up tabs")
        self.tab_view = ctk.CTkTabview(self, width=1500, height=900, anchor="nw")
        self.tab_view.grid_columnconfigure(0, weight=1)
        self.tab_view.grid_rowconfigure(0, weight=1)
        for tab_name in self.controller.tab_names:
            translated_name = _(tab_name)
            logger.debug(f"Adding tab: {translated_name}")
            self.tab_view.add(translated_name)
        self.tab_view.grid(row=1, column=0, padx=padding_x, pady=(2, padding_bottom), sticky="nsew")
        self.tabs = {
            "Processing": ProcessingTab(self.tab_view.tab(_("Processing")), self.controller, self.controller.load_csv),
            "Database": DatabaseTab(self.tab_view.tab(_("Database"))),
            "Logs": LogsTab(self.tab_view.tab(_("Logs")))
        }
        logger.debug("Tabs initialized: {}".format(list(self.tabs.keys())))
        for tab_name, tab in self.tabs.items():
            logger.debug(f"Configuring tab content: {tab_name}")
            tab.pack(fill="both", expand=True)

    def recreate_tabs(self):
        logger.debug("Recreating tabs")
        # Sauvegarder l'onglet actuellement sélectionné
        current_tab = self.tab_view.get() if self.tab_view else None
        # Sauvegarder l'état de ProcessingTab
        processing_state = None
        if "Processing" in self.tabs:
            processing_tab = self.tabs["Processing"]
            processing_state = {
                "selected_file_index": processing_tab.selected_file_index,
                "current_selected_file": processing_tab.current_selected_file
            }
        # Désactiver le LogHandler pour LogsTab
        if "Logs" in self.tabs:
            logs_tab = self.tabs["Logs"]
            logs_tab.disable_logging()
        # Supprimer l'ancien tab_view
        if self.tab_view:
            self.tab_view.destroy()
        # Recréer le tab_view
        self.tab_view = ctk.CTkTabview(self, width=1500, height=900, anchor="nw")
        self.tab_view.grid_columnconfigure(0, weight=1)
        self.tab_view.grid_rowconfigure(0, weight=1)
        for tab_name in self.controller.tab_names:
            translated_name = _(tab_name)
            logger.debug(f"Adding tab: {translated_name}")
            self.tab_view.add(translated_name)
        self.tab_view.grid(row=1, column=0, padx=padding_x, pady=(2, padding_bottom), sticky="nsew")
        # Réinitialiser self.tabs avec des clés fixes
        self.tabs = {
            "Processing": ProcessingTab(self.tab_view.tab(_("Processing")), self.controller, self.controller.load_csv),
            "Database": DatabaseTab(self.tab_view.tab(_("Database"))),
            "Logs": LogsTab(self.tab_view.tab(_("Logs")))
        }
        # Restaurer l'état de ProcessingTab
        if processing_state and "Processing" in self.tabs:
            processing_tab = self.tabs["Processing"]
            processing_tab.selected_file_index = processing_state["selected_file_index"]
            processing_tab.current_selected_file = processing_state["current_selected_file"]
            processing_tab.afficher_liste_fichiers()
            if processing_tab.selected_file_index is not None:
                processing_tab.files_listbox.select_set(processing_tab.selected_file_index)
                processing_tab.files_listbox.activate(processing_tab.selected_file_index)
                processing_tab.files_listbox.see(processing_tab.selected_file_index)
        # Réactiver le LogHandler pour LogsTab
        if "Logs" in self.tabs:
            self.tabs["Logs"].enable_logging()
        for tab_name, tab in self.tabs.items():
            logger.debug(f"Configuring tab content: {tab_name}")
            tab.pack(fill="both", expand=True)
        # Restaurer l'onglet sélectionné
        if current_tab:
            for tab_name in self.controller.tab_names:
                if _(tab_name) == current_tab:
                    self.tab_view.set(_(tab_name))
                    break
        logger.debug("Tabs recreated: {}".format(list(self.tabs.keys())))

    def refresh_ui(self):
        logger.debug("Refreshing UI")
        self.title(_("Sensorem - Sensor Signal Processing"))
        self.language_menu.configure(values=[_("Français"), "English"])
        self.language_var.set(_("Français") if self.language_var.get() == "Français" else _("English"))
        self.quit_button.configure(text=_("Quit"))
        self.recreate_tabs()
        for tab_name, tab in self.tabs.items():
            logger.debug(f"Refreshing tab: {tab_name}")
            tab.refresh()

    def on_closing(self):
        # Désactiver le logging avant de fermer pour éviter les erreurs
        if "Logs" in self.tabs:
            self.tabs["Logs"].disable_logging()
        logger.info("Application closed by user")
        self.quit()