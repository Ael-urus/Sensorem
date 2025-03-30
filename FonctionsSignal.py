# -*- coding: utf-8 -*-
# FonctionSignal.py
"""
Fonctions de traitement du signal.

Created on Wed Apr 15 11:10:34 2020
@author: Aelurus
@contributor: Bruno
"""
import os
import sys
import inspect
from doctest import testmod
from typing import List, Tuple, Union, Dict

from numpy import arange, polyfit, array

try:
    import FonctionsCSV as fc
    import FonctionsGui_V3 as fg

except Exception as e:
    print(f"Une exception s'est produite dans le module {__name__}: {e}")
    print(f"Fichier en cours d'exécution : {os.path.basename(__file__)}")
    input('Appuyez sur Entrée pour continuer...')
    sys.exit(1)


def version() -> str:
    """
    Retourne le numéro de version actuel de l'application.

    Cette fonction retourne une chaîne de caractères représentant le numéro de version actuel de l'application.
    Le numéro de version est au format "x.x.x.x" où chaque "x" représente un numéro de version.

    Args:
        --
        Aucun argument n'est requis pour cette fonction.

    Returns:
        str: Le numéro de version actuel de l'application (e.g. "0.4.3.8 Bêta")

    Examples:
        >>> version()
        '0.4.3.8 Bêta'
    """
    # Le numéro de version est actuellement fixé à "0.4.3.5 Bêta"
    # Il sera mis à jour à mesure que de nouvelles versions de l'application sont publiées
    return str("0.4.3.8 Bêta")

def pas_moyenne_mobile() -> int:
    """
    Retourne le nombre de pas utilisés pour calculer la moyenne mobile.

    Cette fonction retourne un entier représentant le nombre de pas utilisés pour calculer la moyenne mobile.
    La moyenne mobile est une technique de calcul qui consiste à prendre en compte un certain nombre de valeurs précédentes
    pour calculer la moyenne actuelle.

    Args:
        --
        Aucun argument n'est requis pour cette fonction.

    Returns:
        int: Le nombre de pas utilisés pour calculer la moyenne mobile.

    Raises:
        --
        Aucune exception n'est levée par cette fonction.

    Examples:
        >>> pas_moyenne_mobile()
        2

    Notes:
        L'option de configuration pour définir le nombre de pas utilisées pour la moyenne mobile sera implémentée ultérieurement.
        Dans cet instant, elle est simplement fixée à 2 pour les tests.
        La valeur de 2 signifie que la moyenne mobile sera calculée en prenant en compte les 2 valeurs précédentes.
    """
    # Le nombre de pas est actuellement fixé à 2
    # Il sera mis à jour à mesure que de nouvelles fonctionnalités sont ajoutées à l'application
    return 2

# Fonction qui prépare les données pour le graphique
def prep_donnees_graph(donnees: List[float]) -> List[List[Union[int, float]]]:
    """
    Prépare les données pour le graphique en les convertissant en une liste d'éléments incrémentée.

    Cette fonction prend en entrée une liste de données et retourne une liste de listes,
    où chaque liste contient l'indice de la donnée et la valeur de la donnée.

    Parameters:
    ----------
    donnees : List[float]
        Liste de données à traiter, contenant les valeurs à incrémenter.

    Returns:
    ----------
    List[List[int, float]]
        Liste d'éléments incrémentée, où chaque élément est une liste [indice, valeur].

    Examples:
    ----------
    >>> prep_donnees_graph([1, 2, 3, 4, 5])
    [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]]

    Notes:
    -----
    Cette fonction utilise la fonction `enumerate` pour obtenir l'indice et la valeur de chaque élément de la liste.
    La fonction `enumerate` retourne un objet `enumerate` qui produit des tuples contenant l'indice et la valeur de chaque élément.
    La liste en compréhension est utilisée pour convertir l'objet `enumerate` en une liste de listes.
    """

    # Utilisation de la fonction `enumerate` pour obtenir l'indice et la valeur de chaque élément de la liste
    # La liste en compréhension est utilisée pour convertir l'objet `enumerate` en une liste de listes
    return [[indice, valeur] for indice, valeur in enumerate(donnees)]

# Fonction pour générer des noms de paliers
def gen_nom_paliers(n: int) -> Tuple[int,...]:
    """
    Génère une séquence incrémentée ascendante et descendante axée sur le milieu du nombre passé en argument.

    Cette fonction prend en entrée un nombre entier `n` qui définit la longueur de la séquence à générer.
    La séquence est composée de deux parties : une partie ascendante qui va de 0 à `n/2` et une partie descendante qui va de `n/2 - 1` à 0.

    Parameters:
    ----------
    n (int): Nombre de paliers à générer, qui définit la longueur de la séquence.

    Returns:
    ----------
    Tuple[int,...]: Séquence incrémentée ascendante et descendante.

    Examples:
    ----------
    >>> print(gen_nom_paliers(9))
    (0, 1, 2, 3, 4, 3, 2, 1, 0)

    Notes:
    -----
    La fonction utilise la fonction `range` pour générer les parties ascendante et descendante de la séquence.
    La partie ascendante est générée avec `range(moitie + 1)` qui va de 0 à `n/2`.
    La partie descendante est générée avec `range(moitie - 1, -1, -1)` qui va de `n/2 - 1` à 0.
    Les deux parties sont ensuite concaténées pour former la séquence complète.
    """

    # Calcul du milieu de la séquence
    moitie = int(n / 2)

    # Génération de la partie ascendante de la séquence
    liste_ascendante = tuple(range(moitie + 1))

    # Génération de la partie descendante de la séquence
    liste_descendante = tuple(range(moitie - 1, -1, -1))

    # Concaténation des deux parties pour former la séquence complète
    liste_complete = liste_ascendante + liste_descendante

    # Retour de la séquence complète
    return liste_complete

