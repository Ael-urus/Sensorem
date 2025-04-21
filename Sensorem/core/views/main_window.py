# core/views/main_window.py
import customtkinter as ctk
import os
import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.utils.i18n import set_language, _
from core.utils.logger import setup_ui_logger, logger
from core.views.tabs.processing_tab import ProcessingTab
from tkinter import filedialog
from core.datas.csv_handler import read_csv

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurer la langue par défaut (français)
        set_language("fr")

        # Configurer la fenêtre
        self.title(_("Sensorem - Sensor Signal Processing"))
        self.geometry("1200x600")

        # Cadre pour la barre de langue
        self.language_frame = ctk.CTkFrame(self)
        self.language_menu = ctk.CTkOptionMenu(
            self.language_frame,
            values=["English", "Français"],
            command=self.change_language,
            width=100
        )
        self.quit_button = ctk.CTkButton(self.language_frame, text=_("Quit"), command=self.destroy, width=80)

        # Conteneur pour les onglets
        self.tab_view = ctk.CTkTabview(self)

        # Liste des noms d'onglets (non traduits)
        self.tab_names = ["Processing", "Database", "Logs"]
        self.tab_name_map = {}  # Associe noms non traduits à noms traduits

        # Ajouter des onglets avec leurs noms traduits
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

    def setup_tabs(self):
        logger.debug("Configuration des onglets")
        # Onglet Processing
        self.processing_tab = ProcessingTab(self.tab_view.tab(self.tab_name_map["Processing"]), self.load_csv)
        self.processing_tab.pack(fill="both", expand=True)

        # Onglet Database
        db_label = ctk.CTkLabel(
            self.tab_view.tab(self.tab_name_map["Database"]),
            text=_("Welcome to the Database tab")
        )
        db_label.pack(pady=20)

        # Onglet Logs
        logs_content = ""
        if hasattr(self, "logs_text") and self.logs_text.winfo_exists():
            logs_content = self.logs_text.get("1.0", "end")
            logger.debug(f"Contenu des logs sauvegardé : {logs_content[:50]}...")

        self.logs_text = ctk.CTkTextbox(self.tab_view.tab(self.tab_name_map["Logs"]), height=300)
        self.logs_text.pack(padx=10, pady=10, fill="both", expand=True)
        setup_ui_logger(self.logs_text)

        if logs_content:
            self.logs_text.insert("1.0", logs_content)
            self.logs_text.see("end")

        logger.info(_("Interface initialized"))

    def change_language(self, language):
        lang_map = {"English": "en", "Français": "fr"}
        logger.info(f"Changement de langue vers : {lang_map[language]}")
        set_language(lang_map[language])
        self.refresh_ui()

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                data = read_csv(file_path)
                logger.info(_("CSV loaded: {}, {} rows").format(file_path, len(data)))
            except Exception as e:
                logger.error(_("Error loading CSV: {}").format(e))

    def refresh_ui(self):
        logger.debug("Début du rafraîchissement de l'interface")

        # Rafraîchir le titre
        self.title(_("Sensorem - Sensor Signal Processing"))

        # Sauvegarder l'onglet actif (par nom non traduit)
        current_tab = self.tab_view.get()
        current_tab_key = None
        for tab_name, translated_name in self.tab_name_map.items():
            if translated_name == current_tab:
                current_tab_key = tab_name
                break
        if not current_tab_key:
            current_tab_key = "Processing"  # Par défaut

        # Supprimer tous les onglets existants
        for tab_name in list(self.tab_name_map.values()):
            try:
                self.tab_view.delete(tab_name)
            except ValueError as e:
                logger.error(f"Erreur lors de la suppression de l'onglet {tab_name}: {e}")

        # Mettre à jour la carte des noms d'onglets
        self.tab_name_map = {}
        for tab_name in self.tab_names:
            translated_name = _(tab_name)
            self.tab_name_map[tab_name] = translated_name
            self.tab_view.add(translated_name)

        # Restaurer le contenu des onglets
        self.setup_tabs()

        # Restaurer l'onglet actif
        try:
            self.tab_view.set(self.tab_name_map[current_tab_key])
        except ValueError as e:
            logger.error(f"Erreur lors de la sélection de l'onglet {self.tab_name_map[current_tab_key]}: {e}")
            self.tab_view.set(self.tab_name_map["Processing"])

        # Rafraîchir l'onglet Processing
        self.processing_tab.refresh()
        self.quit_button.configure(text=_("Quit"))

        logger.info(_("Language changed: {}").format(self.language_menu.get()))
        logger.debug("Fin du rafraîchissement de l'interface")

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()