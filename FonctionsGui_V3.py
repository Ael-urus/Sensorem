#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Thus Aug 04  2024

@author: Aelurus

"""
import glob
# FonctionGui_V3.py.py
import os
import os.path
import sys
import tkinter as tk
import tkinter.ttk as ttk
from datetime import datetime
from doctest import testmod
from itertools import zip_longest
from tkinter import messagebox

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

try:
    # import de mes fonctions
    import FonctionsSignal as fs
    import FonctionsPdf as pdf
    import FonctionsCSV as fc
    import FonctionsDB  as fdb # Importez FonctionsDB

except Exception as e:
    print(f"Une exception s'est produite dans le module {__name__}: {e}")
    print(f"Fichier en cours d'exécution : {os.path.basename(__file__)}")
    input('Appuyez sur Entrée pour continuer...')
    sys.exit(1)

# Constants
# Définir une variable globale pour stocker le dossier
_DOSSIER_ACTUEL = "./"



#  Dictionnaire qui stocke les variables globales encapsulées
_state = {
    "champ_trigramme": None,
    "zone_texte_info_general": None,
    "liste_fichiers": None,
    "zone_texte_traitement_fichier": None,
    "zone_graphique1": None,
    "zone_graphique2": None,
    "champ_unit_capteurs": None,
    "champ_unit_capteur_ref": None,
    "champ_nom_capteur_ref": None,
    "bouton_generer_pdf": None,
    "capteurs_manager": None,
    "trigramme_valide": False,
    "capteurs_valides": False,
    "unites_valides": False
}

# Variables globales pour les états

def update_file_list(): #Cette fonction doit rester dans FonctionsGui_V3
    """Met à jour la liste des fichiers."""
    liste_fichiers = get_state("liste_fichiers")
    if liste_fichiers:
        liste_fichiers.delete(0, tk.END)
        try:
            for filename in os.listdir("."):
                liste_fichiers.insert(tk.END, filename)
        except FileNotFoundError:
            print("Répertoire non trouvé.")
        except PermissionError:
            print("Permission refusée pour accéder au répertoire.")
        except Exception as e:
            print(f"Une erreur s'est produite : {e}")
    else:
        print("Erreur : liste_fichiers non initialisée.")

def dossier_actuel(new_folder=None):
    """
    Getter/Setter pour le dossier actuel.

    Cette fonction permet de récupérer ou de définir le dossier actuel.
    Si un nouveau dossier est fourni, il est défini comme le dossier actuel.
    Sinon, la fonction retourne le dossier actuel.

    Args:
        new_folder (str, optional): Si fourni, définit le nouveau dossier actuel. Defaults to None.

    Returns:
        str: Le dossier actuel.

    Raises:
        ValueError: Si le nouveau dossier est vide ou None.
    """
    global _DOSSIER_ACTUEL
    if new_folder is not None:
        if not new_folder:
            raise ValueError("Le nouveau dossier ne peut pas être vide")
        _DOSSIER_ACTUEL = new_folder
    return _DOSSIER_ACTUEL
# Fonctions pour accéder et modifier les variables globales
def get_state(key: str) -> any:
    """
    Récupérer la valeur d'une variable globale.

    Cette fonction permet de récupérer la valeur d'une variable globale stockée dans le dictionnaire `_state`.
    Les variables globales sont utilisées pour partager des données entre différentes parties de l'application.

    Args:
        key (str): La clé de la variable globale. Cette clé doit être unique pour éviter les conflits.

    Returns:
        any: La valeur de la variable globale. Cette valeur peut être de n'importe quel type.

    Raises:
        KeyError: Si la clé n'existe pas dans le dictionnaire des variables globales.

    Notes:
        Il est important de noter que les variables globales doivent être utilisées avec précaution, car elles peuvent créer des dépendances entre les différentes parties de l'application.
    """
    # Récupérer la valeur de la variable globale dans le dictionnaire _state
    # Si la clé n'existe pas, une KeyError est levée
    return _state[key]

def set_state(key: str, value: any) -> None:
    """
    Définir la valeur d'une variable globale.

    Cette fonction permet de définir la valeur d'une variable globale stockée dans le dictionnaire `_state`.
    Les variables globales sont utilisées pour partager des données entre différentes parties de l'application.

    Args:
        key (str): La clé de la variable globale. Cette clé doit être unique pour éviter les conflits.
        value (any): La nouvelle valeur de la variable globale. Cette valeur peut être de n'importe quel type.

    Notes:
        Il est important de noter que les variables globales doivent être utilisées avec précaution, car elles peuvent créer des dépendances entre les différentes parties de l'application.
    """
    # Définir la valeur de la variable globale dans le dictionnaire _state
    # Si la clé n'existe pas, elle est créée
    _state[key] = value

def num_colonne_lire(Capteur: str) -> int:
    """
    Récupère le numéro de colonne pour lire les données d'un capteur.

    Cette fonction retourne le numéro de colonne à partir duquel les données d'un capteur spécifique doivent être lues.
    Les numéros de colonne sont stockés dans un dictionnaire qui mappe les noms de capteurs à leurs numéros de colonne respectifs.

    Args:
        Capteur (str): Le nom du capteur.

    Returns:
        int: Le numéro de colonne pour lire les données du capteur.

    Raises:
        ValueError: Si le capteur n'est pas trouvé dans la liste des capteurs.
    """
    # Dictionnaire qui mappe les noms de capteurs à leurs numéros de colonne respectifs
    Capteurs = {
        "capteur1": 2,
        "capteurRef": 10
    }
    try:
        # Retourne le numéro de colonne pour le capteur spécifié
        return Capteurs[Capteur]
    except KeyError:
        # Si le capteur n'est pas trouvé, une ValueError est levée
        raise ValueError(f"Capteur '{Capteur}' non trouvé dans la liste des capteurs")

def num_ligne_lire(FirstLigne: int = 24) -> int:
    """
    Récupère le numéro de ligne pour lire les données.

    Cette fonction retourne le numéro de ligne à partir duquel les données doivent être lues.
    Le numéro de ligne par défaut est de 24.

    Args:
        FirstLigne (int, optional): Le numéro de ligne pour lire les données. Par défaut, 24.

    Returns:
        int: Le numéro de ligne pour lire les données.
    """
    # Retourne le numéro de ligne pour lire les données
    return FirstLigne

def get_data_from_file(fichier: str) -> tuple:
    """
    Récupère les données à partir d'un fichier.

    Cette fonction lit les données à partir d'un fichier spécifié et retourne un tuple contenant les données lues.
    Les données sont lues à partir de deux colonnes spécifiques du fichier, correspondant aux capteurs 1 et 2.

    Args:
        fichier (str): Le chemin du fichier à lire.

    Returns:
        tuple: Un tuple contenant les données lues à partir du fichier, sous la forme [y, y2]
               où y et y2 sont les données des capteurs 1 et 2, respectivement.
               Si une erreur se produit lors de l'ouverture du fichier, la fonction retourne None.

    Raises:
        messagebox.showerror: Si une erreur se produit lors de l'ouverture du fichier.
    """
    # Vérifie si le fichier existe
    if os.path.isfile(fichier):
        try:
            # Ouvre le fichier en mode lecture
            with open(fichier, 'r') as file_in:
                # Lit les données des capteurs 1 et 2 à partir du fichier
                y = fc.read_col_csv(fichier, ";", num_colonne_lire("capteur1"))
                y2 = fc.read_col_csv(fichier, ";", num_colonne_lire("capteurRef"))
                # Crée un tuple contenant les données lues
                datas = [y, y2]
                #liste_valeurs = list(zip_longest(y, y2))  # Cette ligne est commentée, mais pourrait être utilisée pour combiner les données des deux capteurs
        except Exception as e:
            # Affiche un message d'erreur si une exception se produit lors de l'ouverture du fichier
            messagebox.showerror("Erreur d'ouverture du fichier", f"Erreur : {e}")
            # Retourne None si une erreur se produit
            return None

    # Retourne les données lues à partir du fichier
    return datas

def normaliser(chemin, *args):
    """
    Normalise un chemin de fichier pour le rendre compatible avec l'OS utilisé.

    Cette fonction prend en entrée un chemin de base et des arguments supplémentaires,
    puis les combine en un chemin complet en utilisant les séparateurs de chemins appropriés
    pour l'OS utilisé. Elle normalise également le chemin en supprimant les répertoires
    parent (`..`) et courant (`.`) inutiles.

    Args:
        chemin (str): Le chemin de base du fichier.
        *args (str): Les composants supplémentaires du chemin.

    Returns:
        str: Le chemin de fichier normalisé.
    """
    # Utilise os.path.join pour combiner les chemins en utilisant les séparateurs appropriés
    # pour l'OS utilisé, puis os.path.normpath pour normaliser le chemin
    return os.path.normpath(os.path.join(chemin, *args))

def rafraichir_liste_fichiers() -> None:
    """
    Rafraîchit la liste des fichiers CSV dans le dossier actuel.
    """
    dossier = dossier_actuel()  # Récupérer le dossier actuel
    afficher_liste_fichiers(dossier)  # Met à jour la liste

def initialiser_selection_listbox() -> None:
    """
    Initialise une sélection par défaut dans la `Listbox` si elle contient des éléments.
    """
    liste_fichiers = get_liste_fichiers()
    if liste_fichiers.size() > 0:
        liste_fichiers.selection_set(0)  # Sélectionne le premier fichier par défaut
        liste_fichiers.see(0)  # Fait défiler pour afficher le fichier sélectionné

def afficher_liste_fichiers(dossier: str) -> None:
    """
    Affiche la liste des fichiers CSV dans le dossier spécifié.

    Cette fonction nettoie la liste des fichiers existante,
    puis insère les noms des fichiers CSV trouvés dans le dossier spécifié.

    Args:
        dossier (str): Le chemin du dossier où rechercher les fichiers CSV.

    Returns:
        None
    """
    # Récupère la liste des fichiers
    liste_fichiers = get_liste_fichiers()

    # Nettoie la liste des fichiers existante
    liste_fichiers.delete(0, tk.END)

    # Recherche les fichiers CSV dans le dossier spécifié
    for fichier in glob.glob(os.path.join(dossier, "*.CSV")):
        # Insère le nom du fichier dans la liste des fichiers
        # en utilisant le nom de base du fichier (sans le chemin)
        liste_fichiers.insert(tk.END, os.path.basename(fichier))

def nom_fichier_selectionne():
    """
    Récupère le nom du fichier sélectionné dans la liste des fichiers.

    Cette fonction vérifie si un fichier est sélectionné dans la liste,
    et si oui, elle retourne le nom du fichier sélectionné.
    Si aucun fichier n'est sélectionné, elle affiche un message d'avertissement
    et retourne None.

    Returns:
        str: Le nom du fichier sélectionné, ou None si aucun fichier n'est sélectionné.
    """
    # Récupère la liste des fichiers
    liste_fichiers = get_liste_fichiers()

    # Vérifie si un fichier est sélectionné
    selection = liste_fichiers.curselection()

    # Vérifie si rien n'est sélectionné
    if not selection:
        # Affiche un message d'avertissement si aucun fichier n'est sélectionné
        messagebox.showwarning("Aucune sélection", "Veuillez sélectionner un fichier dans la liste.")
        # Retourne None si aucune sélection n'est faite
        return None

    # Utilise la première sélection (si plusieurs fichiers sont sélectionnés)
    nom_fichier_selectionne = liste_fichiers.get(selection[0])

    # Retourne le nom du fichier sélectionné
    return nom_fichier_selectionne

def get_liste_fichiers() -> tk.Listbox:
    """
    Récupère la liste des fichiers stockée dans l'état.

    Cette fonction récupère la liste des fichiers qui est stockée dans l'état de l'application.
    La liste des fichiers est un widget Tkinter de type Listbox qui permet d'afficher et de sélectionner des fichiers.

    Returns:
        tk.Listbox: La liste des fichiers.
    """
    # Récupère la liste des fichiers stockée dans l'état
    return get_state("liste_fichiers")

def traitement_fichier():
    """
    Lecture et affichage des données du fichier sélectionné sans graphiques.

    Cette fonction lit les données des capteurs dans le fichier sélectionné,
    effectue un traitement sur ces données et retourne les résultats sous forme de chaîne de caractères.

    Args:


    Returns:
        str: Le traitement complet des données du fichier sous forme de chaîne de caractères.
    """
    ligne_debut_affichage = 21  # Ligne à partir de laquelle commencer l'affichage
    fichier = normaliser(dossier_actuel(), nom_fichier_selectionne())
    #print(f"Debug nom de fichier: {fichier}")

    try:
        # Lecture des données des deux capteurs
        y = fc.read_col_csv(fichier, ";", num_colonne_lire("capteur1"))
        y2 = fc.read_col_csv(fichier, ";", num_colonne_lire("capteurRef"))

        # Débogage détaillé
        #print("Contenu initial de y:")
        #print(y[:30])
        #print("\nContenu initial de y2:")
        #print(y2[:30])

        # Traitement des données pour chaque capteur
        values_capteurs = fs.isol_capteurs(fs.insert_nomscapteurs_gui(y, 0))
        values_capteurs2 = fs.isol_capteurs(fs.insert_nomscapteurs_gui(y2, 1))

        # Débogage des capteurs
        #print("\nCapteurs trouvés:")
        #print("Capteur 1:", list(values_capteurs.keys()))
        #print("Capteur 2:", list(values_capteurs2.keys()))
        for capteur in values_capteurs:
            pass
            #print(f"Longueur des données pour {capteur}: {len(values_capteurs[capteur])}")
        for capteur in values_capteurs2:
            pass
            #print(f"Longueur des données pour {capteur}: {len(values_capteurs2[capteur])}")

        # Traiter les données
        for ligne in fichier:
            # Vérifier si la ligne est vide
            if ligne.strip() == '':
                continue

            # Essayer de diviser la ligne en éléments
            elements = ligne.split(',')

            # Vérifier si les éléments sont valides
            if len(elements) > 0:
                # Essayer de convertir le premier élément en un nombre
                try:
                    element = float(elements[0].strip())
                    # Traiter l'élément
                    #print("Élément : ", element)
                except ValueError:
                    #print("Erreur de lecture de données : l'élément n'est pas un nombre")
                    pass
            else:
                print("Erreur de lecture de données : la ligne est vide")

    except Exception as e:
        #print("Erreur de lecture de données : ", str(e))
        pass

    try:
        # Lecture des données des deux capteurs
        y = fc.read_col_csv(fichier, ";", num_colonne_lire("capteur1"))
        y2 = fc.read_col_csv(fichier, ";", num_colonne_lire("capteurRef"))

        # Créer une liste combinée des valeurs pour affichage
        liste_valeurs = list(zip_longest(y, y2))
        valeurs_affichage = [
            f"{element[0]}\t\t{element[1]}" for i, element in enumerate(liste_valeurs) if i > ligne_debut_affichage
        ]

        # Traitement des données pour chaque capteur
        values_capteurs = fs.isol_capteurs(fs.insert_nomscapteurs_gui(y, 0))
        values_capteurs2 = fs.isol_capteurs(fs.insert_nomscapteurs_gui(y2, 1))

        # Initialisation des listes pour stocker les données traitées
        datat1 = ["--------------------------\nNom capteur\n[N° palier] \tStabilité \tMoyenne [V] \tÉcart-type [mV]"]
        datat2 = ["--------------------------\nNom capteur_ref\n[N° palier] \tStabilité \tMoyenne [V] \tÉcart-type [mV]"]

        # Traitement des données pour chaque capteur
        for capteur, capteur2 in zip(values_capteurs.keys(), values_capteurs2.keys()):
            # Traitement du signal pour chaque capteur
            values_sep_paliers, data, values_sep, paliers_find, paliers_info1 = fs.traitement_signal(
                values_capteurs[capteur], fs.seuil_capteur1()
            )
            values_sep_paliers2, data2, values_sep2, paliers_find2, paliers_info2 = fs.traitement_signal(
                values_capteurs2[capteur2], fs.seuil_capteur2()
            )

            # Récupération de la zone de texte pour les logs
            zone_texte_info_general = get_state("zone_texte_info_general")
            log_manager = LogManager(zone_texte_info_general)
            fs.setup_log_display(zone_texte_info_general)

            # Analyse et vérification des paliers
            log_message(f"Analyse des paliers pour {capteur} et {capteur2}", "INFO")
            comparison_message = fs.compare_paliers(
                capteur, capteur2,
                paliers_info1, paliers_info2,
                values_sep_paliers, values_sep_paliers2,
                log_manager
            )
            # Vérifier si comparison_message n'est pas vide avant d'appeler log_message
            if comparison_message:
                log_message(comparison_message, "WARNING")

            # Vérification de la cohérence des paliers avant traitement
            if paliers_find!= paliers_find2:
                log_message(
                    f"Différence dans le nombre de paliers: {capteur}={paliers_find}, {capteur2}={paliers_find2}",
                    "WARNING")

            # Appel à la fonction de traitement pour obtenir les données traitées
            donneestraitees = fs.traitement_general_donnees(
                paliers_find, paliers_find2,
                values_sep_paliers, values_sep_paliers2,
                datat1,
                capteur1_info=paliers_info1,
                capteur2_info=paliers_info2,
                capteur1_name=capteur,
                capteur2_name=capteur2
            )

            # Formatage des données traitées
            datat1.append(f"\n----------\n{capteur}\n")
            datat2.append(f"\n----------\n{capteur2}\n")
            for i, d in enumerate(donneestraitees):
                datat1.append(f"[{i}]\t{d[0]}\t{d[1]}\t{d[2]}\n")
                datat2.append(f"[{i}]\t{d[3]}\t{d[4]}\t{d[5]}\n")

        # Récapitulatif du traitement
        traitement = f"{len(values_capteurs.keys())} capteur(s) trouvé(s) à raccorder!\n"
        traitement_capteur1 = "\n Capteur 1, à raccorder\n" + ''.join(datat1)
        traitement_capteur2 = "\n Capteur 2, référence\n" + ''.join(datat2)

        # Vérification du nombre de capteurs
        if len(values_capteurs)!= len(values_capteurs2):
            log_message("Nombre de capteurs incohérent.", "ERROR")
        else:
            log_message("Nombre de capteurs correct", "INFO")

        resultat = f"Voici le traitement du fichier : {fichier}\n"

        # Retourne le traitement complet pour affichage
        return resultat + traitement + traitement_capteur1 + traitement_capteur2

    except Exception as e:
        erreur = f"Erreur lors du traitement du fichier : {str(e)}"
        print(erreur)
        return erreur

class LogManager:
    """
    Gestionnaire de logs amélioré pour le traitement des signaux.
    """

    LEVELS = {
        'DEBUG': 0,
        'INFO': 1,
        'WARNING': 2,
        'ERROR': 3,
        'CRITICAL': 4
    }

    def __init__(self, zone_texte_info_general):
        self.zone_texte = zone_texte_info_general
        self.messages = []
        self.current_context = None

    def start_context(self, context_name):
        """Démarre un nouveau contexte de logging."""
        self.current_context = context_name
        self._log(f"=== Début {context_name} ===", 'INFO')

    def end_context(self):
        """Termine le contexte actuel."""
        if self.current_context:
            self._log(f"=== Fin {self.current_context} ===", 'INFO')
        self.current_context = None

    def _log(self, message, level):
        """Méthode interne pour enregistrer un message."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        context_prefix = f"[{self.current_context}] " if self.current_context else ""
        formatted_message = f"{timestamp} [{level}] {context_prefix}{message}\n"

        if self.zone_texte:
            # Coloration selon le niveau
            tag = f"log_{level.lower()}"
            self.zone_texte.insert(tk.END, formatted_message, tag)
            self.zone_texte.see(tk.END)
        else:
            print(formatted_message)

        self.messages.append((timestamp, level, self.current_context, message))

    def debug(self, message):
        self._log(message, 'DEBUG')

    def info(self, message):
        self._log(message, 'INFO')

    def error(self, message):
        self._log(message, 'ERROR')

    def critical(self, message):
        self._log(message, 'CRITICAL')

    def get_summary(self):
        """Génère un résumé des logs."""
        summary = {level: 0 for level in self.LEVELS}
        for _, level, _, _ in self.messages:
            summary[level] += 1
        return summary

    def warning(self, message):
        if not message:
            print("WARNING : Message vide détecté")
        self._log(message if message else "Message vide ou absent", "WARNING")

