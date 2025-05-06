# core/models/processing_model.py
import os
import glob
import re
from ..utils.i18n import _
from ..utils.logger import logger

class ProcessingModel:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.state = {
            "trigramme_valide": False,
            "capteurs_valides": False,
            "unites_valides": False,
            "coefficients_valides": False
        }
        self.trigramme = "Bbu"
        self.capteurs = [("H_", "0")]  # Liste de tuples (nom, debut)
        self.unit_capteurs = "[V]"
        self.unit_ref = "[m/s]"
        self.nom_ref = "Venturi"
        self.coef_a = 1.0
        self.coef_b = 0.0
        self.selected_file = None
        self.selected_file_index = None

    def get_csv_files(self):
        """Récupérer la liste des fichiers CSV."""
        files = [os.path.basename(f) for f in glob.glob(os.path.join(self.base_dir, "*.csv"))]
        if not files:
            logger.warning(_("No CSV files found in directory: {}").format(self.base_dir))
        return files

    def validate_trigramme(self, trigramme):
        """Valider le trigramme."""
        if len(trigramme) != 3 or not trigramme.isalpha():
            logger.error(_("Trigram must be exactly 3 letters."))
            self.state["trigramme_valide"] = False
            return False
        self.trigramme = trigramme
        self.state["trigramme_valide"] = True
        logger.info(_("Trigram validated: {}").format(trigramme))
        return True

    def validate_capteurs(self, capteurs):
        """Valider la liste des capteurs."""
        try:
            if any(not nom or not debut for nom, debut in capteurs):
                raise ValueError(_("All sensors must have a name and start line."))
            for nom, debut in capteurs:
                if not re.match(r'^[a-zA-Z0-9_]+$', nom):
                    raise ValueError(_("Sensor name '{}' is invalid.").format(nom))
                if not debut.isdigit():
                    raise ValueError(_("Start line '{}' must be a number.").format(debut))
            self.capteurs = capteurs
            self.state["capteurs_valides"] = True
            logger.info(_("Sensors validated successfully: {}").format(
                ", ".join(f"{nom} (start: {debut})" for nom, debut in capteurs)
            ))
            return True
        except ValueError as e:
            logger.error(str(e))
            self.state["capteurs_valides"] = False
            return False

    def validate_unites(self, unit_capteurs, unit_ref, nom_ref):
        """Valider les unités."""
        if not unit_capteurs or not unit_ref or not nom_ref:
            logger.error(_("Units and reference name must be provided."))
            self.state["unites_valides"] = False
            return False
        self.unit_capteurs = unit_capteurs
        self.unit_ref = unit_ref
        self.nom_ref = nom_ref
        self.state["unites_valides"] = True
        logger.info(_("Units validated: Sensor: {}, Ref: {}, Ref Name: {}").format(
            unit_capteurs, unit_ref, nom_ref
        ))
        return True

    def validate_coefficients(self, coef_a, coef_b):
        """Valider les coefficients."""
        try:
            coef_a = float(coef_a)
            coef_b = float(coef_b)
            if coef_a == 0:
                logger.error(_("Coefficient a cannot be zero."))
                self.state["coefficients_valides"] = False
                return False
            self.coef_a = coef_a
            self.coef_b = coef_b
            self.state["coefficients_valides"] = True
            logger.info(_("Coefficients validated: a={}, b={}").format(coef_a, coef_b))
            return True
        except ValueError:
            logger.error(_("Coefficients must be valid numbers."))
            self.state["coefficients_valides"] = False
            return False

    def process_file(self, filename):
        """Traiter un fichier CSV."""
        try:
            resultat = _("Processing file: {}").format(filename) + "\n"
            logger.debug(resultat.strip())
            return resultat
        except Exception as e:
            erreur = _("Error processing file: {}").format(str(e))
            logger.error(erreur)
            return erreur

    def select_file(self, index, files):
        """Sélectionner un fichier."""
        if not files or index < 0 or index >= len(files):
            logger.warning(_("No file selected in the list"))
            self.selected_file = None
            return None
        self.selected_file_index = index
        self.selected_file = files[index]
        logger.debug(_("File selected: {}").format(self.selected_file))
        return self.selected_file