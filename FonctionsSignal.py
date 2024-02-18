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
        " (0.4.3 Bêta_e)"
    """
    return str(" (0.4.3 Bêta_e)")


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
    #return tuple(range(int(n / 2 + 1))) + tuple(range(int(n / 2 - 1), -1, -1))


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
    ([[0.0154, 0.0154, 0.0154, 0.0, 0.0154]], [0.0154, 0.0154, 0.0154, 0.0, 0.0154, 0.0], [0.0154, 0.0154, 0.0154, 0.0, 0.0154], 1)
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
def seuil_capteur1():
    """
    Passage des valeurs (seuil, sensibilité) pour les hélices.

    Returns:
    --------
    tuple
    (0.052, 0.014)
     Examples:
    ----------
    >>> type(seuil_capteur1()), len(seuil_capteur1())
    (<class 'tuple'>, 2)
    """
    return (0.052, 0.014)


# Fonction qui retourne les valeurs de seuil pour le capteur 2
def seuil_capteur2():
    """
    Passage des valeurs (seuil, sensibilité) pour la MacCaffrey.

    Returns:
    --------
    tuple
    (0.69, 0.15)
         Examples:
    ----------
    >>> type(seuil_capteur2()), len(seuil_capteur2())
    (<class 'tuple'>, 2)
    """
    return (0.69, 0.15)


# Fonction pour séparer les valeurs par paliers
def sep_values(sv, seuil_capt):
    """
    Sépare les valeurs par paliers.

    Parameters:
    ----------
    sv : list
        Liste de valeurs décimales.
    seuil_capt : tuple
        Les valeurs de seuil et de sensibilité.

    Returns:
    ----------
    list
        Liste des valeurs des paliers.

    Examples:
    ----------
    >>> sep_values([0.0154, 0.0154, 0.0154, 0.0, 0.0154, 0.0], (0.052, 0.014))
    [0.0154, 0.0154, 0.0154, 0.0, 0.0154]

    """
    # Récupérer les valeurs de seuil et de sensibilité à partir du tuple
    seuil, sensibilite = seuil_capt

    # Nombre total de valeurs
    nb_values = len(sv)

    # Liste pour stocker les valeurs des paliers
    values_sep = list()

    # Première boucle pour traiter les valeurs initiales
    for i in range(nb_values - abs(1) - 9):
        # Comparaison avec la sensibilité pour éliminer les petites variations
        if abs(sv[i + 9] - sv[i]) < sensibilite:
            sv[i] = sv[i]
        else:
            sv[i] = sv[i - 1]

    # Deuxième boucle pour identifier et marquer les transitions entre les paliers
    for i in range(nb_values - 1):
        if abs(sv[i + 1] - sv[i]) > seuil or abs(sv[i] - sv[i + 1]) > seuil:
            values_sep.append(paliers_mark())
        else:
            values_sep.append(sv[i])

    return values_sep


# Fonction pour récupérer des informations sur les paliers
def info_values(iv):
    """
    Récupère des informations sur les paliers.

    Parameters:
    ----------
    iv : list
        Liste de valeurs.

    Returns:
    ----------
    list
        Liste d'informations sur les paliers.

    Examples:
    ----------
    >>> info_values([0, 0.0154, 0, 0, 0.0154, 0, 0, 0, 0])
    [1, [9], 9, [0, 0.0154, 0, 0, 0.0154, 0, 0, 0, 0]]

    Cette fonction prend une liste de valeurs numériques et identifie les paliers
    au sein des données. Elle renvoie une liste contenant les informations suivantes :

    - Le nombre total de paliers trouvés.
    - Une liste indiquant la longueur de chaque palier.
    - Le nombre total de valeurs dans la liste d'entrée.
    - Une liste avec les valeurs où les paliers sont marqués.
    """
    nb_values = len(iv)
    values_sep = list([0] * nb_values)
    paliers_find = 1
    plage_len_find = list()
    count = 1
    for i in range(nb_values):
        if iv[i] == paliers_mark():
            values_sep[i] = paliers_mark()
            paliers_find = paliers_find + 1
            plage_len_find.append(count)
            count = 1
        else:
            values_sep[i] = iv[i]
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

    Parameters:
    ----------
    paliers_find : int
        Nombre de paliers pour le capteur 1.
    paliers_find2 : int
        Nombre de paliers pour le capteur 2.
    values_sep_paliers : list
        Liste des valeurs des paliers pour le capteur 1.
    values_sep_paliers2 : list
        Liste des valeurs des paliers pour le capteur 2.
    entete : list
        Liste des entêtes.
    nb_p = int
        Nombre de points amont et aval à enlever au droit d'un changement de palier

    Returns:
    ----------
    list
        Liste des moyennes et écart-types.

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
    nb_p = 13 #Nombre de points amont et aval à enlever au droit d'un changement de palier

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


if __name__ == "__main__":
    testmod()