def tracer_graphique(
        donnees: list,
        Legende: list,
        titre: str = "",
        xlabel: str = "",
        ylabels: list = None,
        styles: list = None,
        marges: dict = None
) -> Figure:
    """
    Trace un graphique avec les données fournies.

    Cette fonction permet de tracer un graphique avec les données fournies, en utilisant les légendes et les options de personnalisation fournies.

    Parameters:
    ----------
    donnees : list
        Liste de listes de données à tracer.
    Legende : list
        Liste de légendes pour les données.
    titre : str, optional
        Titre du graphique. Par défaut "".
    xlabel : str, optional
        Étiquette de l'axe x. Par défaut "".
    ylabels : list, optional
        Liste d'étiquettes pour les axes y. Par défaut None.
    styles : list, optional
        Liste de dictionnaires de style pour chaque ligne. Par défaut None.
    marges : dict, optional
        Dictionnaire de configuration des marges. Par défaut None.

    Returns:
    -------
    Figure
        La figure du graphique.

    Raises:
    ------
    ValueError
        Si le nombre de listes de données et de légendes ne correspond pas.

    Example:
    -------
    >>> donnees = [np.array([1, 2, 3]), np.array([4, 5, 6])]
    >>> fig = tracer_graphique(donnees, ['Donnée 1', 'Donnée 2'],
   ...                        titre="Mon graphique", xlabel="X", ylabels=["Y1", "Y2"],
   ...                        styles=[{'linestyle': '--'}, {'marker': 'o'}])
    >>> isinstance(fig, Figure)
    True
    """

    # Vérification si le nombre de listes de données et de légendes est identique
    if len(donnees) != len(Legende):
        raise ValueError("Le nombre de listes de données et de légendes doit être identique.")

    # Création d'une figure et d'un axe
    fig, ax1 = plt.subplots(figsize=(4.5, 4), dpi=100)

    # Sélection de couleurs pour les données
    colors = plt.cm.rainbow(np.linspace(0, 1, len(donnees)))

    # Création d'un deuxième axe pour les données
    ax2 = ax1.twinx()

    # Boucle sur les données
    for i, data in enumerate(donnees):
        # Vérification si les données sont non vides
        if data:
            try:
                # Conversion des données en array numpy
                data = np.array(fc.supp_txt(data))
            except Exception as e:
                # Gestion des erreurs de conversion
                print(f"Erreur lors du traitement des données {i + 1}: {e}")
                continue

            # Sélection du style pour les données
            style = styles[i] if styles and i < len(styles) else {}

            # Tracé des données
            if i == 0:
                # Tracé des données sur l'axe 1
                ax1.plot(data, color=colors[i], label=Legende[i], **style)
            else:
                # Tracé des données sur l'axe 2
                ax2.plot(data, color=colors[i], label=Legende[i], **style)
        else:
            # Tracé d'un point pour les données vides
            if i == 0:
                ax1.plot([0], [0], marker='o', color=colors[i], label=Legende[i])
            else:
                ax2.plot([0], [0], marker='o', color=colors[i], label=Legende[i])

    # Configuration du titre et des étiquettes
    ax1.set_title(titre)
    ax1.set_xlabel(xlabel)
    if ylabels and len(ylabels) > 0:
        ax1.set_ylabel(ylabels[0])
    if ylabels and len(ylabels) > 1:
        ax2.set_ylabel(ylabels[1])

    # Configuration de la légende
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='best')

    # Configuration des marges
    if marges:
        plt.subplots_adjust(**marges)
    else:
        fig.tight_layout()

    # Retour de la figure
    return fig


