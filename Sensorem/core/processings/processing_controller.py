# core/controllers/processing_controller.py
from ..utils.i18n import _
from ..utils.logger import logger
from tkinter import messagebox

class ProcessingController:
    def __init__(self, view, model, load_csv_callback):
        self.view = view
        self.model = model
        self.load_csv_callback = load_csv_callback
        self._processing_selection = False
        self.bind_events()
        self.refresh_file_list()

    def bind_events(self):
        """Lier les événements des widgets."""
        self.view.files_listbox.bind("<<ListboxSelect>>", self.on_file_select)
        self.view.trigramme_button.configure(command=self.validate_trigramme)
        self.view.capteurs_manager.validate_button.configure(command=self.validate_capteurs)
        self.view.unites_button.configure(command=self.validate_unites)
        self.view.coefficients_button.configure(command=self.validate_coefficients)
        for capteur in self.view.capteurs_manager.capteurs:
            capteur.nom_entry.bind("<FocusIn>", self.restore_file_selection)
            capteur.debut_entry.bind("<FocusIn>", self.restore_file_selection)
        self.view.trigramme_entry.bind("<FocusIn>", self.restore_file_selection)
        self.view.unit_capteurs_entry.bind("<FocusIn>", self.restore_file_selection)
        self.view.unit_ref_entry.bind("<FocusIn>", self.restore_file_selection)
        self.view.nom_ref_entry.bind("<FocusIn>", self.restore_file_selection)
        self.view.coef_a_entry.bind("<FocusIn>", self.restore_file_selection)
        self.view.coef_b_entry.bind("<FocusIn>", self.restore_file_selection)

    def refresh_file_list(self):
        """Rafraîchir la liste des fichiers."""
        files = self.model.get_csv_files()
        self.view.files_listbox.delete(0, tk.END)
        for file in files:
            self.view.files_listbox.insert(tk.END, file)
        self.initialize_selection()

    def initialize_selection(self):
        """Initialiser la sélection de la listbox."""
        logger.debug(_("Initializing listbox selection"))
        if self.view.files_listbox.size() > 0:
            self.view.files_listbox.select_set(0)
            self.view.files_listbox.activate(0)
            self.model.selected_file_index = 0
            self.on_file_select(None)
        else:
            logger.debug(_("No files to select"))

    def restore_file_selection(self, event=None):
        """Restaurer la sélection précédente."""
        logger.debug(_("Restoring selection: index={}").format(self.model.selected_file_index))
        if self._processing_selection:
            logger.debug(_("Restoration blocked: _processing_selection is True"))
            return
        if self.model.selected_file_index is not None and self.view.files_listbox.size() > self.model.selected_file_index:
            self._processing_selection = True
            try:
                current_selection = self.view.files_listbox.curselection()
                if current_selection != (self.model.selected_file_index,):
                    self.view.files_listbox.select_set(self.model.selected_file_index)
                    self.view.files_listbox.activate(self.model.selected_file_index)
                    logger.debug(_("Selection restored to index {}").format(self.model.selected_file_index))
            finally:
                self._processing_selection = False
        else:
            logger.debug(_("No selection to restore or invalid index"))

    def on_file_select(self, event):
        """Gérer la sélection d'un fichier."""
        logger.debug(_("Event triggered: selection"))
        if self._processing_selection:
            logger.debug(_("Event blocked: _processing_selection is True"))
            return
        self._processing_selection = True
        try:
            selected_indices = self.view.files_listbox.curselection()
            files = self.model.get_csv_files()
            if not selected_indices and self.model.selected_file_index is not None:
                logger.debug(_("Returning to previous selection: index={}").format(self.model.selected_file_index))
                selected_file = files[self.model.selected_file_index]
            elif not selected_indices:
                logger.warning(_("No file selected in the list"))
                messagebox.showwarning(_("No Selection"), _("Please select a file from the list."))
                selected_file = None
            else:
                index = selected_indices[0]
                selected_file = self.model.select_file(index, files)
            if selected_file:
                logger.info(_("File selected: {}").format(selected_file))
                resultat = self.model.process_file(selected_file)
                self.view.treatment_text.configure(state="normal")
                self.view.treatment_text.delete("1.0", "end")
                self.view.treatment_text.insert("1.0", resultat)
                self.view.treatment_text.configure(state="disabled")
            else:
                logger.debug(_("No file selected for processing"))
        finally:
            self._processing_selection = False
            logger.debug(_("Selection event completed"))

    def validate_trigramme(self):
        """Valider le trigramme."""
        trigramme = self.view.trigramme_var.get()
        if not self.model.validate_trigramme(trigramme):
            self.view.trigramme_var.set("Bbu")
            messagebox.showerror(_("Validation Error"), _("Trigram must be exactly 3 letters."))
        self.update_status_labels()

    def validate_capteurs(self):
        """Valider les capteurs."""
        capteurs = [capteur.get_values() for capteur in self.view.capteurs_manager.capteurs]
        if not self.model.validate_capteurs(capteurs):
            messagebox.showerror(_("Validation Error"), _("Invalid sensor configuration."))
        self.update_status_labels()

    def validate_unites(self):
        """Valider les unités."""
        unit_capteurs = self.view.unit_capteurs_var.get().strip()
        unit_ref = self.view.unit_ref_var.get().strip()
        nom_ref = self.view.nom_ref_var.get().strip()
        if not self.model.validate_unites(unit_capteurs, unit_ref, nom_ref):
            messagebox.showerror(_("Validation Error"), _("Units and reference name must be provided."))
        self.update_status_labels()

    def validate_coefficients(self):
        """Valider les coefficients."""
        coef_a = self.view.coef_a_var.get().strip()
        coef_b = self.view.coef_b_var.get().strip()
        if not self.model.validate_coefficients(coef_a, coef_b):
            messagebox.showerror(_("Validation Error"), _("Invalid coefficients."))
        self.update_status_labels()

    def update_status_labels(self):
        """Mettre à jour les labels de statut."""
        self.view.trigramme_status.configure(text="✅" if self.model.state["trigramme_valide"] else "❌")
        self.view.unites_status.configure(text="✅" if self.model.state["unites_valides"] else "❌")
        self.view.coefficients_status.configure(text="✅" if self.model.state["coefficients_valides"] else "❌")
        self.view.capteurs_manager.status_label.configure(text="✅" if self.model.state["capteurs_valides"] else "❌")