# Fonction qui définit la valeur pour marquer la séparation des paliers
def paliers_mark() -> float:
    """
    Définit la valeur pour marquer la séparation des paliers.

    Cette fonction retourne une valeur flottante qui représente la séparation entre les paliers.
    Cette valeur est utilisée pour distinguer visuellement les différents paliers.

    Returns:
    ----------
    float
        Valeur de séparation des paliers (-0.03).

    Notes:
    -----
    La valeur de séparation est actuellement fixée à -0.03.
    Cette valeur peut être ajustée pour modifier l'apparence des paliers.
    """

    # Valeur de séparation des paliers
    # Cette valeur est utilisée pour créer un espace entre les paliers
    return -0.03

# Fonction principale pour le traitement du signal
def traitement_signal(data0, seuil_capt):
    """
    Traite et analyse les données du capteur pour identifier les paliers.

    Cette fonction prend en entrée les données brutes du capteur et les valeurs de seuil et de sensibilité pour l'identification des paliers.
    Elle retourne une liste de valeurs contenant les informations sur les paliers trouvés, les données brutes du capteur traitées, les valeurs de séparation des paliers et le nombre de paliers trouvés.

    Parameters:
    ----------
    data0 : list
        Données brutes du capteur à traiter.
    seuil_capt : tuple
        Valeurs de seuil et de sensibilité pour l'identification des paliers.

    Returns:
    ----------
    tuple
        values_sep_paliers : list
            Liste des valeurs des paliers.
        data : list
            Données brutes du capteur traitées.
        values_sep : list
            Liste des valeurs de séparation des paliers.
        paliers_find : int
            Nombre de paliers trouvés.
        paliers_info : list
            Informations supplémentaires sur les paliers trouvés.

    Examples:
    ----------
    >>> traitement_signal([0.0154, 0.0154, 0.0154, 0.0, 0.0154, 0.0], (0.052, 0.014))
    ([[0.0154, 0.0154, 0.012320000000000001, 0.009240000000000002, 0.0077]], [0.0154, 0.0154, 0.0154, 0.0, 0.0154, 0.0], [0.0154, 0.0154, 0.012320000000000001, 0.009240000000000002, 0.0077], 1, [1, [5], 5, [0.0154, 0.0154, 0.012320000000000001, 0.009240000000000002, 0.0077], [(0, 4)]])

    Notes:
    -----
    La fonction utilise plusieurs étapes pour traiter les données du capteur :
    1. Épuration des valeurs non entières des données brutes du capteur.
    2. Calcul des valeurs de séparation des paliers.
    3. Recherche des paliers dans les données.
    4. Création des paliers à partir des informations trouvées.
    5. Calcul des valeurs des paliers.

    Raises:
    ------
    ValueError
        Si les données brutes sont invalides ou vides.
    """

    # Épuration des valeurs non entières des données brutes du capteur
    data = fc.supp_txt(data0)

    # Vérification si les données brutes sont valides et non vides
    if not data or not isinstance(data, list):
        raise ValueError("Les données brutes sont invalides ou vides.")

    # Calcul des valeurs de séparation des paliers
    values_sep = sep_values(data, seuil_capt)

    # Recherche des paliers dans les données
    paliers_info = info_values(values_sep)

    # Extraction des informations sur les paliers trouvés
    paliers_find, plage_len_find, nb_values, values_sep, paliers_position = paliers_info

    # Création des paliers à partir des informations trouvées
    paliers = make_paliers(paliers_find, plage_len_find)

    # Calcul des valeurs des paliers
    values_sep_paliers = paliers_values_sep(values_sep, nb_values, paliers)

    # Retour des informations sur les paliers trouvés
    resultat = (values_sep_paliers, data, values_sep, paliers_find, paliers_info)
    return resultat

