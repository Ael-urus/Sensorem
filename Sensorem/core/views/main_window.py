# core/views/main_window.py
import customtkinter as ctk
from core.views.tabs.processing_tab import ProcessingTab
from core.views.tabs.db_tab import DatabaseTab
from core.views.tabs.logs_tab import LogsTab
from core.utils.i18n import _
from core.utils.logger import logger

class MainWindow(ctk.CTk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        # Configurer la fenêtre
        self.title(_("Sensorem - Sensor Signal Processing"))
        self.geometry("1200x600")

        # Cadre pour la barre de langue
        self.language_frame = ctk.CTkFrame(self)
        self.language_menu = ctk.CTkOptionMenu(
            self.language_frame,
            values=["English", "Français"],
            command=lambda value: self.on_language_change(value),
            width=100
        )
        self.quit_button = ctk.CTkButton(self.language_frame, text=_("Quit"), command=self.destroy, width=80)

        # Conteneur pour les onglets
        self.tab_view = ctk.CTkTabview(self)
        self.tab_names = ["Processing", "Database", "Logs"]
        self.tab_name_map = {}

        # Ajouter des onglets
        for tab_name in self.tab_names:
            translated_name = _(tab_name)
            self.tab_view.add(translated_name)
            self.tab_name_map[tab_name] = translated_name

        # Configurer le contenu des onglets
        self.setup_tabs()

        # Placer les widgets
        self.language_frame.pack(fill="x", padx=10, pady=0)
        self.language_menu.pack(side="left", padx=5)
        self.quit_button.pack(side="right", padx=5)
        self.tab_view.pack(padx=10, pady=0, fill="both", expand=True)

    def on_language_change(self, value):
        logger.debug(f"Menu déroulant déclenché avec la valeur : {value}")
        self.controller.change_language(value)

    def setup_tabs(self):
        self.processing_tab = ProcessingTab(self.tab_view.tab(self.tab_name_map["Processing"]), self.controller.load_csv)
        self.processing_tab.pack(fill="both", expand=True)

        self.db_tab = DatabaseTab(self.tab_view.tab(self.tab_name_map["Database"]))
        self.db_tab.pack(fill="both", expand=True)

        self.logs_tab = LogsTab(self.tab_view.tab(self.tab_name_map["Logs"]))
        self.logs_tab.pack(fill="both", expand=True)
        self.controller.setup_logger(self.logs_tab.logs_text)

    def refresh_ui(self, current_tab_key="Processing"):
        self.title(_("Sensorem - Sensor Signal Processing"))

        need_recreate = False
        new_tab_name_map = {}
        for tab_name in self.tab_names:
            translated_name = _(tab_name)
            new_tab_name_map[tab_name] = translated_name
            if self.tab_name_map[tab_name] != translated_name:
                need_recreate = True

        if need_recreate:
            current_tab = self.tab_view.get()
            current_tab_key = next(
                (key for key, value in self.tab_name_map.items() if value == current_tab),
                "Processing"
            )

            for tab_name in list(self.tab_name_map.values()):
                self.tab_view.delete(tab_name)

            self.tab_name_map = new_tab_name_map

            for tab_name in self.tab_names:
                self.tab_view.add(self.tab_name_map[tab_name])

            self.setup_tabs()

            self.tab_view.set(self.tab_name_map[current_tab_key])
        else:
            self.processing_tab.refresh()
            self.db_tab.refresh()
            self.logs_tab.refresh()

        self.quit_button.configure(text=_("Quit"))