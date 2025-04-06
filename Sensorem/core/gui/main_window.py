# core/gui/main_window.py
import tkinter as tk
from tkinter import ttk

from .db_tab import DatabaseTab
from .logs_tab import LogsTab
from .processing_tab import ProcessingTab
from ..utils.i18n import _, translator


class MainWindow(tk.Tk):
    def __init__(self, log_manager):
        super().__init__()
        self.log_manager = log_manager
        self.title(_("Sensorem - Sensor Signal Processing"))
        self._setup_language_menu()
        self._setup_notebook()
        translator.set_language('en')

    def _setup_language_menu(self):
        """Configure the language selection menu"""
        menubar = tk.Menu(self)
        lang_menu = tk.Menu(menubar, tearoff=0)
        lang_menu.add_command(label="English", command=lambda: self._change_language('en'))
        lang_menu.add_command(label="Français", command=lambda: self._change_language('fr'))
        menubar.add_cascade(label=_("Language"), menu=lang_menu)
        self.config(menu=menubar)

    def _change_language(self, lang_code):
        """Change the interface language"""
        translator.set_language(lang_code)
        self.title(_("Sensorem - Sensor Signal Processing"))
        self._setup_notebook()

    def _setup_notebook(self):
        """Reconfigure tabs after language change"""
        if hasattr(self, 'notebook'):
            self.log_manager.outputs.clear()  # Clear old widget references
            self.notebook.destroy()

        self.notebook = ttk.Notebook(self)
        self.processing_tab = ProcessingTab(self.notebook, self.log_manager)
        self.db_tab = DatabaseTab(self.notebook, self.log_manager)
        self.logs_tab = LogsTab(self.notebook, self.log_manager)
        self.notebook.add(self.processing_tab, text=_("Processing"))
        self.notebook.add(self.db_tab, text=_("Database"))
        self.notebook.add(self.logs_tab, text=_("Logs"))
        self.notebook.pack(expand=True, fill="both")

if __name__ == "__main__":
    app = MainWindow()  # Will fail without log_manager if run directly
    app.mainloop()