# Fonction qui retourne les valeurs de seuil pour le capteur 1
def seuil_capteur1() -> Tuple[float, float]:
    """
    Retourne des valeurs (seuil, sensibilité) pour les hélices de type 20 et 40 m/s.

    Cette fonction retourne un tuple de deux valeurs flottantes qui représentent le seuil et la sensibilité pour détecter les sauts de palier et filtrer le bruit dans les données de capteur.

    Parameters:
    ----------
    None
        Cette fonction ne prend aucun argument.

    Returns:
    ----------
    Tuple[float, float]
        Un tuple de deux valeurs flottantes : (seuil, sensibilité).
        - seuil (float) : Le coefficient pour détecter les sauts de palier.
        - sensibilité (float) : Le coefficient pour filtrer le bruit.

    Examples:
    ----------
    >>> type(seuil_capteur1()), len(seuil_capteur1())
    (<class 'tuple'>, 2)
    >>> seuil_capteur1()
    (0.052, 0.014)

    Notes:
    -----
    Les valeurs de seuil et de sensibilité sont actuellement fixées à 0.052 et 0.014 respectivement.
    Ces valeurs peuvent être ajustées pour optimiser la détection des sauts de palier et la filtration du bruit.
    """

    # Valeurs de seuil et de sensibilité pour les hélices de type 20 et 40 m/s
    # Ces valeurs sont utilisées pour détecter les sauts de palier et filtrer le bruit dans les données de capteur
    seuil = 0.052
    sensibilite = 0.014

    # Retour du tuple de valeurs
    return (seuil, sensibilite)

# Fonction qui retourne les valeurs de seuil pour le capteur 2
def seuil_capteur2() -> Tuple[float, float]:
    """
    Retourne les valeurs (seuil, sensibilité) pour la MacCaffrey, dans ce cas précis.

    Cette fonction retourne un tuple de deux valeurs flottantes qui représentent le seuil et la sensibilité pour détecter les sauts de palier et filtrer le bruit dans les données de capteur de la MacCaffrey.

    Parameters:
    ----------
    None
        Cette fonction ne prend aucun argument.

    Returns:
    ----------
    Tuple[float, float]
        Un tuple de deux valeurs flottantes : (seuil, sensibilité).
        - seuil (float) : Le coefficient pour détecter les sauts de palier.
        - sensibilité (float) : Le coefficient pour filtrer le bruit.

    Examples:
    ----------
    >>> type(seuil_capteur2()), len(seuil_capteur2())
    (<class 'tuple'>, 2)
    >>> seuil_capteur2()
    (0.3, 0.15)

    Notes:
    -----
    Les valeurs de seuil et de sensibilité sont actuellement fixées à 0.30 et 0.15 respectivement pour la MacCaffrey.
    Ces valeurs peuvent être ajustées pour optimiser la détection des sauts de palier et la filtration du bruit pour ce type de capteur.
    """

    # Valeurs de seuil et de sensibilité pour la MacCaffrey
    # Ces valeurs sont utilisées pour détecter les sauts de palier et filtrer le bruit dans les données de capteur
    seuil = 0.30
    sensibilite = 0.15

    # Retour du tuple de valeurs
    return (seuil, sensibilite)

# Fonction pour séparer les valeurs par paliers
def sep_values(data: List[float], seuil_capt: Tuple[float, float]) -> List[float]:
    """
    Sépare les valeurs par paliers.

    Cette fonction prend en entrée une liste de valeurs d'un capteur en décimales et un tuple contenant les valeurs de seuil et de sensibilité.
    Elle retourne une liste des valeurs des paliers.

    Parameters:
    ----------
    data (List[float])
        Liste de valeurs d'un capteur en décimales.
    seuil_capt (Tuple[float, float])
        Tuple contenant les valeurs de seuil et de sensibilité.

    Returns:
    ----------
    List[float]
        Liste des valeurs des paliers.

    Examples:
    ----------
    >>> sep_values([0.0154, 0.0154, 0.0154, 0.0, 0.0154, 0.0], (0.052, 0.014))
    [0.0154, 0.0154, 0.012320000000000001, 0.009240000000000002, 0.0077]
    """

    # Récupérer les valeurs de seuil et de sensibilité à partir du tuple
    seuil, sensibilite = seuil_capt

    # Appliquer un filtrage par moyenne mobile pour réduire le bruit dans les données
    data = moyenne_mobile(data, pas_moyenne_mobile())

    # Nombre total de valeurs dans la liste
    nb_values = len(data)

    # Liste pour stocker les valeurs des paliers
    values_sep = list()

    # Première boucle pour traiter les valeurs initiales et éliminer les petites variations
    for i in range(nb_values - abs(1) - 9):
        # Comparaison avec la sensibilité pour éliminer les petites variations
        if abs(data[i + 9] - data[i]) < sensibilite:
            # Si la variation est inférieure à la sensibilité, conserver la valeur initiale
            data[i] = data[i]
        else:
            # Si la variation est supérieure à la sensibilité, remplacer la valeur par la valeur précédente
            data[i] = data[i - 1]

    # Deuxième boucle pour identifier et marquer les transitions entre les paliers
    for i in range(nb_values - 1):
        # Vérification si la différence entre deux valeurs consécutives est supérieure au seuil
        if abs(data[i + 1] - data[i]) > seuil or abs(data[i] - data[i + 1]) > seuil:
            # Si la différence est supérieure au seuil, ajouter une marque de transition aux valeurs des paliers
            values_sep.append(paliers_mark())
        else:
            # Si la différence est inférieure au seuil, ajouter la valeur actuelle aux valeurs des paliers
            values_sep.append(data[i])

    # Retourner la liste des valeurs des paliers
    frame = inspect.stack()[1]
    filename = frame.filename
    lineno = frame.lineno
    function_name = frame.function
    #print(f"Fonction sep_values utilisée, appelée par : {function_name} dans {filename}:{lineno}")
    #print("Fonction sep_values utilisée, appelée par :", inspect.stack()[1][3])
    return values_sep

