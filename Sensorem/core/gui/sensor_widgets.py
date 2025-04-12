# core/gui/sensor_widgets.py
import tkinter as tk
from tkinter import ttk
from ..utils.i18n import _ # Assurez-vous que le chemin d'import est correct

class CapteurFrame(ttk.Frame):
    def __init__(self, master, is_first=False):
        super().__init__(master)
        self.nom_var = tk.StringVar()
        self.debut_var = tk.StringVar()
        self.is_first = is_first # Gardez cette logique si elle est importante

        # --- Widgets ---
        self.nom_label = ttk.Label(self, text=_("Name") + " :")
        self.nom_entry = ttk.Entry(self, textvariable=self.nom_var, width=10)
        self.debut_label = ttk.Label(self, text=_("Start") + " :")
        self.debut_entry = ttk.Entry(self, textvariable=self.debut_var, width=10)

        # --- Layout ---
        self.nom_label.grid(row=0, column=0, padx=(0, 2), sticky="w")
        self.nom_entry.grid(row=0, column=1, padx=(0, 5))
        self.debut_label.grid(row=0, column=2, padx=(5, 2), sticky="w")
        self.debut_entry.grid(row=0, column=3, padx=(0, 5))

        if not self.is_first:
            self.delete_button = ttk.Button(self, text=_("Remove"), command=self.supprimer, width=8) # Largeur fixe?
            self.delete_button.grid(row=0, column=4, padx=(5, 0))
        else:
             # Ajoutez un espace réservé pour l'alignement si nécessaire
             ttk.Frame(self, width=int(8 * 8.5)).grid(row=0, column=4, padx=(5,0)) # Approximation largeur bouton

    def supprimer(self):
        # La méthode supprimer appelle la méthode remove_capteur de son parent (CapteursManager)
        # hasattr est une sécurité si le parent n'a pas cette méthode pour une raison quelconque
        if hasattr(self.master, 'remove_capteur') and callable(self.master.remove_capteur):
             self.master.remove_capteur(self)
        else:
            print("Error: Parent does not have 'remove_capteur' method") # Log d'erreur

    def get_values(self) -> tuple[str, str]:
        """Retourne le nom et le début du capteur."""
        return self.nom_var.get(), self.debut_var.get()

    def set_values(self, nom: str, debut: str):
        """Définit les valeurs des champs."""
        self.nom_var.set(nom)
        self.debut_var.set(debut)

    def set_state(self, state: str):
        """Active ou désactive les champs et le bouton (ex: tk.DISABLED)."""
        for widget in (self.nom_entry, self.debut_entry):
            widget.configure(state=state)
        if hasattr(self, 'delete_button'):
            self.delete_button.configure(state=state)


class CapteursManager(ttk.LabelFrame): # Utiliser un LabelFrame peut être sympa visuellement
    def __init__(self, master):
        super().__init__(master, text=_("Sensors")) # Ajout d'un titre au cadre
        self.capteurs_frames: list[CapteurFrame] = [] # Liste pour stocker les frames CapteurFrame

        # Frame interne pour contenir les CapteurFrame et le bouton Add
        # Cela permet au LabelFrame de bien s'adapter au contenu
        content_frame = ttk.Frame(self)
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.capteurs_container = ttk.Frame(content_frame) # Frame pour empiler les CapteurFrame
        self.capteurs_container.pack(fill="x", expand=True)

        self.add_button = ttk.Button(content_frame, text=_("Add sensor"), command=self._add_capteur_ui)
        self.add_button.pack(anchor="w", pady=(5,0))

        # Ajouter le premier capteur par défaut
        self.add_capteur("H_", "0", True)

    def _add_capteur_ui(self):
        """Ajoute un nouveau capteur via l'UI (appelé par le bouton)."""
        self.add_capteur() # Ajoute avec des valeurs par défaut

    def add_capteur(self, nom="", debut="", is_first=False):
        """Crée et ajoute un CapteurFrame à la liste et à l'UI."""
        # Crée le nouveau CapteurFrame dans le conteneur dédié
        capteur_frame = CapteurFrame(self.capteurs_container, is_first=is_first)
        capteur_frame.pack(anchor="w", pady=1, fill="x") # fill='x' pour occuper la largeur
        self.capteurs_frames.append(capteur_frame)

        # Pré-remplir les valeurs si fournies
        if nom or debut:
            capteur_frame.set_values(nom, debut)

    def remove_capteur(self, capteur_frame: CapteurFrame):
        """Supprime un CapteurFrame de la liste et de l'UI."""
        if capteur_frame in self.capteurs_frames and not capteur_frame.is_first:
            self.capteurs_frames.remove(capteur_frame)
            capteur_frame.destroy() # Détruit le widget de l'UI

    def get_capteurs_info(self) -> list[tuple[str, str]]:
        """Récupère les informations (nom, début) de tous les capteurs."""
        return [cf.get_values() for cf in self.capteurs_frames]

    def reset_capteurs(self):
        """Supprime tous les capteurs sauf le premier et le réinitialise."""
        # Itérer en sens inverse pour éviter les problèmes d'index lors de la suppression
        for cf in reversed(self.capteurs_frames):
            if not cf.is_first:
                self.remove_capteur(cf)

        # Réinitialiser le premier capteur si besoin
        if self.capteurs_frames: # S'assurer qu'il en reste au moins un
             self.capteurs_frames[0].set_values("H_", "0")

    def set_state(self, state: str):
         """Active ou désactive tous les CapteurFrame et le bouton Ajouter."""
         for cf in self.capteurs_frames:
             cf.set_state(state)
         self.add_button.configure(state=state)