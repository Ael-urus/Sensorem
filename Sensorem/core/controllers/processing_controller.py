# core/controllers/processing_controller.py
import re
from tkinter import messagebox # Ou utiliser les méthodes de la vue pour afficher les messages
from typing import TYPE_CHECKING

# Modules internes (supposons qu'ils existent et fournissent les services nécessaires)
# from core.reporting.pdf_generator import PdfGenerator # Exemple
# from core.processing.signal_processor import SignalProcessor # Exemple
# from core.utils.logger import LogManager # Type hint pour log_manager
from ..utils.i18n import _, _f # Import des fonctions de traduction

# Pour éviter les imports circulaires pour le type hinting
if TYPE_CHECKING:
    from ..gui.processing_tab import ProcessingTab
    from ..utils.logger import LogManager # S'assure que LogManager est défini pour le hinting

class ProcessingController:
    def __init__(self, view: 'ProcessingTab', log_manager: 'LogManager', pdf_generator=None, signal_processor=None, app_state=None):
        """
        Initialise le contrôleur.

        Args:
            view: L'instance de la vue (ProcessingTab) associée.
            log_manager: L'instance du gestionnaire de logs.
            pdf_generator: Service pour générer les PDF (Modèle/Service).
            signal_processor: Service pour traiter les signaux (Modèle/Service).
            app_state: Objet ou dictionnaire gérant l'état global de l'application
                       (ex: dossier courant). Peut aussi être un contrôleur principal.
        """
        self.view = view
        self.log_manager = log_manager
        self.pdf_generator = pdf_generator # À remplacer par la vraie instance
        self.signal_processor = signal_processor # À remplacer par la vraie instance
        self.app_state = app_state # À remplacer par la vraie instance/mécanisme

        # États internes pour suivre la validation (remplace fg.set_state pour cette logique)
        self.trigram_valid = False
        self.units_valid = False
        self.sensors_valid = False
        # D'autres états si nécessaire (ex: coefficients_valid)

    def handle_validate_trigram(self):
        """Logique de validation du trigramme."""
        trigram = self.view.get_trigram()
        if len(trigram) != 3 or not trigram.isalpha():
            self.view.show_error(
                _("Validation Error"),
                _("The trigram must contain exactly 3 letters.")
            )
            self.view.clear_trigram_input("???")
            self.trigram_valid = False
            self.log_manager.warning(_("Invalid trigram attempt.")) # Log plus précis
        else:
            self.trigram_valid = True
            self.log_manager.info(_f("Trigram validated: {0}", trigram))
            # Optionnel: Désactiver le champ ou le bouton après validation réussie ?
            # self.view.set_trigram_entry_state(False)

    def handle_validate_units(self):
        """Logique de validation des unités."""
        unit, unit_ref, nom_ref = self.view.get_unit_values()
        if not unit or not unit_ref or not nom_ref:
            self.view.show_error(
                _("Validation Error"),
                _("All unit fields must be filled.")
            )
            self.units_valid = False
            self.log_manager.warning(_("Unit validation failed: Missing fields."))
        else:
            self.units_valid = True
            self.log_manager.info(_f("Units validated: Sensor={0}, Ref={1}, RefName={2}", unit, unit_ref, nom_ref))
            # Optionnel: Désactiver les champs après validation ?
            # self.view.set_unit_fields_state(False)

    def handle_validate_sensors(self):
        """Logique de validation des capteurs."""
        infos = self.view.get_sensor_info()
        is_valid = True
        if not infos:
            is_valid = False
        else:
            for nom, debut in infos:
                if not nom or not debut: # Ajouter une validation plus poussée si nécessaire (ex: debut est un nombre)
                    is_valid = False
                    break

        if not is_valid:
            self.view.show_error(
                 _("Validation Error"),
                 _("All sensors must have a non-empty name and start value.")
            )
            self.sensors_valid = False
            self.log_manager.warning(_("Sensor validation failed: Missing or invalid sensor data."))
        else:
            self.sensors_valid = True
            self.log_manager.info(_f("Sensors validated: {0}", infos))
            # Optionnel: Désactiver le bouton "Add sensor" ou le frame après validation ?
            # self.view.set_sensor_frame_state(False)


    def handle_generate_pdf(self):
        """Logique pour générer le PDF."""
        # 1. Vérifier si les étapes précédentes sont valides
        if not self.trigram_valid or not self.units_valid or not self.sensors_valid:
            self.view.show_error(
                _("PDF Generation Error"),
                _("Please validate Trigram, Units, and Sensors before generating the PDF.")
            )
            return

        # 2. Récupérer les informations nécessaires depuis la Vue et l'état de l'application
        selected_file = self.view.get_selected_file_from_list()
        if not selected_file:
             self.view.show_error(_("PDF Generation Error"), _("Please select a file from the list."))
             return

        # Assumons que app_state fournit le dossier courant
        current_directory = self.app_state.get_current_directory() if self.app_state else "." # Placeholder
        if not current_directory:
             self.view.show_error(_("Configuration Error"), _("Current directory not set."))
             return

        trigram = self.view.get_trigram()
        unit_sensor, unit_ref, ref_name = self.view.get_unit_values()
        # Récupérer les infos capteurs (si nécessaire pour le PDF, sinon déjà validées)
        sensor_infos = self.view.get_sensor_info()
        # Récupérer les coefficients (si nécessaire)
        coeff1, coeff2 = self.view.get_coefficients() # Exemple, ajoutez la validation si besoin

        # TODO: Récupérer les numéros de colonne (était dans fg.num_colonne_lire)
        # Cela doit venir soit de la config, soit de la logique métier, soit d'une partie de l'UI dédiée
        col_sensor = 1 # Placeholder
        col_ref = 2 # Placeholder


        # 3. Appeler le service de génération PDF (Modèle/Service)
        if not self.pdf_generator:
            self.view.show_error(_("Configuration Error"), _("PDF Generator service not available."))
            self.log_manager.error("PDF Generator service not initialized.")
            return

        try:
            self.log_manager.info(_f("Attempting PDF generation for file: {0}", selected_file))
            # L'API de votre PdfGenerator peut varier
            pdf_success = self.pdf_generator.generate(
                output_dir=current_directory,
                source_file_name=selected_file, # Ou chemin complet si nécessaire
                user_trigram=trigram,
                sensor_column=col_sensor,
                reference_column=col_ref,
                unit_info=(unit_sensor, unit_ref, ref_name),
                # Passez d'autres infos si nécessaire: sensor_infos, coefficients...
            )

            if pdf_success:
                self.view.show_info(_("Success"), _("PDF successfully generated"))
                self.log_manager.info(_("PDF generation successful."))
            else:
                # Si generate() retourne False au lieu de lever une exception
                self.view.show_error(_("PDF Generation Error"), _("PDF generation failed. Check logs."))
                self.log_manager.error(_("PDF generation failed for an unknown reason."))

        except Exception as e:
            self.view.show_error(
                _("PDF Generation Error"),
                _f("An error occurred during PDF generation: {0}", str(e))
            )
            self.log_manager.exception(_f("Exception during PDF generation for {0}", selected_file))

    def update_file_list_view(self, file_list: list):
        """ Met à jour la liste de fichiers dans la vue. """
        self.view.update_file_list(file_list)

    def process_selected_file(self):
        """ Lance le traitement du fichier sélectionné dans la liste. """
        selected_file = self.view.get_selected_file_from_list()
        if not selected_file:
            self.view.update_output_text(_("Please select a file to process."))
            return

        # Placeholder pour la logique de traitement
        self.view.update_output_text(_f("Processing file: {0}...\n", selected_file))
        self.log_manager.info(_f("Starting processing for file: {0}", selected_file))

        # TODO: Appeler ici votre self.signal_processor.process(...)
        try:
            # result = self.signal_processor.process(file_path, ...)
            # Supposons que le processeur met à jour les graphiques via un mécanisme de callback ou retourne des données
            result_text = f"File {selected_file} processed successfully.\n" # Placeholder
            result_text += "Displaying results in graphs and output area." # Placeholder
            self.view.update_output_text(result_text)
            self.log_manager.info(_f("Processing finished for file: {0}", selected_file))

            # TODO: Mettre à jour les graphiques (le contrôleur pourrait avoir des références
            # aux objets graphiques ou appeler une méthode de la vue pour le faire)
            # self.view.update_graph1(result.graph1_data)
            # self.view.update_graph2(result.graph2_data)

        except Exception as e:
             error_message = _f("Error processing file {0}: {1}", selected_file, str(e))
             self.view.update_output_text(error_message)
             self.log_manager.exception(error_message)