# Fonction pour récupérer des informations sur les paliers
def info_values(data):
    """
    Récupère des informations sur les paliers dans une liste de valeurs numériques.

    Cette fonction prend en entrée une liste de valeurs numériques d'un capteur et retourne une liste contenant des informations sur les paliers trouvés.

    Parameters:
    ----------
    data (list[float])
        Liste de valeurs numériques d'un capteur.

    Returns:
    ----------
    list
        Contient :
            - Le nombre total de paliers trouvés (int).
            - La liste de la longueur de chaque palier (list[int]).
            - Le nombre total de valeurs (int).
            - Une liste avec les valeurs où les paliers sont marqués (list[float]).
            - Une liste de tuples (début, fin) indiquant la position de chaque palier (list[tuple]).

    Examples:
    ----------
    >>> info_values([0.0154, 0.0154, 0.0154, paliers_mark(), 0.0154, 0.0154, paliers_mark(), 0.0154, 0.0154])
    [3, [4, 3, 2], 9, [0.0154, 0.0154, 0.0154, -0.03, 0.0154, 0.0154, -0.03, 0.0154, 0.0154], [(0, 2), (4, 5), (7, 8)]]
    """

    # Nombre total de valeurs dans la liste
    nb_values = len(data)

    # Liste pour stocker les valeurs des paliers
    values_sep = [0] * nb_values

    # Initialisation des variables
    paliers_find = 1  # Nombre de paliers trouvés
    plage_len_find = []  # Liste pour stocker la longueur de chaque palier
    paliers_position = []  # Liste pour stocker les positions de début et fin des paliers
    count = 1  # Compteur pour la longueur du palier actuel
    debut = 0  # Position de début du palier actuel

    # Parcours de la liste de valeurs
    for i in range(nb_values):
        # Vérification si la valeur est une marque de séparation de paliers
        if data[i] == paliers_mark():
            # Marquage de la séparation des paliers
            values_sep[i] = paliers_mark()
            # Incrémentation du nombre de paliers trouvés
            paliers_find += 1
            # Ajout de la longueur du palier précédent à la liste
            plage_len_find.append(count)
            # Ajout de la position du palier précédent à la liste
            paliers_position.append((debut, i - 1))
            # Mise à jour du début du prochain palier
            debut = i + 1
            # Réinitialisation du compteur pour la longueur du palier actuel
            count = 1
        else:
            # Copie de la valeur dans la liste des valeurs des paliers
            values_sep[i] = data[i]
            # Vérification si c'est le dernier élément de la liste
            if i == (nb_values - 1):
                # Ajout de la longueur du dernier palier à la liste
                plage_len_find.append(count)
                # Ajout de la position du dernier palier à la liste
                paliers_position.append((debut, i))
            # Incrémentation du compteur pour la longueur du palier actuel
            count += 1

    # Retour des informations sur les paliers trouvés
    return [paliers_find, plage_len_find, nb_values, values_sep, paliers_position]

# Fonction pour créer la liste du nombre de paliers avec la taille
def make_paliers(paliers_find, plage_len_find):
    """
    Crée une liste avec chaque palier.

    Cette fonction prend en entrée le nombre de paliers et une liste de la taille de chaque palier.
    Elle retourne une liste de paliers, où chaque palier est une liste remplie de zéros et la taille de chaque palier est déterminée par la liste de tailles.

    Parameters:
    ----------
    paliers_find : int
        Nombre de paliers.
    plage_len_find : list
        Liste de la taille de chaque palier.

    Returns:
    ----------
    list
        Liste de paliers.

    Examples:
    ----------
    >>> make_paliers(3, [1, 5, 3])
    [[0], [0, 0, 0, 0, 0], [0, 0, 0]]
    """

    # Calcul du nombre de paliers
    nombre_de_paliers = len(plage_len_find)

    # Pré-allocation de la liste de paliers
    paliers = [None] * nombre_de_paliers

    # Boucle sur le nombre de paliers
    for i in range(nombre_de_paliers):
        # Création d'un palier avec la taille déterminée par la liste de tailles
        paliers[i] = [0] * plage_len_find[i]

    # Retour de la liste de paliers
    return paliers

# Fonction pour passer des données séparées en liste des tableaux remplis
def paliers_values_sep(values_sep, nb_values, paliers):
    """
    Passe des données séparées en liste des tableaux remplis.

    Cette fonction prend en entrée une liste de valeurs des paliers, le nombre de valeurs et une liste de paliers.
    Elle retourne une liste de valeurs des paliers, où chaque palier est un tableau rempli de valeurs.

    Parameters:
    ----------
    values_sep : list
        Liste des valeurs des paliers.
    nb_values : int
        Nombre de valeurs.
    paliers : list
        Liste de paliers.

    Returns:
    ----------
    list
        Liste des valeurs des paliers.

    Examples:
    ----------
    >>> paliers_values_sep([1, 2, 3, paliers_mark(), 4, 5, 6], 7, [[0, 0, 0], [0, 0, 0]])
    [[1, 2, 3], [4, 5, 6]]
    """

    # Initialisation des compteurs
    count = 0  # Compteur de paliers
    nb = 0  # Compteur de valeurs dans le palier actuel

    # Copie de la liste de paliers
    values_paliers = paliers

    # Boucle sur les valeurs
    for i in range(nb_values):
        # Vérification si la valeur est une marque de séparation de paliers
        if values_sep[i] == paliers_mark():
            # Remplacement de la dernière valeur du palier actuel par la valeur précédente
            values_paliers[count][nb - 1] = values_sep[i - 1]
            # Passage au palier suivant
            count += 1
            # Réinitialisation du compteur de valeurs dans le palier actuel
            nb = 0
        else:
            # Remplacement de la valeur actuelle dans le palier actuel
            values_paliers[count][nb] = values_sep[i]
            # Incrémentation du compteur de valeurs dans le palier actuel
            nb += 1

    # Retour de la liste de valeurs des paliers
    return values_paliers

