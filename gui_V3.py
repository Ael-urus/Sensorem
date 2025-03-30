#!/usr/bin/python
# -*- coding: utf-8 -*-
# gui_V3.py.py

import os
import os.path
import re
import sys
import tkinter as tk
import traceback
from idlelib.tooltip import Hovertip  # Importation du module pour les infobulles
from tkinter import ttk, messagebox
from typing import List, Tuple


from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

try:
    #import de mes fonctions
    import FonctionsSignal as fs
    import FonctionsPdf as pdf
    import FonctionsGui_V3 as fg
    import FonctionsDB as fdb
    from FonctionsDB import GestionnaireFenetreDB

except Exception as e:
    print(f"Une exception s'est produite dans le module {__name__}: {e}")
    print(f"Fichier en cours d'exécution : {os.path.basename(__file__)}")
    input('Appuyez sur Entrée pour continuer...')
    sys.exit(1)


# Exemple de gestion de l'état
def valider_trigramme() -> None:
    """Valide le trigramme saisi par l'utilisateur.

    Vérifie si le trigramme comporte exactement 3 lettres et met à jour l'état de validation en conséquence.
    Si le trigramme est valide, il est enregistré dans les logs. Si le trigramme est invalide, une erreur est affichée à l'utilisateur et le champ est réinitialisé.
    Met également à jour l'état du bouton PDF.

    Args:
        None.

    Returns:
        None.
    """
    # Récupère le champ de saisie du trigramme depuis l'objet FrameGlobal.
    champ_trigramme: tk.Entry = fg.get_state("champ_trigramme")  # type: ignore
    # Récupère la valeur saisie dans le champ.
    trigramme: str = champ_trigramme.get()

    # Vérifie si le trigramme est valide : 3 lettres alphabétiques.
    if len(trigramme) != 3 or not trigramme.isalpha():
        # Trigramme invalide : affiche une erreur.
        messagebox.showerror("Erreur de validation", "Le trigramme doit comporter exactement 3 lettres.")
        # Réinitialise le champ de saisie.
        champ_trigramme.delete(0, "end")
        champ_trigramme.insert(0, "???")
        # Met à jour l'état de validation à False.
        fg.set_state("trigramme_valide", False)  # type: ignore
    else:
        # Trigramme valide : enregistre un message dans les logs.
        fg.log_message(f"Trigramme : {trigramme}, validé.\n", "INFO")  # type: ignore
        # Met à jour l'état de validation à True.
        fg.set_state("trigramme_valide", True)  # type: ignore

    # Met à jour l'état du bouton PDF.
    mettre_a_jour_bouton_pdf()  # type: ignore

def mettre_a_jour_bouton_pdf() -> None:
    """Met à jour l'état du bouton de génération PDF.

    Active le bouton PDF si le trigramme, les capteurs et les unités sont valides, sinon le désactive.

    Returns:
        None.
    """
    # Récupère l'état de validation du trigramme.
    trigramme_valide = fg.get_state("trigramme_valide") # type: ignore
    # Récupère l'état de validation des capteurs.
    capteurs_valides = fg.get_state("capteurs_valides") # type: ignore
    # Récupère l'état de validation des unités.
    unites_valides = fg.get_state("unites_valides") # type: ignore

    # Si toutes les validations sont True, active le bouton.
    if trigramme_valide and capteurs_valides and unites_valides:
        # Configure le bouton pour l'état NORMAL (activé).
        fg.get_state("bouton_generer_pdf").config(state=tk.NORMAL) # type: ignore
    else:
        # Sinon, configure le bouton pour l'état DISABLED (désactivé).
        fg.get_state("bouton_generer_pdf").config(state=tk.DISABLED) # type: ignore

class CapteurFrame(ttk.Frame):
    """Représente un cadre pour la saisie des informations d'un capteur.

    Ce cadre contient des champs pour le nom et la ligne de début du capteur, ainsi qu'un bouton de suppression (sauf pour le premier cadre).
    """

    def __init__(self, master: ttk.Frame, is_first: bool = False, **kwargs):
        """Initialise un nouveau cadre CapteurFrame.

        Args:
            master: Le widget parent.
            is_first: Indique si c'est le premier cadre (et donc sans bouton de suppression).
            **kwargs: Arguments supplémentaires passés au constructeur de ttk.Frame.
        """
        super().__init__(master, **kwargs)
        # Variable pour le nom du capteur.
        self.nom_var: tk.StringVar = tk.StringVar()
        # Variable pour la ligne de début du capteur.
        self.debut_var: tk.StringVar = tk.StringVar()
        # Indique si c'est le premier cadre.
        self.is_first: bool = is_first

        self.create_widgets()
        self.place_widgets()
        self.add_tooltips()

    def create_widgets(self) -> None:
        """Crée les widgets du cadre."""
        # Champ de saisie pour le nom.
        self.nom_entry: ttk.Entry = ttk.Entry(self, textvariable=self.nom_var, width=10)
        # Champ de saisie pour la ligne de début.
        self.debut_entry: ttk.Entry = ttk.Entry(self, textvariable=self.debut_var, width=10)
        # Label pour le nom.
        self.nom_label: ttk.Label = ttk.Label(self, text="Nom :")
        # Label pour la ligne de début.
        self.debut_label: ttk.Label = ttk.Label(self, text="Début :")
        # Bouton de suppression (seulement si ce n'est pas le premier cadre).
        if not self.is_first:
            self.delete_button: ttk.Button = ttk.Button(self, text="Supprimer", command=self.supprimer)

    def place_widgets(self) -> None:
        """Place les widgets dans la grille."""
        self.nom_label.grid(row=0, column=0, padx=2, pady=2)
        self.nom_entry.grid(row=0, column=1, padx=2, pady=2)
        self.debut_label.grid(row=0, column=2, padx=2, pady=2)
        self.debut_entry.grid(row=0, column=3, padx=2, pady=2)
        if not self.is_first:
            self.delete_button.grid(row=0, column=4, padx=2, pady=2)

    def add_tooltips(self) -> None:
        """Ajoute des infobulles aux champs de saisie."""
        Hovertip(self.nom_entry, 'Entrez le nom du capteur')
        Hovertip(self.debut_entry, 'Entrez la ligne de début pour ce capteur')

    def supprimer(self) -> None:
        """Supprime ce cadre capteur de son parent."""
        self.master.remove_capteur(self)

    def get_values(self) -> Tuple[str, str]:
        """Récupère les valeurs du nom et de la ligne de début.

        Returns:
            Un tuple contenant le nom et la ligne de début (str, str).
        """
        return self.nom_var.get(), self.debut_var.get()

    def set_values(self, nom: str, debut: str) -> None:
        """Définit les valeurs du nom et de la ligne de début.

        Args:
            nom: Le nom du capteur.
            debut: La ligne de début du capteur.
        """
        self.nom_var.set(nom)
        self.debut_var.set(debut)

    def reset(self) -> None:
        """Réinitialise les champs nom et début à des chaînes vides."""
        self.set_values("", "")

