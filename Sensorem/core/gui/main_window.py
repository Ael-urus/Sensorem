# core/gui/main_window.py
import tkinter as tk
from tkinter import ttk
# Importez les classes nécessaires (ajustez les chemins si besoin)
from .processing_tab import ProcessingTab
from ..controllers.processing_controller import ProcessingController
from .db_tab import DatabaseTab # Gardez si non refactoré, sinon importez la vue et le contrôleur
from .logs_tab import LogsTab   # Gardez si non refactoré, sinon importez la vue et le contrôleur

from ..utils.i18n import _, translator


class MainWindow(tk.Tk):
    def __init__(self, log_manager):
        super().__init__()
        self.log_manager = log_manager
        self.title(_("Sensorem - Sensor Signal Processing"))

        # Créer les widgets principaux
        self.menubar = tk.Menu(self)
        self.lang_menu_cascade = None  # Pour stocker la référence au menu "Language"
        self.lang_menu = tk.Menu(self.menubar, tearoff=0)
        self._setup_language_menu()
        self._setup_notebook()

        # S'abonner aux changements de langue
        translator.add_observer(self._on_language_changed)

        # Initialiser la langue par défaut
        translator.set_language('en')

    def _setup_language_menu(self):
        """Configure the language selection menu"""
        self.lang_menu.add_command(label="English", command=lambda: translator.set_language('en'))
        self.lang_menu.add_command(label="Français", command=lambda: translator.set_language('fr'))
        #self.lang_menu_cascade = tk.Menubutton(self.menubar, text=_("Language"), menu=self.lang_menu, direction="below")
        self.menubar.add_cascade(label=_("Language"), menu=self.lang_menu)
        self.config(menu=self.menubar)

    def _on_language_changed(self, lang_code):
        """Appelé lorsque la langue est changée"""
        self.title(_("Sensorem - Sensor Signal Processing"))

        # Mettre à jour les titres des onglets sans les recréer
        self.notebook.tab(self.processing_tab, text=_("Processing"))
        self.notebook.tab(self.db_tab, text=_("Database"))
        self.notebook.tab(self.logs_tab, text=_("Logs"))

        # Mettre à jour le menu
        self._update_language_menu()

        # Informer l'utilisateur du changement
        self.log_manager.info(_("Language changed to")+" {lang}".format(lang=lang_code))

    def _update_language_menu(self):
        """Met à jour les labels du menu après changement de langue"""
        menubar = self.menubar
        if menubar:
            print(f"Éléments de la barre de menu (winfo_children): {menubar.winfo_children()}")
            try:
                for i in range(menubar.index('end') + 1):
                    item_type = menubar.type(i)
                    print(f"Index: {i}, Type: {item_type}")
                    if item_type in ('cascade', 'menubutton'):  # Vérifie si le type est 'cascade' ou 'menubutton'
                        try:
                            label = menubar.entrycget(i, 'label')
                            print(f"  Label: {label}")
                            if label == "Language" or label == "Langue":
                                print(f"  Found language menu at index {i}, configuring label to: {_('Language')}")
                                self.menubar.entryconfigure(i, label=_("Language"))
                                break
                        except tk.TclError as e:
                            print(f"  Erreur lors de l'obtention du label à l'index {i}: {e}")
                    else:
                        print(f"  Skipping type: {item_type}")
            except ValueError as e:
                print(f"Erreur dans _update_language_menu: {e}")

    def _setup_notebook(self):
        """Configure les onglets de l'application"""
        self.notebook = ttk.Notebook(self)

        # --- Onglet Processing (Refactoré MVC) ---
        # 1. Créer la Vue (ne prend que le parent)
        processing_tab_view = ProcessingTab(self.notebook)

        # 2. Créer le Contrôleur (passez la vue et les dépendances)
        processing_tab_controller = ProcessingController(
            view=processing_tab_view,
            log_manager=self.log_manager,
            # pdf_generator=self.pdf_generator,       # Décommentez et passez les vrais objets
            # signal_processor=self.signal_processor, # si initialisés dans __init__
            # app_state=self.app_state                # de MainWindow
        )

        # 3. Injecter le Contrôleur dans la Vue
        processing_tab_view.set_controller(processing_tab_controller)

        # 4. Ajouter la Vue au notebook
        self.notebook.add(processing_tab_view, text=_("Processing"))

        # 5. Optionnel: garder des références si nécessaire pour d'autres interactions
        self.processing_tab_view = processing_tab_view
        self.processing_tab_controller = processing_tab_controller

        # --- Onglet Database ---
        # TODO: Appliquer le même pattern MVC si DatabaseTab est/sera refactoré
        # Si DatabaseTab n'a pas été refactoré et attend toujours log_manager dans __init__:
        self.db_tab = DatabaseTab(self.notebook, self.log_manager)
        # Si DatabaseTab EST refactoré (exemple):
        # db_tab_view = DatabaseTabView(self.notebook)
        # db_tab_controller = DatabaseController(db_tab_view, self.log_manager, ...)
        # db_tab_view.set_controller(db_tab_controller)
        # self.notebook.add(db_tab_view, text=_("Database"))
        # self.db_tab_view = db_tab_view # Garder référence si besoin
        self.notebook.add(self.db_tab, text=_("Database"))

        # --- Onglet Logs ---
        # TODO: Appliquer le même pattern MVC si LogsTab est/sera refactoré
        # Si LogsTab n'a pas été refactoré :
        self.logs_tab = LogsTab(self.notebook, self.log_manager)
        # Si LogsTab EST refactoré (exemple):
        # logs_tab_view = LogsTabView(self.notebook)
        # logs_tab_controller = LogsController(logs_tab_view, self.log_manager)
        # logs_tab_view.set_controller(logs_tab_controller)
        # self.notebook.add(logs_tab_view, text=_("Logs"))
        # self.logs_tab_view = logs_tab_view # Garder référence si besoin
        self.notebook.add(self.logs_tab, text=_("Logs"))

        # --- Finalisation ---
        self.notebook.pack(expand=True, fill="both")

    def __del__(self):
        # Se désabonner pour éviter les fuites mémoire
        translator.remove_observer(self._on_language_changed)


if __name__ == "__main__":
    class DummyLogManager:
        def info(self, message):
            print(f"[INFO] {message}")
        def warning(self, message):
            print(f"[WARNING] {message}")

    log_manager = DummyLogManager()
    app = MainWindow(log_manager)
    app.mainloop()