def insert_nomscapteurs_gui(valeurs_brutes, numero_capteur):
    """
    Insère les noms des capteurs dans la liste de valeurs.

    Parameters:
    ----------
    valeurs_brutes : list
        Liste de valeurs brutes.
    numero_capteur : int
        Numéro du capteur.

    Returns:
    ----------
    list
        Liste de valeurs avec les noms des capteurs insérés.
    """
    if not isinstance(valeurs_brutes, list):
        raise ValueError("Erreur : 'valeurs_brutes' doit être une liste.")

    valeurs_nettoyees = valeurs_brutes[23:]
    informations_capteurs = fg.get_state("capteurs_manager").get_names_position_capteurs()
    nom_capteur_ref = fg.get_state("champ_nom_capteur_ref").get().strip()

    valeurs_modifiees = valeurs_nettoyees.copy()
    for nom_capteur, position in informations_capteurs:
        prefixe = f"{nom_capteur_ref} " if numero_capteur == 1 else ""
        if int(position) < len(valeurs_modifiees):
            valeurs_modifiees[int(position)] = f"{prefixe}{nom_capteur}"

    return valeurs_modifiees

def isol_capteurs(valeurs: List[Union[str, float]]) -> Dict[str, List[float]]:
    """
    Isôle les valeurs des capteurs dans un dictionnaire.

    Parameters:
    ----------
    valeurs : List[Union[str, float]]
        Liste de valeurs.

    Returns:
    ----------
    Dict[str, List[float]]
        Dictionnaire avec les noms des capteurs comme clés et les listes de valeurs comme valeurs.
        Retourne un dictionnaire vide si la liste en entrée est vide.
    """
    if not isinstance(valeurs, list):
        raise ValueError("Erreur : 'valeurs' doit être une liste.")

    capteurs: Dict[str, List[float]] = {}
    derniere_cle: str | None = None

    for valeur in valeurs:
        if isinstance(valeur, str):
            capteurs[valeur] = []
            derniere_cle = valeur
        elif derniere_cle and isinstance(valeur, (int, float)): #on vérifie le type avant d'ajouter
            capteurs[derniere_cle].append(float(valeur)) #on convertit en float pour l'annotation de type
        elif derniere_cle:
            raise ValueError(f"Erreur : une valeur de type {type(valeur)} a été trouvé après le nom du capteur {derniere_cle}, la valeur doit être numérique")
        else:
            raise KeyError(f"Erreur : Aucun nom de capteur trouvé avant la valeur '{valeur}'.")

    return capteurs