class CapteursManager(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.capteurs = []  # Liste pour stocker les informations de chaque capteur
        self.nom_capteur_ref = ""  # Nom pour le champ "Nom capteur ref"
        self.unite_capteur_ref = ""  # Unité du capteur de référence

        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Button(button_frame, text="Ajouter Capteur", command=self.add_capteur).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Valider le ou les capteurs", command=self.valider_capteurs).pack(side=tk.LEFT, padx=5)

        self.add_capteur("H_", "0", is_first=True)  # Ajout du capteur par défaut dans l'interface graphique

    def add_capteur(self, nom: str = "", debut: str = "", is_first: bool = False) -> None:
        """
        Ajout des champs pour un nouveau capteur dans l'interface graphiqye
        Args:
            nom:
            debut:
            is_first:

        Returns:

        """
        capteur = CapteurFrame(self, is_first=is_first)
        capteur.pack(pady=2)
        self.capteurs.append(capteur)
        if nom and debut:
            capteur.set_values(nom, debut)

    def remove_capteur(self, capteur: "CapteurFrame") -> None:
        if capteur != self.capteurs[0]:  # Ne pas supprimer le premier capteur
            self.capteurs.remove(capteur)
            capteur.destroy()

    def ajouter_capteurEtPosition_a_list(self, nom_capteur, position, unite):
        """
        Ajoute un capteur avec son nom, sa position dans la liste Y et Y2, et son unité.
        Si un capteur avec le même nom existe déjà, ajoute un suffixe (a, b, c, ...) pour rendre le nom unique.

        Args:
            nom_capteur (str): Nom de base du capteur.
            position (int): Position de début dans les listes Y et Y2.
            unite (str): Unité du capteur.
        """
        # Vérifie si un capteur avec le même nom existe déjà
        nom_unique = nom_capteur
        suffixe = ord('a')  # Suffixe initial, correspond à 'a'

        # Crée un nom unique en ajoutant un suffixe en cas de doublon
        existing_names = {capteur["nom"] for capteur in self.capteurs}
        while nom_unique in existing_names:
            nom_unique = f"{nom_capteur}{chr(suffixe)}"
            suffixe += 1

        # Ajoute le capteur avec le nom unique
        self.capteurs.append({"nom": nom_unique, "position": position, "unite": unite})

    def set_nom_capteur_ref(self, nom_ref, unite_ref):
        """
        Définit le nom de référence et l'unité du capteur de référence.

        Args:
            nom_ref (str): Nom du capteur de référence.
            unite_ref (str): Unité du capteur de référence.
        """
        self.nom_capteur_ref = nom_ref
        self.unite_capteur_ref = unite_ref

    def get_names_position_capteurs(self) -> List[Tuple[str, int]]:
        """
        Récupère le nom et la position de début des capteurs sous forme de liste de tuples.

        Returns:
            List[Tuple[str, int]]: Liste de tuples contenant le nom et la position de chaque capteur.
                                   Ex : [('H1', 24), ('H5', 53), ...]
        """
        """values = [
            #(capteur["nom"], int(capteur["position"]))
            (capteur["nom"], (capteur["position"]))

            for capteur in self.capteurs
            if "nom" in capteur and "position" in capteur
        ]"""
        values = [capteur.get_values() for capteur in self.capteurs]
        return values

    def get_info_unite(self):
        """
        Retourne un dictionnaire contenant les noms et unités des capteurs à raccorder,
        ainsi que le nom et l'unité du capteur de référence.
        """
        # Récupérer les noms et unités des capteurs
        info_unites = {
            "capteurs": {
                capteur.get_values()[0]: capteur.get_values()[1]  # Nom et unité des capteurs
                for capteur in self.capteurs if capteur.get_values()[0]  # Vérifie que le nom n'est pas vide
            },
            "capteur_ref": {
                "nom": self.nom_capteur_ref,
                "unite": self.unite_capteur_ref
            }
        }
        return info_unites

    def get_capteurs_info(self) -> List[Tuple[str, str]]:
        """Retourne les informations des capteurs sous forme de liste de tuples (nom, debut)."""
        return [capteur.get_values() for capteur in self.capteurs]

    def update_capteurs_names(self, Y, Y2):
        """
        Met à jour les listes Y et Y2 avec les noms de capteurs et leurs positions respectives.

        Args:
            Y (list): Liste des valeurs de mesure pour le capteur principal.
            Y2 (list): Liste des valeurs de mesure pour le capteur de référence.

        Returns:
            tuple: Les listes Y et Y2 mises à jour.
        """
        for nom_capteur, info in self.capteurs.items():
            position = info["position"]

            # Ajoute le nom du capteur principal dans Y à la position spécifiée
            if position < len(Y):
                Y[position] = nom_capteur
            else:
                # Complète Y avec des espaces vides si nécessaire
                Y.extend([""] * (position - len(Y)))
                Y.append(nom_capteur)

            # Ajoute "Nom capteur ref <nom_capteur>" dans Y2 à la position spécifiée
            ref_capteur = f"{self.nom_capteur_ref} {nom_capteur}"
            if position < len(Y2):
                Y2[position] = ref_capteur
            else:
                # Complète Y2 avec des espaces vides si nécessaire
                Y2.extend([""] * (position - len(Y2)))
                Y2.append(ref_capteur)

        return Y, Y2

    def est_nom_fichier_valide(self,nom: str) -> bool:
        """Vérifie si un nom est valide pour un fichier, en tenant compte des contraintes multi-OS.

        Args:
            nom: Le nom à vérifier.

        Returns:
            True si le nom est valide, False sinon.
        """

        if not nom:  # Vérification pour les chaînes vides
            return False

        if len(nom) > 255:  # Vérification de la longueur maximale
            return False

        # Caractères interdits universellement (tous OS)
        interdits = r'[\\/:*?"<>|]'
        if re.search(interdits, nom):
            return False

        # Caractères interdits sous Windows
        if os.name == 'nt':
            if re.search(r'[\x00-\x1F]', nom):  # Caractères de contrôle ASCII
                return False
            if nom.endswith('.') or nom.endswith(' '):  # Noms finissant par un point ou un espace
                return False
            if nom in (".", ".."):  # Noms "." ou ".."
                return False
            if re.search(r'CON|PRN|AUX|NUL|COM[0-9]|LPT[0-9]', nom, re.IGNORECASE):  # Noms réservés Windows
                return False

        # Caractères interdits sous macOS (principalement le caractère ':')
        if os.name == 'posix' and os.uname().sysname == 'Darwin':
            if ':' in nom:
                return False

        # Caractères interdits sous Linux (principalement le caractère '/')
        if os.name == 'posix' and os.uname().sysname == 'Linux':
            if '/' in nom:  # Déjà géré par la vérification universelle, mais ajouté pour plus de clarté
                return False

        return True

    def valider_capteurs(self) -> None:
        """Valide les informations des capteurs et affiche les résultats."""
        fg.log_message("Début de la validation des capteurs", "DEBUG")
        liste_fichiers = fg.get_state("liste_fichiers")
        if not liste_fichiers:
            fg.log_message("La liste des fichiers n'est pas initialisée", "ERROR")
            messagebox.showerror("Erreur", "La liste des fichiers n'est pas initialisée")
            fg.set_state("capteurs_valides", False)
            mettre_a_jour_bouton_pdf()
            return
        fichier = liste_fichiers.get(liste_fichiers.curselection())
        if not fichier:
            fg.log_message("Aucun fichier selectionné", "WARNING")
            messagebox.showwarning("Attention", "Veuillez sélectionner un fichier.")
            fg.set_state("capteurs_valides", False)
            mettre_a_jour_bouton_pdf()
            return
        try:
            values = self.get_capteurs_info()  # Appel corrigé ici
            if any(not nom or not debut for nom, debut in values):
                raise ValueError("Tous les capteurs doivent avoir un nom et un début.")

            for nom, debut in values:
                if not self.est_nom_fichier_valide(nom):
                    raise ValueError(f"Le nom du capteur '{nom}' est invalide.")

            self.afficher_graphique2(fichier)
            self.afficher_infos("general")
            fg.set_state("capteurs_valides", True)
            fg.log_message("Validation des capteurs terminée avec succès", "INFO")
        except ValueError as e:
            fg.log_message(f"Erreur de validation : {e}", "WARNING")
            messagebox.showerror("Erreur de validation", str(e))
            fg.set_state("capteurs_valides", False)
        except Exception as e:
            fg.log_message(f"Erreur inattendue : {e}\n{traceback.format_exc()}", "ERROR")
            messagebox.showerror("Erreur", f"Une erreur s'est produite : {e}")
            fg.set_state("capteurs_valides", False)
        finally:
            mettre_a_jour_bouton_pdf()

    def reset_capteurs(self) -> None:
        for capteur in self.capteurs[1:]:  # Supprime tous les capteurs sauf le premier
            capteur.destroy()
        self.capteurs = [self.capteurs[0]]
        #self.capteurs[0].set_values("H8", "0")
        fg.set_state("capteurs_valides", False)
        mettre_a_jour_bouton_pdf()

    def afficher_infos(self, type_affichage="general") -> None:
        """Affiche les informations des capteurs dans la zone de texte.

        Args:
            type_affichage (str, optional): Le type d'affichage souhaité.
                Peut être "general" (informations générales et traitement) ou "traitement" (uniquement le traitement).
                Par défaut "general".

        Raises:
            ValueError: Si le type d'affichage n'est pas reconnu.
        """
        fichier = fg.nom_fichier_selectionne()
        if not fichier:  # Gestion du cas ou aucun fichier est selectionné
            return
        if type_affichage == "general":
            info = f"Traitement du fichier : {fichier}\n"
            info += f"Nombre de capteurs validés : {len(self.capteurs)}\n"
            info += "Noms du/des capteur (s) : " + ", ".join(capteur.nom_var.get() for capteur in self.capteurs) + "\n"
            info += fg.traitement_fichier()  # On ajoute le traitement
        elif type_affichage == "traitement":
            info = f"Traitement du fichier : {fichier}\n"
            info += fg.traitement_fichier()
        else:
            raise ValueError("Type d'affichage non reconnu.")

        zone_texte_traitement_fichier = fg.get_state("zone_texte_traitement_fichier")
        if zone_texte_traitement_fichier:  # Gestion du cas ou la zone de texte n'existe pas
            zone_texte_traitement_fichier.delete('1.0', tk.END)
            zone_texte_traitement_fichier.insert(tk.END, info)
        else:
            fg.log_message("Zone texte traitement non initialisé", "ERROR")

    def afficher_traitement_capteurs(self) -> None:
        info = f"Traitement du fichier : {str(fg.nom_fichier_selectionne())}\n"
        info += fg.traitement_fichier()
        zone_texte_traitement_fichier = fg.get_state("zone_texte_traitement_fichier")
        zone_texte_traitement_fichier.delete('1.0', tk.END)
        zone_texte_traitement_fichier.insert(tk.END, info)

    def afficher_graphique2(self, nomFichier):
        """Affiche le deuxième graphique dans zone_graphique2."""
        try:
            zone_graphique2 = fg.get_state("zone_graphique2")

            # Récupération des données brutes
            donnees = fg.get_data_from_file(nomFichier)

            # Vérification cruciale : s'assurer que les données existent et ont la bonne structure
            if not donnees or not isinstance(donnees, list) or len(donnees) < 2:
                print(f"Erreur : Données incorrectes ou insuffisantes pour {nomFichier}. Données : {donnees}")
                fg.log_message(f"Erreur : Données incorrectes ou insuffisantes pour {nomFichier}. Données : {donnees}",
                               "ERREUR")
                # Afficher un message à l'utilisateur dans l'interface graphique
                messagebox.showerror("Erreur de données",
                                     f"Le fichier {nomFichier} ne contient pas les données attendues.")
                cacher_graphique2()  # cacher le graph pour ne pas avoir d'erreur
                return  # Important : sortir de la fonction en cas d'erreur

            # Traitement des données pour chaque capteur
            donnees_traitees = []
            for i, data in enumerate(donnees):  # Itérer avec l'index pour un meilleur débogage
                try:
                    seuil = fs.seuil_capteur1() if i == 0 else fs.seuil_capteur2()
                    _, data_with_paliers = fs.get_data_with_paliers(data, seuil)
                    donnees_traitees.append(data_with_paliers)
                except IndexError as e:
                    print(f"Erreur d'index lors du traitement du capteur {i + 1} : {e}")
                    fg.log_message(f"Erreur d'index lors du traitement du capteur {i + 1} : {e}", "ERREUR")
                    messagebox.showerror("Erreur de données", f"Erreur lors du traitement du capteur {i + 1} : {e}")
                    return
                except Exception as e:
                    print(f"Erreur lors du traitement du capteur {i + 1} : {e}")
                    fg.log_message(f"Erreur lors du traitement du capteur {i + 1} : {e}", "ERREUR")
                    messagebox.showerror("Erreur de données", f"Erreur lors du traitement du capteur {i + 1} : {e}")
                    return

            # Affichage des données traitées
            afficher_graphique(donnees_traitees, zone_graphique2, titre="Données traitées")
            zone_graphique2.grid()
        except Exception as e:
            print(f"Erreur dans afficher_graphique2 : {e}")
            traceback.print_exc()  # Pour afficher la trace complète de l'erreur
            fg.log_message(f"Erreur lors de l'affichage du graphique 2 : {e}", "ERROR")


def on_file_select(event: tk.Event) -> None:
    """Gère la sélection d'un fichier dans la liste.

    Affiche les informations du fichier sélectionné dans la zone de texte,
    met à jour les graphiques et réinitialise les capteurs.

    Args:
        event: L'événement de sélection du fichier.
    """
    # Récupère la liste des fichiers depuis l'objet fg.
    liste_fichiers = fg.get_liste_fichiers()
    # Vérifie si un élément est sélectionné dans la liste.
    if not liste_fichiers.curselection():
        print("Aucun fichier sélectionné")
        fg.log_message("Aucun fichier sélectionné", "WARNING")
        return  # Si aucun fichier n'est sélectionné, on sort de la fonction.

    # Récupère le nom du fichier sélectionné.
    fichier: str = fg.nom_fichier_selectionne()

    # Récupère la zone de texte pour l'affichage des informations.
    zone_texte_traitement_fichier: tk.Text = fg.get_state("zone_texte_traitement_fichier")

    # Efface le contenu précédent de la zone de texte.
    zone_texte_traitement_fichier.delete('1.0', tk.END)
    # Insère le nom du fichier sélectionné dans la zone de texte.
    zone_texte_traitement_fichier.insert(tk.END, f"Fichier sélectionné : {fichier}\n")
    fg.log_message(f"Fichier sélectionné : {fichier}\n", "INFO")

    # Met à jour le premier graphique.
    afficher_graphique1(fichier)
    # Cache le deuxième graphique.
    cacher_graphique2()
    # Réinitialise les capteurs via le gestionnaire de capteurs.
    fg.get_state("capteurs_manager").reset_capteurs()

def on_listbox_lose_focus(event: tk.Event) -> None:
    """Gère la perte de focus de la liste des fichiers."""
    liste_fichiers = fg.get_state("liste_fichiers")
    selection = liste_fichiers.curselection()

    # Si une sélection existe, la restaurer
    if selection:
        liste_fichiers.selection_set(selection)
        liste_fichiers.see(selection)  # Faire défiler pour afficher l'élément sélectionné

def afficher_graphique(donnees: List[List], zone_graphique: ttk.Frame, titre: str = "un titre") -> None:
    """Affiche un graphique dans la zone graphique.

    Efface le contenu précédent de la zone graphique, récupère les unités et le nom du capteur de référence,
    puis trace le graphique avec les données fournies.

    Args:
        donnees: Liste de listes de données à tracer.
        zone_graphique: Zone graphique où tracer le graphique.
        titre: Titre du graphique.
    """
    # Détruit tous les widgets enfants de la zone graphique pour effacer le graphique précédent.
    for widget in zone_graphique.winfo_children():
        widget.destroy()

    # Récupère les variables d'unité et de nom du capteur de référence depuis l'objet fg.
    champ_unit_capteurs: tk.StringVar = fg.get_state("champ_unit_capteurs")
    champ_unit_capteur_ref: tk.StringVar = fg.get_state("champ_unit_capteur_ref")
    champ_nom_capteur_ref: tk.StringVar = fg.get_state("champ_nom_capteur_ref")

    # Récupère les valeurs des unités et du nom, en supprimant les espaces superflus.
    unit: str = champ_unit_capteurs.get().strip()
    unit_ref: str = champ_unit_capteur_ref.get().strip()
    nom_ref: str = champ_nom_capteur_ref.get().strip()

    # Crée les légendes pour le graphique.
    Legende: List[str] = ['Capteur (s) passé (s)' + unit, 'Capteur_ref :' + nom_ref + ' ' + unit_ref]

    # Définit les styles pour les lignes du graphique.
    styles = [
        {'linestyle': '-', 'marker': 'None', 'linewidth': '0.6'},
        {'linestyle': '-', 'marker': 'None', 'linewidth': '0.6'}
    ]
    # Définit les marges du graphique.
    marges = {'left': 0.08, 'right': 0.935, 'top': 0.92, 'bottom': 0.12}

    # Trace le graphique en utilisant la fonction tracer_graphique de l'objet fg.
    fig = fg.tracer_graphique(donnees, Legende, titre,
                              xlabel="Nombre de points d'acquisition",
                              ylabels=["Capteur (s) " + unit, "Capteur ref " + unit_ref],
                              styles=styles,
                              marges=marges)

    # Crée un canvas Tkinter pour afficher le graphique.
    canvas: FigureCanvasTkAgg = FigureCanvasTkAgg(fig, master=zone_graphique)
    # Dessine le graphique sur le canvas.
    canvas.draw()
    # Empaquète le canvas dans la zone graphique pour l'afficher.
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def afficher_graphique1(nomFichier) -> None:
    """Affiche un graphique des données brutes dans la zone graphique 1.

    Cette fonction récupère les données à partir d'un fichier spécifié, puis les affiche
    dans la zone graphique 1 de l'interface utilisateur en utilisant la fonction
    'afficher_graphique'.

    Args:
        nomFichier: Le nom du fichier contenant les données à afficher.
    """
    zone_graphique1 = fg.get_state("zone_graphique1")
    """Récupère la référence de la zone graphique 1 depuis l'état global."""
    donnees = [[0, 1, 2, 3, 4, 7, 6, 7, 8, 9, 10, 11, 12, 5, 14,15],[0, 10, 2, 7, 4, 5, 6, 7, 8, 9, 1, 11, 12, 25, 14,15]]
    """Données de test (sera remplacé par les données du fichier)."""
    donnees = fg.get_data_from_file(nomFichier)
    """Récupère les données à partir du fichier spécifié."""
    afficher_graphique(donnees, zone_graphique1, titre = "Données brutes")
    """Appelle la fonction 'afficher_graphique' pour afficher les données
    dans la zone graphique 1 avec le titre "Données brutes".
    """

def cacher_graphique2() -> None:
    zone_graphique2 = fg.get_state("zone_graphique2")
    zone_graphique2.grid_remove()

def generer_pdf() -> None:
    """
    Lance l'exécution de la génération du PDF après quelques vérifications.
    """
    try:
        # Debug - Afficher le dossier actuel
        dossier = fg.dossier_actuel()
        #print(f"Dossier actuel: '{dossier}'")

        # Vérifier si un fichier est sélectionné
        nom_fichier = fg.nom_fichier_selectionne()
        #print(f"Nom du fichier sélectionné: '{nom_fichier}'")
        if not nom_fichier:
            messagebox.showwarning("Attention", "Veuillez sélectionner un fichier.")
            return

        # Récupérer le trigramme de l'utilisateur
        champ_trigramme = fg.get_state("champ_trigramme")
        # Obtenir la valeur du champ Entry
        nom_utilisateur = champ_trigramme.get() if champ_trigramme else ""


        if not nom_utilisateur:
            messagebox.showwarning("Attention", "Le trigramme utilisateur n'est pas défini.")
            return

        # Vérifier que toutes les valeurs requises sont présentes et valides
        if not dossier:
            messagebox.showwarning("Attention", "Veuillez sélectionner un dossier de travail.")
            return

        # Récupérer les valeurs des champs Entry
        champ_unit_capteurs = fg.get_state("champ_unit_capteurs")
        champ_unit_capteur_ref = fg.get_state("champ_unit_capteur_ref")
        champ_nom_capteur_ref = fg.get_state("champ_nom_capteur_ref")

        # Extraire les valeurs des widgets Entry
        info_unites = (
            champ_unit_capteurs.get() if champ_unit_capteurs else None,
            champ_unit_capteur_ref.get() if champ_unit_capteur_ref else None,
            champ_nom_capteur_ref.get() if champ_nom_capteur_ref else None
        )

        #print(f"Vérification des valeurs extraites : {info_unites}")

        # Récupérer les numéros de colonnes
        numero_col_1 = fg.num_colonne_lire("capteur1")
        numero_col_2 = fg.num_colonne_lire("capteurRef")

        # Appeler traitement_pdf
        pdf.traitement_pdf(
            rundir=dossier,
            nom_fichier=nom_fichier,
            nom_utilisateur=nom_utilisateur,
            colonne1=numero_col_1,
            colonne2=numero_col_2,
            info_unites = info_unites
        )

        messagebox.showinfo("Succès", "PDF généré avec succès!")

    except Exception as e:
        messagebox.showerror("Erreur",
                             f"Une erreur s'est produite lors de la génération du PDF : {str(e)}")
        print(f"Exception lors de la génération du PDF : {e}")
        print(f"Détails de l'erreur : {traceback.format_exc()}")

def valider_unites() -> None:
    champ_unit_capteurs = fg.get_state("champ_unit_capteurs")
    champ_unit_capteur_ref = fg.get_state("champ_unit_capteur_ref")
    champ_nom_capteur_ref = fg.get_state("champ_nom_capteur_ref")

    unit = champ_unit_capteurs.get().strip()
    unit_ref = champ_unit_capteur_ref.get().strip()
    nom_ref = champ_nom_capteur_ref.get().strip()

    if not unit or not unit_ref or not nom_ref:
        messagebox.showerror(
            "Erreur de validation",
            f"Les unités doivent être renseignées.\n"
            f"Unité capteurs : {unit}\nUnité référence : {unit_ref}\nNom référence : {nom_ref}"
        )
        fg.set_state("unites_valides", False)
    else:

        fg.log_message(f"L'unité des capteurs est : {unit}\n", "INFO")
        fg.log_message(f"L'unité du capteur de référence est : {unit_ref}\n", "INFO")
        fg.log_message(f"Le nom du capteur de référence est : {nom_ref}\n", "INFO")
        fg.set_state("unites_valides", True)

    mettre_a_jour_bouton_pdf()

def valider_coefficients() -> None:
    """Valide les coefficients de conversion"""
    champ_coef_a = fg.get_state("champ_coef_a")
    champ_coef_b = fg.get_state("champ_coef_b")

    coef_a = champ_coef_a.get().strip()
    coef_b = champ_coef_b.get().strip()

    try:
        if not coef_a or not coef_b:
            messagebox.showerror(
                "Erreur de validation",
                f"Les coefficients doivent être renseignés.\n"
                f"Coefficient a : {coef_a}\nCoefficient b : {coef_b}"
            )
            fg.set_state("coefficients_valides", False)
        else:
            # Conversion en float pour validation
            float_a = float(coef_a)
            float_b = float(coef_b)

            if float_a == 0:
                messagebox.showerror(
                    "Erreur de validation",
                    "Le coefficient a ne peut pas être nul."
                )
                fg.set_state("coefficients_valides", False)
            else:
                fg.log_message(f"Le coefficient a est : {float_a}\n", "INFO")
                fg.log_message(f"Le coefficient b est : {float_b}\n", "INFO")
                fg.set_state("coefficients_valides", True)

    except ValueError:
        messagebox.showerror(
            "Erreur de validation",
            "Les coefficients doivent être des nombres valides."
        )
        fg.set_state("coefficients_valides", False)

def create_tooltip(widget: tk.Widget, text: str) -> None:
    tooltip = tk.Toplevel(widget)
    tooltip.overrideredirect(True)
    label = tk.Label(tooltip, text=text, justify=tk.LEFT, relief=tk.SOLID, borderwidth=1)
    label.pack(ipadx=1)

    def show_tooltip(event):
        tooltip.deiconify()
        tooltip.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")

    def hide_tooltip():
        tooltip.withdraw()

    widget.bind("<Enter>", show_tooltip)
    widget.bind("<Leave>", lambda event: hide_tooltip())
    widget.bind("<Button-1>", lambda event: hide_tooltip())

def creer_frame_avec_label(parent, label_text, padding="5", borderwidth=0, relief=None):
    """Crée un frame avec un label."""
    frame = ttk.Frame(parent, padding=padding, borderwidth=borderwidth, relief=relief)
    ttk.Label(frame, text=label_text).grid(row=0, column=0, padx=2, pady=2, sticky="W")
    return frame

def creer_entry_avec_tooltip(parent, width, tooltip_text, default_text=""):
    """Crée un Entry avec un Hovertip."""
    entry = ttk.Entry(parent, width=width)
    entry.insert(0, default_text)
    Hovertip(entry, tooltip_text)
    return entry

def configurer_affichage(root: tk.Tk) -> None:
    """
    Configure l'affichage principal de l'application.
    Args:
        root: La fenêtre principale de l'application
    """
    # Configuration initiale des états
    fg.set_state("champ_trigramme", None)
    fg.set_state("zone_texte_info_general", None)
    fg.set_state("liste_fichiers", None)
    fg.set_state("zone_texte_traitement_fichier", None)
    fg.set_state("zone_graphique1", None)
    fg.set_state("zone_graphique2", None)
    fg.set_state("champ_unit_capteurs", None)
    fg.set_state("champ_unit_capteur_ref", None)
    fg.set_state("champ_nom_capteur_ref", None)
    fg.set_state("capteurs_manager", None)
    fg.set_state("bouton_generer_pdf", None)
    fg.set_state("trigramme_valide", False)
    fg.set_state("capteurs_valides", False)
    fg.set_state("unites_valides", False)
    fg.set_state("champ_coef_a", None)
    fg.set_state("champ_coef_b", None)
    fg.set_state("coefficients_valides", False)

    # Configuration des colonnes pour une répartition égale
    root.grid_columnconfigure(0, weight=1, uniform="group1")
    root.grid_columnconfigure(1, weight=1, uniform="group1")
    root.grid_columnconfigure(2, weight=1, uniform="group1")
    root.grid_rowconfigure(0, weight=0)
    root.grid_rowconfigure(1, weight=1)
    root.grid_rowconfigure(2, weight=2)
    root.grid_rowconfigure(3, weight=0)

    # Configuration des largeurs par défaut (en caractères)
    WIDGET_WIDTH = 40  # Largeur par défaut des widgets
    WIDGET_HEIGHT = 10 # Hauteur par défault des widgets

    # Frame pour le trigramme et les capteurs
    frame_trigramme_capteurs = ttk.Frame(root, padding="5")
    frame_trigramme_capteurs.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="NSEW")

    # Frame Trigramme
    frame_trigramme = creer_frame_avec_label(frame_trigramme_capteurs, "Nom (Trigramme) :", borderwidth=2,
                                             relief="groove")
    frame_trigramme.grid(row=0, column=0, padx=2, pady=2, sticky="W")
    champ_trigramme = creer_entry_avec_tooltip(frame_trigramme, 4, 'Entrez votre trigramme de 3 lettres', "Bbu")
    champ_trigramme.grid(row=0, column=1, padx=2, pady=2)
    fg.set_state("champ_trigramme", champ_trigramme)
    ttk.Button(frame_trigramme, text="Valider", command=valider_trigramme).grid(row=0, column=2, padx=2, pady=2)

    # Gestionnaire de capteurs (inchangé)
    capteurs_manager = CapteursManager(frame_trigramme_capteurs)
    capteurs_manager.grid(row=0, column=1, padx=2, pady=2, sticky="W")
    fg.set_state("capteurs_manager", capteurs_manager)

    # Frame Unités
    frame_unites = ttk.Frame(frame_trigramme_capteurs, padding="5")
    frame_unites.grid(row=0, column=2, padx=2, pady=2, sticky="W")

    ttk.Label(frame_unites, text="Unité (Capteur) :").grid(row=0, column=0, padx=2, pady=2)
    champ_unit_capteurs = creer_entry_avec_tooltip(frame_unites, 6, "Entrez l'unités du ou des capteurs passés", "[V]")
    champ_unit_capteurs.grid(row=0, column=1, padx=2, pady=2)
    fg.set_state("champ_unit_capteurs", champ_unit_capteurs)

    ttk.Label(frame_unites, text="Unité (Capteur ref) :").grid(row=1, column=0, padx=2, pady=2)
    champ_unit_capteur_ref = creer_entry_avec_tooltip(frame_unites, 6, "Entrez l'unité de référence", "[m/s]")
    champ_unit_capteur_ref.grid(row=1, column=1, padx=2, pady=2)
    fg.set_state("champ_unit_capteur_ref", champ_unit_capteur_ref)

    ttk.Label(frame_unites, text="Nom (Capteur ref) :").grid(row=2, column=0, padx=2, pady=2)
    champ_nom_capteur_ref = creer_entry_avec_tooltip(frame_unites, 10, "Entrez le nom du capteur de référence", "Venturi")  # Pas de Tooltip
    champ_nom_capteur_ref.grid(row=2, column=1, padx=2, pady=2)
    fg.set_state("champ_nom_capteur_ref", champ_nom_capteur_ref)

    ttk.Button(frame_unites, text="Valider Unités", command=valider_unites).grid(row=3, column=0, columnspan=2, padx=2,
                                                                                 pady=2)
    # Frame convertion capteur ref
    frame_conversion = ttk.Frame(frame_trigramme_capteurs, borderwidth=2, relief="groove", padding=(5, 5))
    frame_conversion.grid(row=0, column=3, columnspan=2, sticky="EW")

    # Ajouter le titre à l'intérieur de la frame
    titre_conversion = ttk.Label(frame_conversion, text="Coefficient de conversion du capteur de référence.")
    titre_conversion.grid(row=0, column=0, columnspan=2, sticky="W", padx=2, pady=(2, 5))  # Padding bas augmenté

    # Configuration des colonnes pour un meilleur contrôle de l'espacement
    frame_conversion.grid_columnconfigure(0, weight=0)  # Colonne des labels ne s'étire pas
    frame_conversion.grid_columnconfigure(1, weight=1)  # Colonne des champs s'étire

    # Configuration des colonnes
    frame_conversion.grid_columnconfigure(0, weight=0)  # Colonne des labels
    frame_conversion.grid_columnconfigure(1, weight=1)  # Colonne des champs

    # Champ pour le coefficient a
    ttk.Label(frame_conversion, text="Coefficient a :").grid(row=1, column=0, padx=(2, 0), pady=1,
                                                             sticky="W")  # sticky W, padx ajusté
    champ_coef_a = creer_entry_avec_tooltip(frame_conversion, 6, "Coefficient a pour la conversion", "1.0")
    champ_coef_a.grid(row=1, column=1, padx=1, pady=1, sticky="W")
    fg.set_state("champ_coef_a", champ_coef_a)

    # Champ pour le coefficient b
    ttk.Label(frame_conversion, text="Coefficient b :").grid(row=2, column=0, padx=(2, 0), pady=1,
                                                             sticky="W")  # sticky W, padx ajusté
    champ_coef_b = creer_entry_avec_tooltip(frame_conversion, 6, "Coefficient b pour la conversion", "0.0")
    champ_coef_b.grid(row=2, column=1, padx=1, pady=1, sticky="W")
    fg.set_state("champ_coef_b", champ_coef_b)

    # Bouton de validation
    ttk.Button(frame_conversion, text="Valider Coefficients", command=valider_coefficients).grid(row=3, column=0,
                                                                                                 columnspan=2, padx=2,
                                                                                                 pady=2, sticky="E")
    # Frame Liste des fichiers
    frame_liste_fichiers = creer_frame_avec_label(root, "Liste des fichiers :", padding="5")
    frame_liste_fichiers.grid(row=1, column=0, padx=5, pady=5, sticky="NSEW")
    frame_liste_fichiers.grid_columnconfigure(0, weight=1)
    frame_liste_fichiers.grid_rowconfigure(1, weight=1)

    # Container frame pour la liste et les scrollbars
    list_container = ttk.Frame(frame_liste_fichiers)
    list_container.grid(row=1, column=0, sticky="NSEW")
    list_container.grid_columnconfigure(0, weight=1)
    list_container.grid_rowconfigure(0, weight=1)

    # Liste avec scrollbars
    liste_fichiers = tk.Listbox(list_container, width=5, height=WIDGET_HEIGHT)
    scrollbar_v = ttk.Scrollbar(list_container, orient="vertical", command=liste_fichiers.yview)
    scrollbar_h = ttk.Scrollbar(list_container, orient="horizontal", command=liste_fichiers.xview)

    liste_fichiers.grid(row=0, column=0, sticky="NSEW")
    scrollbar_v.grid(row=0, column=1, sticky="NS")
    scrollbar_h.grid(row=1, column=0, sticky="EW")

    liste_fichiers.config(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
    fg.set_state("liste_fichiers", liste_fichiers)
    liste_fichiers.bind("<ButtonRelease-1>", on_file_select)

    # Lier l'événement de perte de focus
    liste_fichiers.bind("<FocusOut>", on_listbox_lose_focus)

    # Frame Traitement
    frame_traitement = ttk.Frame(root, padding="5")
    frame_traitement.grid(row=1, column=1, padx=5, pady=5, sticky="NSEW")
    frame_traitement.grid_columnconfigure(0, weight=1)
    frame_traitement.grid_rowconfigure(1, weight=1)

    ttk.Label(frame_traitement, text="Traitement du fichier :").grid(row=0, column=0, padx=2, pady=2, sticky="W")

    # Container frame pour le texte et les scrollbars
    traitement_container = ttk.Frame(frame_traitement)
    traitement_container.grid(row=1, column=0, sticky="NSEW")
    traitement_container.grid_columnconfigure(0, weight=1)
    traitement_container.grid_rowconfigure(0, weight=1)

    # Zone de texte avec scrollbars
    zone_texte_traitement_fichier = tk.Text(traitement_container, width=WIDGET_WIDTH, height=WIDGET_HEIGHT, wrap="none")
    scrollbar_v = ttk.Scrollbar(traitement_container, orient="vertical", command=zone_texte_traitement_fichier.yview)
    scrollbar_h = ttk.Scrollbar(traitement_container, orient="horizontal", command=zone_texte_traitement_fichier.xview)

    zone_texte_traitement_fichier.grid(row=0, column=0, sticky="NSEW")
    scrollbar_v.grid(row=0, column=1, sticky="NS")
    scrollbar_h.grid(row=1, column=0, sticky="EW")

    zone_texte_traitement_fichier.config(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
    fg.set_state("zone_texte_traitement_fichier", zone_texte_traitement_fichier)

    # Frame Info
    frame_info = ttk.Frame(root, padding="5")
    frame_info.grid(row=1, column=2, padx=5, pady=5, sticky="NSEW")
    frame_info.grid_columnconfigure(0, weight=1)
    frame_info.grid_rowconfigure(1, weight=1)

    ttk.Label(frame_info, text="Logs & Informations Générales :").grid(row=0, column=0, padx=2, pady=2, sticky="W")

    # Container frame pour le texte et les scrollbars
    info_container = ttk.Frame(frame_info)
    info_container.grid(row=1, column=0, sticky="NSEW")
    info_container.grid_columnconfigure(0, weight=1)
    info_container.grid_rowconfigure(0, weight=1)

    # Zone de texte avec scrollbars
    zone_texte_info_general = tk.Text(info_container, width=WIDGET_WIDTH, height=WIDGET_HEIGHT, wrap="none")
    scrollbar_v = ttk.Scrollbar(info_container, orient="vertical", command=zone_texte_info_general.yview)
    scrollbar_h = ttk.Scrollbar(info_container, orient="horizontal", command=zone_texte_info_general.xview)

    zone_texte_info_general.grid(row=0, column=0, sticky="NSEW")
    scrollbar_v.grid(row=0, column=1, sticky="NS")
    scrollbar_h.grid(row=1, column=0, sticky="EW")

    zone_texte_info_general.config(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
    fg.set_state("zone_texte_info_general", zone_texte_info_general)

    # Frame Graphiques
    frame_graphiques = ttk.Frame(root, padding="5")
    frame_graphiques.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="NSEW")
    frame_graphiques.grid_columnconfigure(0, weight=1)
    frame_graphiques.grid_columnconfigure(1, weight=1)
    frame_graphiques.grid_rowconfigure(0, weight=1)

    zone_graphique1 = ttk.Frame(frame_graphiques)
    zone_graphique1.grid(row=0, column=0, padx=2, pady=2, sticky="NSEW")
    fg.set_state("zone_graphique1", zone_graphique1)

    zone_graphique2 = ttk.Frame(frame_graphiques)
    zone_graphique2.grid(row=0, column=1, padx=2, pady=2, sticky="NSEW")
    zone_graphique2.grid_remove()
    fg.set_state("zone_graphique2", zone_graphique2)

    # Frame Boutons
    frame_boutons = ttk.Frame(root, padding="5")
    frame_boutons.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="E")

    # Créer l'instance du gestionnaire de fenêtre DB
    gestionnaire_db = GestionnaireFenetreDB()

    bouton_generer_pdf = ttk.Button(frame_boutons, text="Générer PDF", command=generer_pdf, state=tk.DISABLED)
    bouton_generer_pdf.pack(side=tk.LEFT, padx=5)
    fg.set_state("bouton_generer_pdf", bouton_generer_pdf)

    # Ajouter le bouton Base de données
    ttk.Button(frame_boutons, text="Base de données",
               command=lambda: gestionnaire_db.ouvrir_fenetre_db(root)).pack(side=tk.LEFT, padx=5)

    ttk.Button(frame_boutons, text="Quitter", command=root.quit).pack(side=tk.LEFT, padx=5)

    # Tooltip pour le bouton PDF
    create_tooltip(bouton_generer_pdf, "Pour pouvoir générer le PDF, il faut :\n"
                                       "   Valider le trigramme.\n"
                                       "   Valider le ou les capteurs.\n"
                                       "   Valider les unités.\n")

    # Initialiser l'affichage de la liste des fichiers
    fg.afficher_liste_fichiers("./")


def mainGui(title="Version Direct", width=500, height=400):
    root = tk.Tk()
    root.title(title)
    root.minsize(width, height)
    configurer_affichage(root)
    fg.log_message("Application démarrée avec succès", "INFO")
    root.mainloop()

if __name__ == "__main__":
    mainGui()

