# core/views/main_window.py
import customtkinter as ctk
import os
import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.utils.i18n import set_language, _  # Importer _ une seule fois
from core.utils.logger import setup_ui_logger, logger
from core.views.tabs.processing_tab import ProcessingTab
from tkinter import filedialog
from core.datas.csv_handler import read_csv


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurer la langue par défaut (anglais)
        #print("Initialisation langue : en")
        set_language("en")
        #print(f"Après set_language('en'), _('Processing') = {_('Processing')}")

        # Configurer la fenêtre
        self.title(_("Sensorem - Sensor Signal Processing"))
        self.geometry("1200x600")

        # Menu pour changer la langue - MODIFIÉ
        self.language_menu = ctk.CTkOptionMenu(
            self,
            values=["English", "Français"],
            command=self.change_language,
            width=100  # Réduire la largeur
        )
        self.language_menu.pack(anchor="nw", padx=10, pady=1)  # Changed pady to 0 to reduce vertical space

        # Conteneur pour les onglets
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(padx=10, pady=2, fill="both", expand=True)

        # Liste des noms d'onglets (non traduits)
        self.tab_names = ["Processing", "Database", "Logs"]

        # Ajouter des onglets avec leurs noms traduits
        for tab_name in self.tab_names:
            self.tab_view.add(_(tab_name))

        # Configurer le contenu des onglets
        self.setup_tabs()

    def setup_tabs(self):
        #print(f"Dans setup_tabs, _('Processing') = {_('Processing')}")
        # Nettoyer le contenu des onglets
        for tab_name in self.tab_names:
            for widget in self.tab_view.tab(_(tab_name)).winfo_children():
                widget.destroy()

        # Onglet Processing
        self.processing_tab = ProcessingTab(self.tab_view.tab(_("Processing")), self.load_csv)
        self.processing_tab.pack(fill="both", expand=True)

        # Onglet Database
        db_label = ctk.CTkLabel(
            self.tab_view.tab(_("Database")),
            text=_("Welcome to the Database tab")
        )
        db_label.pack(pady=20)

        # Onglet Logs
        logs_content = ""
        if hasattr(self, "logs_text") and self.logs_text.winfo_exists():
            logs_content = self.logs_text.get("1.0", "end")
            #print(f"Contenu des logs sauvegardé dans setup_tabs : {logs_content[:50]}...")

        self.logs_text = ctk.CTkTextbox(self.tab_view.tab(_("Logs")), height=300)
        self.logs_text.pack(padx=10, pady=10, fill="both", expand=True)
        setup_ui_logger(self.logs_text)
        #print(f"Nouvelle logs_text créée et logger configuré")

        if logs_content:
            self.logs_text.insert("1.0", logs_content)
            self.logs_text.see("end")
            #print(f"Contenu des logs restauré")

        logger.info(_("Interface initialized"))

    def change_language(self, language):
        lang_map = {"English": "en", "Français": "fr"}
        #print(f"Changement de langue vers : {lang_map[language]}")
        set_language(lang_map[language])
        #print(f"Après set_language('{lang_map[language]}'), _('Processing') = {_('Processing')}")
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
        #print(f"Avant rafraîchissement, _('Processing') = {_('Processing')}")
        #print(f"Onglets avant suppression : {list(self.tab_view._tab_dict.keys())}")

        # Rafraîchir le titre
        self.title(_("Sensorem - Sensor Signal Processing"))

        # Sauvegarder l'onglet actif
        current_tab = self.tab_view.get()

        # Supprimer tous les onglets existants
        for tab_name in list(self.tab_view._tab_dict.keys()):
            try:
                self.tab_view.delete(tab_name)
            except ValueError:
                pass

        # Recréer les onglets avec leurs noms traduits
        for tab_name in self.tab_names:
            self.tab_view.add(_(tab_name))

        # Restaurer l'onglet actif
        for tab_name in self.tab_names:
            if _(tab_name) == current_tab:
                self.tab_view.set(_(tab_name))
                break
        else:
            self.tab_view.set(_(self.tab_names[0]))  # Par défaut, premier onglet

        # Rafraîchir le contenu des onglets
        self.setup_tabs()

        # Rafraîchir l'onglet Processing
        self.processing_tab.refresh()

        logger.info(_("Language changed: {}").format(self.language_menu.get()))
        #print(f"Après rafraîchissement, _('Processing') = {_('Processing')}")
        #print(f"Onglets après recréation : {list(self.tab_view._tab_dict.keys())}")

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()