# Fonction pour le traitement général des données
def traitement_general_donnees(
        paliers_find: int, paliers_find2: int, values_sep_paliers: list[list[str]], values_sep_paliers2: list[list[str]],
        entete: list[str], capteur1_info: str = None, capteur2_info: str = None, capteur1_name: str = "Capteur 1",
        capteur2_name: str = "Capteur 2"
) -> list[list[str]]:
    """
    Traite les données générales pour les deux capteurs.

    Cette fonction prend en entrée les nombres de paliers pour les deux capteurs, les listes de valeurs séparées
    par palier pour les deux capteurs, l'entête pour les données traitées, ainsi que les informations et noms
    des capteurs. Elle retourne la liste des données traitées.

    Parameters:
    ----------
    paliers_find : int
        Nombre de paliers pour le capteur 1.
    paliers_find2 : int
        Nombre de paliers pour le capteur 2.
    values_sep_paliers : list[list[str]]
        Liste de valeurs séparées par palier pour le capteur 1.
    values_sep_paliers2 : list[list[str]]
        Liste de valeurs séparées par palier pour le capteur 2.
    entete : list[str]
        Entête pour les données traitées.
    capteur1_info : str, optional
        Informations pour le capteur 1 (par défaut : None).
    capteur2_info : str, optional
        Informations pour le capteur 2 (par défaut : None).
    capteur1_name : str, optional
        Nom du capteur 1 (par défaut : "Capteur 1").
    capteur2_name : str, optional
        Nom du capteur 2 (par défaut : "Capteur 2").

    Returns:
    -------
    list[list[str]]
        Liste des données traitées.
    """

    # Initialisation des listes pour les moyennes et écarts-types
    moyenne = [""] * paliers_find
    moyenne2 = [""] * paliers_find2
    ecartype = [""] * paliers_find
    ecartype2 = [""] * paliers_find2
    nb_p = 13  # Nombre de points amont et aval à enlever au droit d'un changement de palier

    # Conversion des données en nombres
    values_sep_paliers = [[float(x) for x in sublist] for sublist in values_sep_paliers]
    values_sep_paliers2 = [[float(x) for x in sublist] for sublist in values_sep_paliers2]

    # Initialisation de la liste pour les données traitées
    donneestraitees = [["0"] * len(entete) for _ in range(max(paliers_find, paliers_find2))]

    for i in range(max(paliers_find, paliers_find2)):
        if i < len(values_sep_paliers) and i < len(values_sep_paliers2):
            # Traitement des données pour les deux capteurs
            if len(values_sep_paliers[i]) >= 2 * nb_p and len(values_sep_paliers2[i]) >= 2 * nb_p:
                valeurs_capteur1 = values_sep_paliers[i][nb_p: -nb_p]
                valeurs_capteur2 = values_sep_paliers2[i][nb_p: -nb_p]
                moyenne[i] = sum(valeurs_capteur1) / len(valeurs_capteur1)
                ecartype[i] = (sum((x - moyenne[i]) ** 2 for x in valeurs_capteur1) / len(valeurs_capteur1)) ** 0.5 * 1000
                moyenne2[i] = sum(valeurs_capteur2) / len(valeurs_capteur2)
                ecartype2[i] = (sum((x - moyenne2[i]) ** 2 for x in valeurs_capteur2) / len(valeurs_capteur2)) ** 0.5 * 1000
                donneestraitees[i] = (
                    str(calculate_trend(values_sep_paliers[i])), str(round(moyenne[i], 4)), str(round(ecartype[i], 4)),
                    str(calculate_trend(values_sep_paliers2[i])), str(round(moyenne2[i], 4)),
                    str(round(ecartype2[i], 4))
                )
            else:  # Erreur : pas assez d'éléments dans les listes
                print(f"Erreur : Les listes values_sep_paliers[{i}] ou values_sep_paliers2[{i}] n'ont pas assez d'éléments.")
                donneestraitees[i] = ('NA', 'NA', 'NA', 'NA', 'NA', 'NA')
        elif i < len(values_sep_paliers):
            # Traitement des données pour le capteur 1
            if len(values_sep_paliers[i]) >= 2 * nb_p:
                valeurs_capteur1 = values_sep_paliers[i][nb_p: -nb_p]
                moyenne[i] = sum(valeurs_capteur1) / len(valeurs_capteur1)
                ecartype[i] = (sum((x - moyenne[i]) ** 2 for x in valeurs_capteur1) / len(valeurs_capteur1)) ** 0.5 * 1000
                donneestraitees[i] = (
                    str(calculate_trend(values_sep_paliers[i])), str(round(moyenne[i], 4)), str(round(ecartype[i], 4)),
                    'NA', 'NA', 'NA'
                )
            else:  # Erreur : pas assez d'éléments dans la liste
                print(f"Erreur : La liste values_sep_paliers[{i}] n'a pas assez d'éléments.")
                donneestraitees[i] = ('NA', 'NA', 'NA', 'NA', 'NA', 'NA')
        else:
            # Traitement des données pour le capteur 2
            if len(values_sep_paliers2[i]) >= 2 * nb_p:
                valeurs_capteur2 = values_sep_paliers2[i][nb_p: -nb_p]
                moyenne2[i] = sum(valeurs_capteur2) / len(valeurs_capteur2)
                ecartype2[i] = (sum((x - moyenne2[i]) ** 2 for x in valeurs_capteur2) / len(valeurs_capteur2)) ** 0.5 * 1000
                donneestraitees[i] = (
                    'NA', 'NA', 'NA',
                    str(calculate_trend(values_sep_paliers2[i])), str(round(moyenne2[i], 4)),
                    str(round(ecartype2[i], 4))
                )
            else:  # Erreur : pas assez d'éléments dans la liste
                print(f"Erreur : La liste values_sep_paliers2[{i}] n'a pas assez d'éléments.")
                donneestraitees[i] = ('NA', 'NA', 'NA', 'NA', 'NA', 'NA')

    # Retourne la liste des données traitées
    return donneestraitees

def moyenne(liste: list) -> float:
    """
    Renvoie la moyenne des éléments contenus dans une liste.

    Cette fonction prend en entrée une liste de nombres (entiers ou flottants) et retourne leur moyenne arithmétique.
    Si la liste est vide, elle lève une exception ValueError. Si la liste contient des éléments non numériques,
    elle les ignore et calcule la moyenne des éléments numériques restants.

    Parameters:
    ----------
    liste : list
        La liste dont on veut calculer la moyenne. Chaque élément doit être un entier ou un flottant.

    Raises:
    ------
    ValueError
        Si la liste est vide.

    Returns:
    -------
    float
        La moyenne arithmétique des membres de la liste.

    Examples:
    ----------
    >>> moyenne([0,0,1,0,0,0.0,0,0,0,0,0,0,0,10,0,25.80,0,0,0,0,0,0,0,0.0])
    1.5333333333333332
    """

    # Vérification si la liste est vide
    elements_numeriques = [element for element in liste if isinstance(element, (int, float))]
    if not elements_numeriques:
        raise ValueError("La liste est vide ou ne contient pas d'éléments numériques")
    return round(sum(elements_numeriques) / len(elements_numeriques), 7)

