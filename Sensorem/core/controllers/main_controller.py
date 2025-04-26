# core/controllers/main_controller.py
import os
import re
from tkinter import messagebox
import pandas as pd
from core.datas.csv_handler import read_csv
from core.utils.i18n import _
import logging

logger = logging.getLogger('Sensorem')

class MainController:
    def __init__(self, model, base_dir=r"D:\PycharmGitSensorem\Sensorem-1"):
        self.model = model
        self.view = None
        self.base_dir = base_dir
        self.tab_names = [_("Processing"), _("Database"), _("Logs")]

    def set_view(self, view):
        self.view = view
        # Initialiser les statuts dans l'onglet Traitement
        if self.view and hasattr(self.view.tabs[_("Processing")], 'update_status_labels'):
            self.view.tabs[_("Processing")].update_status_labels(
                self.model.trigram_valid,
                self.model.sensors_valid,
                self.model.units_valid,
                self.model.coefficients_valid
            )

    def load_csv(self, filename):
        logger.info("DEBUG: Executing MainController.load_csv (selection only, no reading) (2025-04-26)")
        if not filename:
            logger.warning(_("No file selected for loading"))
            raise ValueError(_("No file selected"))
        file_path = os.path.join(self.base_dir, filename)
        try:
            if not os.path.exists(file_path):
                logger.error(_("File not found: {}").format(file_path))
                raise FileNotFoundError(_("File not found: {}").format(file_path))
            logger.info(_("File selected successfully: {}").format(file_path))
            if self.view:
                self.view.refresh_ui()
        except Exception as e:
            logger.error(_("Error selecting file: {}").format(str(e)))
            raise

    def list_csv_files(self):
        try:
            csv_files = [
                f for f in os.listdir(self.base_dir)
                if f.lower().endswith('.csv') and os.path.isfile(os.path.join(self.base_dir, f))
            ]
            logger.debug(_("Found {} CSV files in {}").format(len(csv_files), self.base_dir))
            return sorted(csv_files)
        except FileNotFoundError:
            logger.error(_("Directory not found: {}").format(self.base_dir))
            return []
        except Exception as e:
            logger.error(_("Error listing CSV files: {}").format(str(e)))
            return []

    def validate_trigram(self, trigram):
        if not isinstance(trigram, str) or len(trigram) != 3 or not trigram.isalpha():
            logger.error(_("Invalid trigram: {}").format(trigram))
            raise ValueError(_("Trigram must be exactly 3 letters"))
        self.model.set_trigram(trigram)
        logger.info(_("Trigram validated: {}").format(trigram))
        # Mettre à jour les statuts
        if self.view and hasattr(self.view.tabs[_("Processing")], 'update_status_labels'):
            self.view.tabs[_("Processing")].update_status_labels(
                self.model.trigram_valid,
                self.model.sensors_valid,
                self.model.units_valid,
                self.model.coefficients_valid
            )

    def validate_sensors(self, sensors):
        if not sensors or not all(len(s) == 2 for s in sensors):
            logger.error(_("Invalid sensors format"))
            raise ValueError(_("Invalid sensors format"))
        for name, start_line in sensors:
            try:
                int(start_line)
            except ValueError:
                logger.error(_("Invalid start line for sensor {}: {}").format(name, start_line))
                raise ValueError(_("Start line must be a number"))
        self.model.set_sensors(sensors)
        logger.info(_("Sensors validated: {}").format(sensors))
        # Mettre à jour les statuts
        if self.view and hasattr(self.view.tabs[_("Processing")], 'update_status_labels'):
            self.view.tabs[_("Processing")].update_status_labels(
                self.model.trigram_valid,
                self.model.sensors_valid,
                self.model.units_valid,
                self.model.coefficients_valid
            )

    def validate_units(self, unit_sensor, unit_ref, ref_name):
        if not all(isinstance(x, str) and x.strip() for x in [unit_sensor, unit_ref, ref_name]):
            logger.error(_("Invalid units or reference name"))
            raise ValueError(_("Units and reference name must be non-empty strings"))
        self.model.set_units(unit_sensor, unit_ref, ref_name)
        logger.info(_("Units validated: {}, {}, {}").format(unit_sensor, unit_ref, ref_name))
        # Mettre à jour les statuts
        if self.view and hasattr(self.view.tabs[_("Processing")], 'update_status_labels'):
            self.view.tabs[_("Processing")].update_status_labels(
                self.model.trigram_valid,
                self.model.sensors_valid,
                self.model.units_valid,
                self.model.coefficients_valid
            )

    def validate_coefficients(self, coef_a, coef_b):
        try:
            coef_a = float(coef_a)
            coef_b = float(coef_b)
        except ValueError:
            logger.error(_("Invalid coefficients: {}, {}").format(coef_a, coef_b))
            raise ValueError(_("Coefficients must be numbers"))
        self.model.set_coefficients(coef_a, coef_b)
        logger.info(_("Coefficients validated: {}, {}").format(coef_a, coef_b))
        # Mettre à jour les statuts
        if self.view and hasattr(self.view.tabs[_("Processing")], 'update_status_labels'):
            self.view.tabs[_("Processing")].update_status_labels(
                self.model.trigram_valid,
                self.model.sensors_valid,
                self.model.units_valid,
                self.model.coefficients_valid
            )

    def change_language(self, language):
        from core.utils.i18n import set_language
        lang_map = {"Français": "fr", "English": "en"}
        if language in lang_map:
            set_language(lang_map[language])
            logger.info(_("Language changed to {}").format(language))
            if self.view:
                self.view.refresh_ui()
        else:
            logger.error(_("Unsupported language: {}").format(language))
            messagebox.showerror(_("Error"), _("Unsupported language: {}").format(language))