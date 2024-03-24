# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 11:10:34 2020
@author: Aelurus
@contributor: Bruno
"""
# FonctionsSignal.py

try:
    import sys
    import os
    from statistics import mean, pstdev
    from doctest import testmod
    import FonctionCSV as fc  # Importe le module FonctionCSV pour utiliser ses fonctions
    #from collections import deque

except ImportError as import_error:
    module_name = import_error.name if hasattr(import_error, 'name') else None
    print(f"Erreur d'importation dans le module {module_name}: {import_error}")
    print(f"Fichier en cours d'exécution : {os.path.basename(__file__)}")
    input('Appuyez sur Entrée pour continuer...')
    sys.exit(1)
except Exception as e:
    print(f"Une exception s'est produite dans le module {__name__}: {e}")
    print(f"Fichier en cours d'exécution : {os.path.basename(__file__)}")
    input('Appuyez sur Entrée pour continuer...')
    sys.exit(1)


# Fonction qui retourne la version
def version():
    """
    Retourne le numéro de version.

    Returns:
    ----------
    str
        " (0.4.3.2 Bêta)"
    """
    return str(" (0.4.3.2 Bêta)")

def pas_moyenne_mobile()-> int:
    """
    Retourne les pas pour la moyenne mobile, arbitrairement calé à 3, c'est une option qui pourrait être mis dans le gui,
    pour la piloter en fonction du signal et voir le resultat en direct.

    Returns:
        3

    """
    return 2
# Fonction qui prépare les données pour le graphique
def prep_donnees_graph(donnees):
    """
    Transforme une liste de données en une liste d'éléments incrémentée.

    Parameters:
    ----------
    donnees : list
        Liste de données.

    Returns:
    ----------
    list
        Liste d'éléments incrémentée où chaque élément est une liste [indice, valeur].

    Examples:
    ----------
    >>> prep_donnees_graph([1, 2, 3, 4, 5])
    [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]]
    """
    # Utilise la fonction enumerate pour obtenir l'indice et la valeur de chaque élément
    # puis crée une liste d'éléments incrémentée en utilisant une liste en compréhension
    return [[indice, valeur] for indice, valeur in enumerate(donnees)]


# Fonction pour générer des noms de paliers
def gen_nom_paliers(n):
    """
    Retourne une liste incrémentée ascendante et descendante axée sur le milieu du nombre passé en argument.

    Parameters:
    ----------
    n : int
        Nombre de paliers.

    Returns:
    ----------
    tuple
        Liste incrémentée ascendante et descendante.

    Examples:
    ----------
    >>> print(gen_nom_paliers(9))
    (0, 1, 2, 3, 4, 3, 2, 1, 0)
    """
    # Calcule la moitié du nombre de paliers
    moitie = int(n / 2)

    # Génère une liste ascendante de 0 à moitie (inclus)
    liste_ascendante = tuple(range(moitie + 1))

    # Génère une liste descendante de moitie - 1 à 0 (inclus)
    liste_descendante = tuple(range(moitie - 1, -1, -1))

    # Concatène les deux listes pour obtenir la liste complète
    liste_complete = liste_ascendante + liste_descendante

    return liste_complete
    # return tuple(range(int(n / 2 + 1))) + tuple(range(int(n / 2 - 1), -1, -1))


# Fonction qui définit la valeur pour marquer la séparation des paliers
def paliers_mark():
    """
    Définition de la valeur pour marquer la séparation des paliers.

    Returns:
    ----------
    float
        -0.03
    """
    return float(-0.03)


# Fonction principale pour le traitement du signal
def traitement_signal(data0, seuil_capt):
    """
    Appel et compile tous les traitements du capteur.

    Parameters:
    ----------
    data0 : list
        Les données brutes du capteur.
    seuil_capt : tuple
        Les valeurs de seuil et de sensibilité pour l'identification des paliers.

    Returns:
    ----------
    tuple
        values_sep_paliers : list
            Liste des valeurs des paliers.
        data : list
            Les données brutes du capteur.
        values_sep : list
            Liste des valeurs de séparation des paliers.
        paliers_find : int
            Le nombre de paliers trouvés.

    Examples:
    ----------
    >>> traitement_signal([0.0154, 0.0154, 0.0154, 0.0, 0.0154, 0.0], (0.052, 0.014))
    ([[0.0154, 0.0154, 0.012320000000000001, 0.009240000000000002, 0.0077]], [0.0154, 0.0154, 0.0154, 0.0, 0.0154, 0.0], [0.0154, 0.0154, 0.012320000000000001, 0.009240000000000002, 0.0077], 1)


    """
    # Épurer les valeurs non entières des données brutes du capteur
    data = fc.supp_txt(data0)

    # Séparer les valeurs par paliers en utilisant les seuils fournis
    values_sep = sep_values(data, seuil_capt)

    # Récupérer des informations sur les paliers
    paliers_find, plage_len_find, nb_values, values_sep = info_values(values_sep)

    # Créer la liste des paliers avec la taille de chaque palier
    paliers = make_paliers(paliers_find, plage_len_find)

    # Passer des données séparées en liste des tableaux remplis
    values_sep_paliers = paliers_values_sep(values_sep, nb_values, paliers)

    return values_sep_paliers, data, values_sep, paliers_find


# Fonction qui retourne les valeurs de seuil pour le capteur 1
def seuil_capteur1() -> tuple:
    """
    Retourne des valeurs (seuil, sensibilité) pour les hélices de type 20 et 40 m/s.

    Args:
    -----
    seuil (float): Le coefficient pour détecter les sauts de palier.
    sensibilite (float): Le coefficient pour filtrer le bruit.

    Returns:
    --------
    tuple (a, b), (0.052, 0.014).  a est le coefficient pour detecter les sauts de palier et  b est le coefficient pour filtrer le bruit

    Examples:
    ----------
    >>> type(seuil_capteur1()), len(seuil_capteur1())
    (<class 'tuple'>, 2)
    """
    return (0.052, 0.014)


# Fonction qui retourne les valeurs de seuil pour le capteur 2
def seuil_capteur2() -> tuple:
    """
    Retourne les valeurs (seuil, sensibilité) pour la MacCaffrey, dans ce cas précis.

    Args:
    -----
    seuil (float): Le coefficient pour détecter les sauts de palier.
    sensibilite (float): Le coefficient pour filtrer le bruit.

    Returns:
    --------
    tuple (a, b)

    a est le coefficient pour detecter les sauts de palier, le seuil

    b est le coefficient pour filtrer le bruit, la sensibilitée

    Examples:
    ----------
    >>> type(seuil_capteur2()), len(seuil_capteur2())
    (<class 'tuple'>, 2)
    """
    return (0.60, 0.15)


# Fonction pour séparer les valeurs par paliers
def sep_values(data: list[float], seuil_capt: tuple) -> list:
    """
    Sépare les valeurs par paliers.

    Parameters:
    ----------
    data : list
        Liste de valeurs d'un capteur en décimales.
    seuil_capt : tuple
        Les valeurs de seuil et de sensibilité.

    Returns:
    ----------
    list
        Liste des valeurs des paliers.

    Examples:
    ----------
    >>> sep_values([0.0154, 0.0154, 0.0154, 0.0, 0.0154, 0.0], (0.052, 0.014))
    [0.0154, 0.0154, 0.012320000000000001, 0.009240000000000002, 0.0077]

    """
    # Récupérer les valeurs de seuil et de sensibilité à partir du tuple
    seuil, sensibilite = seuil_capt

    #Mise en place d'un filtrage par moyenne mobile
    data = moyenne_mobile(data, pas_moyenne_mobile())
    # Nombre total de valeurs
    nb_values = len(data)

    # Liste pour stocker les valeurs des paliers
    values_sep = list()

    # Première boucle pour traiter les valeurs initiales
    for i in range(nb_values - abs(1) - 9):
        # Comparaison avec la sensibilité pour éliminer les petites variations
        if abs(data[i + 9] - data[i]) < sensibilite:
            data[i] = data[i]
        else:
            data[i] = data[i - 1]

    # Deuxième boucle pour identifier et marquer les transitions entre les paliers
    for i in range(nb_values - 1):
        if abs(data[i + 1] - data[i]) > seuil or abs(data[i] - data[i + 1]) > seuil:
            values_sep.append(paliers_mark())
        else:
            values_sep.append(data[i])

    return values_sep


# Fonction pour récupérer des informations sur les paliers
def info_values(data: list[float]) -> list:
    """
    Récupère des informations sur les paliers dans une liste de valeurs numériques.

    Parameters:
    ----------
    data : list[float]
        Liste de valeurs numériques d'un capteur.

    Returns:
    ----------
    list
        Liste d'informations sur les paliers, contenant :
        - Le nombre total de paliers trouvés.
        - Une liste indiquant la longueur de chaque palier.
        - Le nombre total de valeurs dans la liste d'entrée.
        - Une liste avec les valeurs où les paliers sont marqués.

    Examples:
    ----------
    >>> info_values([0, 0.0154, 0, 0, 0.0154, 0, 0, 0, 0])
    [1, [9], 9, [0, 0.0154, 0, 0, 0.0154, 0, 0, 0, 0]]
    >>> info_values([])
    [1, [], 0, []]

    Cette fonction prend une liste de valeurs numériques et identifie les paliers
    au sein des données. Elle renvoie une liste contenant les informations suivantes :

        - Le nombre total de paliers trouvés.
        - Une liste indiquant la longueur de chaque palier.
        - Le nombre total de valeurs dans la liste d'entrée.
        - Une liste avec les valeurs où les paliers sont marqués.
    """
    nb_values = len(data)
    values_sep = list([0] * nb_values)
    paliers_find = 1
    plage_len_find = list()
    count = 1
    for i in range(nb_values):
        if data[i] == paliers_mark():
            values_sep[i] = paliers_mark()
            paliers_find = paliers_find + 1
            plage_len_find.append(count)
            count = 1
        else:
            values_sep[i] = data[i]
            if i == (nb_values - 1):
                plage_len_find.append(count)
            count = count + 1
    return [paliers_find, plage_len_find, nb_values, values_sep]


# Fonction pour créer la liste du nombre de paliers avec la taille
def make_paliers(paliers_find, plage_len_find):
    """
    Crée une liste avec chaque palier.

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

       Cette fonction prend le nombre de paliers (paliers_find) et une liste de la taille
    de chaque palier (plage_len_find). Elle retourne une liste de paliers, où chaque palier
    est une liste remplie de zéros et la taille de chaque palier est déterminée par la liste
    plage_len_find.
    """
    paliers = list([0] * paliers_find)
    for i in range(len(paliers)):
        paliers[i] = list([0] * plage_len_find[i])
    return paliers


# Fonction pour passer des données séparées en liste des tableaux remplis
def paliers_values_sep(values_sep, nb_values, paliers):
    """
    Passe des données séparées en liste des tableaux remplis.

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

    """
    count = 0
    nb = 0
    values_paliers = paliers
    for i in range(nb_values):
        if values_sep[i] == paliers_mark():
            values_paliers[count][nb] = values_sep[i - 1]
            count = count + 1
            nb = 0
        else:
            values_paliers[count][nb] = values_sep[i]
            nb = nb + 1
    return values_paliers


# Fonction pour isoler les capteurs
def isol_capteurs(values):
    """
    Isoler les capteurs.

    Parameters:
    ----------
    values : list
        Liste de valeurs.

    Returns:
    ----------
    dict
        Dictionnaire des noms de capteurs avec les valeurs.

    Examples:
    ----------
    >>> isol_capteurs([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 'Capteur1', 0.0154, 0.0154, 0.0154, 0.0, 0.0154, 'Capteur2', 0.0])
    {'Capteur1': [0.0154, 0.0154, 0.0154, 0.0, 0.0154], 'Capteur2': [0.0]}
    """
    del values[0:23]  # la suppression des 23 premieres ligne sont en rapport avec le fichier de sortie de central
    last_key = None
    values_capteurs = dict()
    for value in values:
        if value == 'Invalid':
            value = 0.01
        if isinstance(value, str):
            values_capteurs[value] = list()
            last_key = value
        elif last_key:
            values_capteurs[last_key].append(value)
        else:
            raise KeyError("Error in the first item, no sensor name in the line 23")
    return values_capteurs


# Fonction pour le traitement général des données
def traitement_general_donnees(paliers_find, paliers_find2, values_sep_paliers, values_sep_paliers2, entete):
    """
       Calcule les moyennes et écart-types pour remplir les onglets.

       Cette fonction prend en compte les données de deux capteurs pour chaque palier, calcule les moyennes et écart-types,
       puis retourne une liste de tuples contenant ces valeurs.

           Parameters:
           ----------
               paliers_find: (int)
                   Nombre de paliers pour le capteur 1.
               paliers_find2 : int
                   Nombre de paliers pour le capteur 2.
               values_sep_paliers : List[List[float]]
                   Liste des valeurs des paliers pour le capteur 1.
               values_sep_paliers2 : List[List[float]]
                   Liste des valeurs des paliers pour le capteur 2.
               entete : List[str]
                   Liste des entêtes.
               nb_p : int
                   Nombre de points amont et aval à enlever au droit d'un changement de palier.

           Returns:
           ----------
               List[Tuple[str, str, str, str]]
                   Liste des moyennes et écart-types.

           Raises:
           ----------
               ValueError:
                   Si la liste values_sep_paliers ou values_sep_paliers2 n'a pas assez d'éléments.

    Examples:
    ----------
    >>> traitement_general_donnees(1,1,[[0.0025, 0.0025, 0.0025, 0.0025, 0.0025,0.0028, 0.0025, 0.0025, 0.0025, 0.0025,0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0027, 0.0025, 0.0025, 0.0023, 0.0055, 0.0025, 0.0025, 0.0025, 0.00285, 0.0025, 0.00295]],[[0.001, 0.01, 0.01, 0.014, 0.01, 0.01, 0.013, 0.01, 0.01,0.01, 0.013, 0.01, 0.01,0.01, 0.013, 0.01, 0.01,0.01, 0.013, 0.01, 0.01, 0.01, 0.01, 0.01, 0.019, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01]],['--------------------------Nom capteur [N° palier] Moyenne [V] Écart-type [mV]'])
    [('0.0025', '0.0', '0.0109', '0.0014')]
    """
    # Initialisation des listes pour les moyennes et écarts-types
    moyenne = list([""] * paliers_find)
    moyenne2 = list([""] * paliers_find2)
    ecartype = list([""] * paliers_find)
    ecartype2 = list([""] * paliers_find2)
    nb_p = 13  # Nombre de points amont et aval à enlever au droit d'un changement de palier

    # Initialisation de la liste pour les données traitées
    donneestraitees2 = [["0"] * len(entete) for _ in
                        range(paliers_find)]  # Il faut les 2 même taille pour la mise en tableau

    # Vérification si le nombre de paliers est le même pour les deux capteurs
    if len(range(paliers_find)) == len(range(paliers_find2)):
        # Boucle sur les paliers des deux capteurs
        for i, j in zip(range(paliers_find), range(paliers_find2)):
            # Vérification si le nombre d'éléments dans la liste de valeurs est suffisant
            if len(values_sep_paliers[i]) >= 20:
                # Calcul des moyennes et écart-types pour le capteur 1
                moyenne[i] = mean(map(float, values_sep_paliers[i][nb_p: -nb_p]))
                ecartype[i] = pstdev(map(float, values_sep_paliers[i][nb_p: -nb_p]))
            else:
                print(f"Erreur: La liste values_sep_paliers[{i}] n'a pas assez d'éléments.")
                moyenne2[i] = 'Oups'
                ecartype2[i] = 'Oups'

            # Vérification si le nombre d'éléments dans la liste de valeurs du capteur 2 est suffisant
            if len(values_sep_paliers2[j]) >= 20:
                # Calcul des moyennes et écart-types pour le capteur 2
                moyenne2[j] = mean(map(float, values_sep_paliers2[j][nb_p: -nb_p]))
                ecartype2[j] = pstdev(map(float, values_sep_paliers2[j][nb_p: -nb_p]))
            else:
                print(f"Erreur: La liste values_sep_paliers2[{j}] n'a pas assez d'éléments.")
                moyenne2[j] = 'Oups'
                ecartype2[j] = 'Oups'

            # Remplissage de la liste des données traitées
            donneestraitees2[i] = (str(round(moyenne[i], 4)), str(round(ecartype[i], 4)),
                                   str(round(moyenne2[j], 4)), str(round(ecartype2[j], 4)))
    else:
        # Affichage d'une erreur si le nombre de paliers est différent
        print('Nombre de palier. P1 = ', paliers_find, 'P2 = ', paliers_find2)
        print('Taille du palier. P1 = ', len(values_sep_paliers), 'P2 = ', len(values_sep_paliers2))

        # Correction pour la différence de taille dans les paliers
        for i in range(paliers_find):
            # Calcul des moyennes et écart-types pour le capteur 1
            moyenne[i] = mean(values_sep_paliers[i][nb_p: -nb_p])
            ecartype[i] = pstdev(values_sep_paliers[i][nb_p: -nb_p])

            # Remplissage de la liste des données traitées avec 'Oups' pour le capteur 2
            donneestraitees2[i] = (str(round(moyenne[i], 4)), str(round(ecartype[i], 4)), 'Oups', 'Oups')

    # Retourne la liste des données traitées
    return donneestraitees2


def moyenne(liste: list) -> list:
    """
    Renvoie la moyenne des éléments contenus dans une liste

    Parameters
    ----------
    liste : list
        La liste dont on veut calculer la moyenne. Chaque élément doit être un entier ou un flottant.

    Raises
    ------
    Exception
       Message indiquant que la liste est vide ou ne contient pas exclusivement des int ou des float.

    Returns
    -------
    float : int ou float
           La moyenne arithmétique des membres de la liste.


    Examples:
    ----------
    >>> moyenne([0,0,1,0,0,0.0,0,0,0,0,0,0,0,10,0,25.80,0,0,0,0,0,0,0,0.0])
    1.5333333333333332
    """
    n = len(liste)

    if n == 0:
        raise ValueError("La liste est vide")
    try :
        # Calcul de la somme des éléments de la liste
        somme = sum(liste)
    except TypeError:
        somme = 0
        print('Attention ! Certains éléments de votre liste sont différents des float ou de int')

    # Calcul de la moyenne en divisant la somme par le nombre d'éléments
    moyenne = somme / n
    if n == 1:
        moyenne = somme
    return moyenne


def moyenne_mobile(liste: list[float], pas: int):
    """
    Calcule la moyenne mobile en encadrant chaque élement de la liste avec -pas à +pas à partir de liste[pas].

    Args:
        liste (list[float]): La liste en entrée.
        pas (int): Le nombre d'éléments à considérer avant et après chaque élément.

    Returns:
        list[float]: La liste des moyennes mobiles.

    Examples:
    ----------
    >>> moyenne_mobile([1,2,3,4.20,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29], pas = 3)
    [1, 2, 3, 4.0285714285714285, 5.028571428571429, 6.028571428571429, 7.028571428571429, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 26.5, 27.0, 27.5]
    >>> moyenne_mobile([1,2,3,4.20,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29], pas = 5)
    [1, 2, 3, 4.2, 5, 6.0181818181818185, 7.0181818181818185, 8.018181818181818, 9.018181818181818, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 24.5, 25.0, 25.5, 26.0, 26.5]
    >>> moyenne_mobile([1,2,3,4.20,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29], pas = 0)
    [1, 2, 3, 4.2, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
    """
    taille_liste = len(liste)
    moyennes = []
    for i in range(taille_liste):
        if i < pas or pas == 0:
            moyennes.append(liste[i])
        else:
            # Détermination des indices de la fenêtre mobile pour chaque élément
            debut = max(0, int(i - pas))
            fin = min(taille_liste, int(i + pas)+1)

            # Calcul de la moyenne de la fenêtre autour de l'élément actuel
            moyenne_fenetre = sum(liste[debut:fin]) / (fin - debut)
            moyennes.append(moyenne_fenetre)

    return moyennes

if __name__ == "__main__":
    testmod()