def moyenne_mobile(liste: List[float], pas: int, decimales: int = None) -> List[float]:
    """
    Calcule la moyenne mobile en encadrant chaque élément de la liste avec -pas à +pas à partir de liste[pas].

    Cette fonction prend en entrée une liste de nombres flottants et un entier représentant le nombre d'éléments
    à considérer avant et après chaque élément. Elle retourne une liste des moyennes mobiles pour chaque élément
    de la liste en entrée.

    Parameters:
    ----------
    liste : List[float]
        La liste en entrée.
    pas : int
        Le nombre d'éléments à considérer avant et après chaque élément.
    decimales : int, optionnel
        Nombre de décimales pour arrondir les moyennes mobiles. Si None, aucun arrondi n'est effectué.

    Returns:
    -------
    List[float]
        La liste des moyennes mobiles.

    Raises:
    ------
    ValueError:
        Si pas est négatif.
    ValueError:
        Si la liste est vide.

    Examples:
    ----------
    >>> moyenne(moyenne_mobile([1,2,3,4.20,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29], pas = 3))
    14.900492610837437
    >>> moyenne(moyenne_mobile([1,2,3,4.20,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29], pas = 5))
    14.75078369905956
    >>> moyenne(moyenne_mobile([1,2,3,4.20,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29], pas = 0))
    15.006896551724138
    """

    if pas < 0:
        raise ValueError("Le paramètre 'pas' doit être un entier non négatif.")
    if not liste:
        raise ValueError("La liste ne doit pas être vide.")

    taille_liste = len(liste)
    moyennes = []

    for i in range(taille_liste):
        if i < pas:
            moyennes.append(liste[i])
        else:
            debut = max(0, int(i - pas))
            fin = min(taille_liste, int(i + pas + 1))
            moyenne_fenetre = sum(liste[debut:fin]) / (fin - debut)
            if decimales is not None:
                moyenne_fenetre = round(moyenne_fenetre, decimales)
            moyennes.append(moyenne_fenetre)

    return moyennes

def verifier_paliers(paliers_capteur1: list[list[float]], paliers_capteur2: list[list[float]],
                     indices_capteur1: list[tuple], indices_capteur2: list[tuple],
                     nom_capteur1: str, nom_capteur2: str) -> None:
    """
    Compare les paliers de deux capteurs et identifie ceux qui posent un problème.
    Affiche le numéro du palier, le début et la fin pour chaque capteur.
    """

    nombre_paliers1, nombre_paliers2 = len(paliers_capteur1), len(paliers_capteur2)

    if nombre_paliers1!= nombre_paliers2:
        fg.log_message(
            f"[WARNING] Différence dans le nombre de paliers : {nom_capteur1}={nombre_paliers1}, {nom_capteur2}={nombre_paliers2}",
            "WARNING"
        )

    tableau_paliers = f"\nNom capteur 1 : {nom_capteur1}\tNom capteur 2 : {nom_capteur2}\n"
    tableau_paliers += "Paliers\tDébut - Fin (Capteur 1)\tDébut - Fin (Capteur 2)\n"

    nombre_paliers_min = min(nombre_paliers1, nombre_paliers2)

    for i in range(nombre_paliers_min):
        debut1, fin1 = indices_capteur1[i]
        debut2, fin2 = indices_capteur2[i]
        tableau_paliers += f"[{i}]\t({debut1} - {fin1})\t\t({debut2} - {fin2})\n"

    for i in range(nombre_paliers_min, max(nombre_paliers1, nombre_paliers2)):
        if i < nombre_paliers1:
            debut1, fin1 = indices_capteur1[i]
            tableau_paliers += f"[{i}] (Capteur 1)\t({debut1} - {fin1})\t\tOups\n"
        else:
            debut2, fin2 = indices_capteur2[i]
            tableau_paliers += f"[{i}] (Capteur 2)\tOups\t\t({debut2} - {fin2})\n"

    fg.log_message(tableau_paliers, "INFO")

def calculate_trend(values: list) -> tuple:
    """
    Calcule la tendance d'un palier.

    Cette fonction prend en entrée une liste de valeurs numériques et retourne une chaîne de caractères
    décrivant la tendance du palier ('stable ---', 'croissant ->+', 'décroissant +>-') ainsi que la pente
    de la tendance.

    Parameters:
    ----------
    values : list
        Liste de valeurs numériques du palier.

    Returns:
    -------
    tuple
        Un tuple contenant la description de la tendance (str) et la pente de la tendance (float).
    """

    # Vérification si la liste de valeurs est suffisamment longue pour calculer la tendance
    if len(values) < 2:
        # Retourne 'indéterminé' si la liste est trop courte
        return 'indéterminé', 0

    # Conversion des valeurs en tableau numpy pour utiliser les fonctions de numpy
    x = arange(len(values))
    y = array([float(v) for v in values])

    # Calcul de la régression linéaire simplifiée pour déterminer la pente de la tendance
    pente = polyfit(x, y, 1)[0]

    # Définition des seuils de stabilité (à ajuster selon vos besoins)
    SEUIL_STABILITE = 1e-5

    # Détermination de la tendance en fonction de la pente
    if abs(pente) < SEUIL_STABILITE:
        # La tendance est stable si la pente est proche de zéro
        return f"Stb ---", round(pente, 6)
    elif pente > 0:
        # La tendance est croissante si la pente est positive
        return f"Cro ->+", round(pente, 6)
    else:
        # La tendance est décroissante si la pente est négative
        return f"Déc +>-", round(pente, 6)