# import traceback

def log_message(message: str, level: str = "INFO") -> None:
    """
    Enregistre un message de log dans la zone de texte dédiée.

    Cette fonction permet d'enregistrer un message de log dans la zone de texte dédiée, avec un niveau de log spécifique.
    Le niveau de log peut être INFO, WARNING, ERROR, etc.

    Args:
        message (str): Le message à enregistrer.
        level (str, optional): Le niveau de log. Par défaut "INFO".

    Raises:
        ValueError: Si la zone de texte pour les logs n'a pas été initialisée.

    Notes:
        La zone de texte pour les logs est obtenue à l'aide de la fonction get_state.
        Le message est inséré dans la zone de texte avec un tag spécifique pour le niveau de log.
        La zone de texte est défilée jusqu'à la fin pour que le message soit visible.
    """

    # Récupération de la zone de texte pour les logs
    zone_texte_info_general = get_state("zone_texte_info_general")

    # Vérification si la zone de texte a été initialisée
    if zone_texte_info_general:
        # Définition du tag pour le niveau de log
        tag = f"log_{level.lower()}"

        # Insertion du message dans la zone de texte avec le tag
        zone_texte_info_general.insert(tk.END, f"[{level}] {message}\n", tag)

        # Défilement de la zone de texte jusqu'à la fin pour que le message soit visible
        zone_texte_info_general.see(tk.END)

        # Forcer le rafraîchissement de l'interface (commenté pour l'instant)
        # root.update()
    else:
        # Levage d'une exception si la zone de texte n'a pas été initialisée
        raise ValueError("La zone de texte pour les logs n'a pas été initialisée")


if __name__ == "__main__":
    testmod()

