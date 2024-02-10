# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 11:10:34 2020
@author: Aelurus
@contributor: Bruno
"""
# FonctionsSignal.py

try:
    from statistics import mean, pstdev
    from doctest import testmod
    import FonctionCSV as fc  # Importe le module FonctionCSV pour utiliser ses fonctions
except Exception as e:
    print(e)
    input('***')

# Fonction qui retourne la version
def version():
    """
    Retourne le numéro de version.

    Returns:
    ----------
    str
        " (0.4.3 Bêta_d)"
    """
    return str(" (0.4.3 Bêta_d)")

# Fonction qui prépare les données pour le graphique
def prep_donnees_graph(donnees):
    """
    Retourne une liste d'éléments en listes d'éléments incrémentée.

    Parameters:
    ----------
    donnees : list
        Liste de données.

    Returns:
    ----------
    list
        Liste d'éléments incrémentée.

    Examples:
    ----------
    >>> prep_donnees_graph([1, 2, 3, 4, 5])
    [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]]
    """
    return [[i, donnee] for i, donnee in enumerate(donnees)]

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
    return tuple(range(int(n / 2 + 1))) + tuple(range(int(n / 2 - 1), -1, -1))

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
    data = fc.supp_txt(data0)  # Épurer les valeurs non entières
    values_sep = sep_values(data, seuil_capt)
    paliers_find, plage_len_find, nb_values, values_sep = info_values(values_sep)
    paliers = make_paliers(paliers_find, plage_len_find)
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

    """
    seuil, sensibilite = seuil_capt
    nb_values = len(sv)
    values_sep = list()

    for i in range(nb_values - abs(1) - 9):
        if abs(sv[i + 9] - sv[i]) < sensibilite:
            sv[i] = sv[i]
        else:
            sv[i] = sv[i - 1]

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
    >>> isol_capteurs([0, 'Capteur1', 0.0154, 0.0154, 0.0154, 0.0, 0.0154, 'Capteur2', 0.0])
    {}
    """
    del values[0:23]
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
            raise KeyError("Error in the first item")
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

    Returns:
    ----------
    list
        Liste des moyennes et écart-types.

    Examples:
    ----------

    """
    moyenne = list([""] * paliers_find)
    moyenne2 = list([""] * paliers_find2)
    ecartype = list([""] * paliers_find)
    ecartype2 = list([""] * paliers_find2)
    donneestraitees2 = [["0"] * len(entete)] * paliers_find

    if len(range(paliers_find)) == len(range(paliers_find2)):
        for i, j in zip(range(paliers_find), range(paliers_find2)):
            moyenne[i] = mean(values_sep_paliers[i][10: -10])
            ecartype[i] = pstdev(values_sep_paliers[i][10: -10]) * 1000

            if values_sep_paliers2[j][10: -10]:
                moyenne2[j] = mean(values_sep_paliers2[j][10: -10])
                ecartype2[j] = pstdev(values_sep_paliers2[j][10: -10])
            else:
                moyenne2[j] = 0
                ecartype2[j] = 0
            donneestraitees2[i] = (str(round(moyenne[i], 4)), str(round(ecartype[i], 4)),
                                   str(round(moyenne2[j], 4)), str(round(ecartype2[j], 4)))
    else:
        print('Erreur dans la taille du palier. P1 = ', paliers_find, 'P2 = ', paliers_find2)
        for i in range(paliers_find):
            moyenne[i] = mean(values_sep_paliers[i][18: -18])
            ecartype[i] = pstdev(values_sep_paliers[i][18: -18])
            donneestraitees2[i] = (str(round(moyenne[i], 4)), str(round(ecartype[i], 4)), 'Oups', 'Oups')
    return donneestraitees2

if __name__ == "__main__":
    testmod()