def compare_paliers(
        capteur1_name: str, capteur2_name: str, paliers_info1: tuple, paliers_info2: tuple,
        values_sep_paliers1: list, values_sep_paliers2: list, logger
) -> str:
    """
    Compare les paliers de deux capteurs avec analyse de tendance.
    """

    paliers_find1, _, _, _, positions1 = paliers_info1
    paliers_find2, _, _, _, positions2 = paliers_info2

    if paliers_find1!= paliers_find2:
        logger.start_context("Analyse des différences de paliers")
        message = [
            f"Différence dans le nombre de paliers: {capteur1_name}={paliers_find1}, {capteur2_name}={paliers_find2}"
        ]
        message.append(f"\n{'=' * 50}")
        message.append(f"{'Palier':<8} {capteur1_name:<25} {capteur2_name:<25}")
        message.append(f"{'-' * 60}")

        max_paliers = max(paliers_find1, paliers_find2)

        for i in range(max_paliers):
            info1 = f"({positions1[i][0]}-{positions1[i][1]}) {calculate_trend(values_sep_paliers1[i])}" if i < len(positions1) and i < len(values_sep_paliers1) else "(-)"
            info2 = f"({positions2[i][0]}-{positions2[i][1]}) {calculate_trend(values_sep_paliers2[i])}" if i < len(positions2) and i < len(values_sep_paliers2) else "(-)"
            message.append(f"[{i:2d}]    {info1:<25} {info2:<25}")

            if i < len(positions1) and i < len(positions2):
                trend1, _ = calculate_trend(values_sep_paliers1[i])
                trend2, _ = calculate_trend(values_sep_paliers2[i])
                if trend1 is None or trend2 is None:
                    logger.warning(f"Tendance manquante pour le palier {i}.")
                else:
                    logger.warning(
                        f"Palier {i}: Tendances différentes - {capteur1_name}: {trend1}, {capteur2_name}: {trend2}"
                    )

        logger.end_context()
        return "\n".join(message)
    return None

def setup_log_display(text_widget):
    """
    Configure l'affichage des logs dans le widget texte.

    Cette fonction configure les tags de couleur pour les différents niveaux de logs
    (debug, info, warning, error, critical) dans le widget texte.

    Parameters:
    ----------
    text_widget
        Le widget texte où les logs seront affichés.
    """

    # Configuration des tags de couleur pour les niveaux de logs
    # Les tags sont utilisés pour appliquer des styles à des parties spécifiques du texte

    # Niveau de log debug : texte gris
    text_widget.tag_configure('log_debug', foreground='gray')

    # Niveau de log info : texte bleu
    text_widget.tag_configure('log_info', foreground='blue')

    # Niveau de log warning : texte orange
    text_widget.tag_configure('log_warning', foreground='orange')

    # Niveau de log error : texte rouge
    text_widget.tag_configure('log_error', foreground='red')

    # Niveau de log critical : texte rouge sur fond jaune
    text_widget.tag_configure('log_critical', foreground='red', background='yellow')

def get_data_with_paliers(data: list[float], seuil_capt: tuple[float, float]) -> tuple[list[float], list[float]]:
    """
    Récupère les données brutes et les données avec détection des paliers.

    Cette fonction prend en entrée les données brutes du capteur et les seuils de détection des paliers.
    Elle retourne les données brutes nettoyées et les données avec marqueurs de paliers (0 aux transitions).

    Parameters:
    ----------
    data : list[float]
        Données brutes du capteur.
    seuil_capt : tuple[float, float]
        Tuple contenant (seuil, sensibilité) pour la détection des paliers.

    Returns:
    -------
    tuple[list[float], list[float]]
        - Liste des données brutes nettoyées.
        - Liste des données avec marqueurs de paliers (0 aux transitions).

    Example:
    -------
    >>> donnees = [0.0154, 0.0154, 0.0154, 0.0, 0.0154, 0.0]
    >>> seuils = (0.052, 0.014)
    >>> brutes, avec_paliers = get_data_with_paliers(donnees, seuils)
    """

    # Nettoyage des données brutes en supprimant les valeurs texte
    data_clean = fc.supp_txt(data)

    # Obtention des données avec détection des paliers en utilisant la fonction sep_values
    values_with_marks = sep_values(data_clean, seuil_capt)

    # Remplacement des marqueurs de paliers par 0 pour obtenir les données avec marqueurs de paliers
    values_with_zeros = [0 if val == paliers_mark() else val for val in values_with_marks]

    # Retourne les données brutes nettoyées et les données avec marqueurs de paliers
    return data_clean, values_with_zeros

if __name__ == "__main__":
    testmod()
