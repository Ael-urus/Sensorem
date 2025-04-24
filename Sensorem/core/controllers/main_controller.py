# core/controllers/main_controller.py
from core.utils.i18n import set_language, _
from core.utils.logger import setup_ui_logger, logger
from tkinter import filedialog, messagebox
from core.datas.csv_handler import read_csv
from pathlib import Path
from core.controllers.processing_controller import ProcessingController
from core.models.processing_model import ProcessingModel

class MainController:
    def __init__(self, model):
        self.model = model
        self.base_dir = Path(__file__).resolve().parent.parent.parent.parent
        self.processing_model = ProcessingModel(self.base_dir)
        self.processing_controller = None  # Sera initialisé dans setup_tabs
        set_language("fr")

    def change_language(self, language):
        logger.debug(f"Tentative de changement de langue vers : {language}")
        lang_map = {"English": "en", "Français": "fr"}
        set_language(lang_map[language])
        logger.info(f"Changement de langue vers : {lang_map[language]}")
        self.model.notify_view()

    def load_csv(self, file_path=None):
        if not file_path:
            file_path = filedialog.askopenfilename(
                initialdir=str(self.base_dir),
                filetypes=[("CSV files", "*.csv")]
            )
        if file_path:
            try:
                data = read_csv(file_path)
                self.model.set_csv_data(data)
                logger.info(_("CSV loaded: {}, {} rows").format(file_path, len(data)))
            except Exception as e:
                logger.error(_("Error loading CSV: {}").format(e))
                messagebox.showerror(_("Error"), _("Error loading CSV: {}").format(e))

    def setup_logger(self, textbox):
        setup_ui_logger(textbox)
        logger.info(_("Interface initialized"))

    def initialize_processing_controller(self, view):
        """Initialiser le ProcessingController avec la vue de l'onglet Processing."""
        self.processing_controller = ProcessingController(view, self.processing_model, self.load_csv)