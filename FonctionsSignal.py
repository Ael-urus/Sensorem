# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 11:10:34 2020

@author: Aelurus

@contributor: Bruno

"""
try:
    from statistics import mean, pstdev
    from doctest import testmod
    import csv
    import sys,os
    # from reportlab.graphics.widgets.markers import makeMarker
    # from reportlab.graphics.charts.textlabels import Label

except Exception as e:
    print(e)
    input('***')


# 1

def version():
    """Retourne le numéro de version du logiciel
    """
    # definition et passage du numéro de version du traitement
    # version = str(" (0.4.3 Bêta_c)")
    return str(" (0.4.3 Bêta_c)")


def prep_donnees_graph(donnees):
    """Retourne une liste d'éléments en listes d'éléments incrémentée,
    >>> prep_donnees_graph([1,2,3,4,5])
    [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]]
    """
    return [[i, donnee] for i, donnee in enumerate(donnees)]



def readColCSV1(fichier, sep, n):
    """Pour les deux premiers paramètres attention à bien utiliser les guillements
    car la fonction attend des chaines de caractères.
    fichier <str> : Le nom du fichier -> "mon_fichier.csv"
    sep <str> : Le séparateur des colonnes par exemple -> ";"
    n <int> : Le numéro de la colonne à lire

    retourne les valeurs de la colone du fichier en remplacant le separateur de
    decimal de , a . si besoin.
    Ignore les valeurs non int
    Echappe les valeurs vide de la colonne comme les fin de fichier de fin de fichier

    >>> readColCSV1 ("DebudFindeFichier.csv", ";", 2)
    [0.0154, 0.0154, 0.0154, 0.0, 0.0154, 0.0]
    """
    file = open(fichier, "r")
    reader = csv.reader(file, delimiter=sep)
    col = []
    for row in reader:
        if(len(row)>n):
            # if row[n] == "Invalid": row[n]=float(0.0)
            if row[n] == 'Invalid':
                row[n] = float(0.0)  # BGU supress ? car row[n] peut planter (or try/except), notamment sur une ligne vide
            try:
                notation_point = row[n].replace(",", ".")
                col.append(float(notation_point))
            # except Exception as e:
            except :
                if row[n] == 'Invalid': col.append(0.0)
                # print(e, n)
                # print(row[n])
                # pass
                col.append(row[n])  # la différence est içi entre readColCSV &1 y a une couille mais ..... # BGU : problem potentiel quand ligne vide
                # input('***')
    file.close()
    return col

# determination des coefficients en fonction du nombre de paliers pour la génération de paliers ascendents et descendants
def gen_nom_paliers(n):
    """
    Parametres
    ----------
    n (int) : nombre de paliers

    return
    ------
    une liste incrémentée ascendant et descendant axée sur le milleu du nombe passé en argument
    >>> print (gen_nom_paliers(9))
    (0, 1, 2, 3, 4, 3, 2, 1, 0)
    """
    return tuple(range(int(n / 2 + 1))) + tuple(range(int(n / 2 - 1), -1, -1))


# Recuperation des valeurs pour detection separation des paliers avec
def paliers_mark():
    """Definition de la valeur pour marquer la séparation des paliers.

    Valeur
    ------
    -0.03

    Returns
    -------
    La valeur
    """
    return float(-0.03)


def suppr_txt(data0):
    data = []
    for i in data0:
        try:
            data.append(float(i))
        except:
            pass

    return data


######
def traitement_signal(data0, seuil_capt):
    """Appel et compile tous les traitements du capteur.

    Return :
    -------
    values_sep_paliers  : list

    data  : list
        les données brutes de la mesure du capteur

    values_sep  : list

    paliers_find  : int
        le nombre de paliers trouvé, au mini 1

    TBC
    """
    # Ajout pretraitement pour ne garder que les <float> (épurer les <str>)
    data = suppr_txt(data0)
    # identification des paliers
    values_sep = sep_values(data, seuil_capt)
    paliers_find, plage_len_find, nb_values, values_sep = info_values(values_sep)
    paliers = make_paliers(paliers_find, plage_len_find)
    values_sep_paliers = paliers_values_sep(values_sep, nb_values, paliers)
    return values_sep_paliers, data, values_sep, paliers_find


def seuil_capteur1():
    """Passage des valeurs (seuil,sensibilite)

    seuil       = 0.052 seuil de détection des changements de paliers, le delta entre deux seuils
                    (delta entre deux moyennes de 7 valeurs)

    sensibilite = 0.014 seuil de nettoyage, valeur de bruit du signal, permet d'éliminer les valeurs
                    qui peuvent polluer le signal (delta entre deux valeurs)

    return :
    --------
    les valeurs de seuil et de sensibilité pour identification des paliers des capteurs types hélices
    20 et 40 m/s (mini et macro).
    """
    return (0.052, 0.014)


def seuil_capteur2():
    """Passage des valeurs (seuil,sensibilite)

    seuil       = 0.5 seuil de détection des changements de paliers, le delta entre deux seuils
                    (delta entre deux moyennes de 7 valeurs)

    sensibilite = 0.21 seuil de nettoyage, valeur de bruit du signal, permet d'éliminer les valeurs
                    qui peuvent polluer le signal (delta entre deux valeurs)

    return :
    --------
    les valeurs de seuil et de sensibilité pour identification des paliers des capteurs types MacCaffrey.
    """
    return (0.5, 0.21)


def sep_values(sv,seuil_capt):
    """
    Parameters
    ----------
    sv : TYPE,list
        DESCRIPTION.
        Liste de valeurs décimales, ayant la forme d'un signal carré ascendant puis descendant
        (données expérimentales).
    >>> a = [0.0015  ,0.0015 ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015 , 0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015 , 0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015 , 0.0015 , 0.0015 , 0.0015 , 0.0015 , 0.0015 , 0.0015 , 0.0206 , 0.0779 , 0.1577 , 0.1747 , 0.1769 , 0.1675 , 0.1447 , 0.1294 , 0.1219 , 0.1193 , 0.1187 , 0.1179 , 0.1174 , 0.1175 , 0.1172 , 0.1168 , 0.1169 , 0.1165 , 0.1166 , 0.1167 , 0.1168 , 0.1173 , 0.1176 , 0.1168 , 0.1176 , 0.1172 , 0.1173 , 0.1171 , 0.1165 , 0.1172 , 0.1173 , 0.1174 , 0.1172 , 0.1175 , 0.1177 , 0.1172 , 0.1173 , 0.1173 , 0.1176 , 0.1178 , 0.1173 , 0.1174 , 0.1174 , 0.1172 , 0.1173 , 0.1173 , 0.1174 , 0.1173 , 0.1169 , 0.1171 , 0.1174 , 0.1171 , 0.1172 , 0.1173 , 0.1164 , 0.1164 , 0.1165 , 0.1164 , 0.1165 , 0.1168 , 0.1171 , 0.1172 , 0.1171 , 0.1172 , 0.1177 , 0.1175 , 0.1174 , 0.1176 , 0.1173 , 0.1173 , 0.1171 , 0.1171 , 0.1168 , 0.1167 , 0.1169 , 0.1169 , 0.1169 , 0.1171 , 0.1172 , 0.1173 , 0.2008 , 0.2177 , 0.2205 , 0.2219 , 0.2236 , 0.2237 , 0.2216 , 0.2217 , 0.2216 , 0.2225 , 0.2242 , 0.2231 , 0.2226 , 0.2233 , 0.2225 , 0.2228 , 0.2239 , 0.2239 , 0.2245 , 0.2231 , 0.2228 , 0.2233 , 0.2237 , 0.2238 , 0.2232 , 0.2228 , 0.2236 , 0.3808 , 0.4189 , 0.4319 , 0.4338 , 0.4339 , 0.4307 , 0.4313 , 0.4342 , 0.4319 , 0.4332 , 0.4333 , 0.4329 , 0.4358 , 0.4366 , 0.4353 , 0.4343 , 0.4343 , 0.4337 , 0.4341 , 0.4363 , 0.4318 , 0.4319 , 0.4322 , 0.4312 , 0.4334 , 0.4333 , 0.4334 , 0.4322 , 0.4359 , 0.4337 , 0.4319 , 0.4313 , 0.4325 , 0.4317 , 0.4313 , 0.4307 , 0.4318 , 0.4283 , 0.5441 , 0.6355 , 0.6491 , 0.6531 , 0.6504 , 0.6537 , 0.6538 , 0.6546 , 0.6529 , 0.6537 , 0.6538 , 0.6539 , 0.6539 , 0.6538 , 0.6539 , 0.6539 , 0.6539 , 0.6539 , 0.6534 , 0.6538 , 0.6539 , 0.6534 , 0.6535 , 0.6534 , 0.6525 , 0.6528 , 0.6529 , 0.6554 , 0.6558 , 0.6559 , 0.5521 , 0.4593 , 0.4364 , 0.4325 , 0.4279 , 0.4299 , 0.4287 , 0.4307 , 0.4308 , 0.4309 , 0.4311 , 0.4321 , 0.4328 , 0.4282 , 0.4285 , 0.4324 , 0.4331 , 0.4317 , 0.4328 , 0.4328 , 0.4313 , 0.4332 , 0.4321 , 0.4321 , 0.4351 , 0.4287 , 0.4336 , 0.4304 , 0.4318 , 0.4275 , 0.4271 , 0.4239 , 0.4237 , 0.4054 , 0.2998 , 0.2448 , 0.2449 , 0.2193 , 0.2205 , 0.2189 , 0.2175 , 0.2191 , 0.2197 , 0.2202 , 0.2194 , 0.2189 , 0.2184 , 0.2174 , 0.2179 , 0.2180 , 0.2179 , 0.2195 , 0.2194 , 0.2187 , 0.2211 , 0.2206 , 0.2207 , 0.2212 , 0.2205 , 0.2207 , 0.2208 , 0.2206 , 0.2204 , 0.2195 , 0.2209 , 0.2210 , 0.2203 , 0.2204 , 0.2116 , 0.1881 , 0.18 , 0.1771 , 0.1754 , 0.1606 , 0.1391 , 0.1261 , 0.1209 , 0.1192 , 0.1181 , 0.1181 , 0.1182 , 0.1178 , 0.1175 , 0.1176 , 0.1167 , 0.1179 , 0.1180 , 0.1174 , 0.1174 , 0.1177 , 0.1178 , 0.1176 , 0.1178 , 0.1172 , 0.1178 , 0.1177 , 0.1184 , 0.1182 , 0.1183 , 0.1184 , 0.1181 , 0.1173 , 0.0015 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0015 , 0.0017 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0009 , 0.0010 , 0.0011 , 0.0011 , 0.0011 , 0.0012 , 0.0009 , 0.0005 , 0.0007 , 0.0007 , 0.0005 , 0.0005 , 0.0008 , 0.0008 , 0.0007 , 0.0004 , 0.0005 , 0.0004 , 0.0004 , 0.0004 , 0.0009 , 0.0008 , 0.0009 , ]

    Returns
    -------
    values_sep : TYPE, list
        DESCRIPTION.
        La liste de sortie est l'identification des paliers par le remplacement de sa première
        valeur par paliers_mark(). Une première boucle nettoie le signal des valeurs aberrantes
        Dû à la mesure.
        La deuxième boucle identifie les paliers
    >>> type(sep_values(a))
    <class 'list'>

    """
    seuil,sensibilite=seuil_capt
    nb_values = len(sv)
    values_sep = list()  # Donne brute avec identification des étages
    nb_remplacement = 1

    for i in range(nb_values - abs(nb_remplacement) - 5):
        if abs(sv[i + 5] - sv[i]) < sensibilite:  # attention le i+x (5) est à mettre en accord avec les valeurs d'exclusion des moyenne et ecartype du pdf et de l'interface graphique
            sv[i] = sv[i]
        else:
            sv[i] = sv[i - nb_remplacement]

    for i in range(nb_values - 1):
        if abs(sv[i + 1] - sv[i]) > seuil or abs(sv[i] - sv[i + 1]) > seuil:
            values_sep.append(paliers_mark())
        else:
            values_sep.append(sv[i])
    return values_sep


def make_paliers2(paliers_find, plage_len_find):
    """Création  efzfezrgeùprjcgammiguflfùpronrgzrtzg d'une liste avec chaque palier, le passage est obscure sur le pourquoi :)
    je refais une liste imbriqué avec le nombre de paliers associer à ses valeurs de paliers
    utile pour les graph imlkhl me semble, car les deux biblio de graph prennent pas les mêmes structures je crois
    ...
    TBC
    """
    paliers = list([0] * paliers_find)
    for i in range(len(paliers)):
        paliers[i] = list([0] * plage_len_find[i])
    return paliers

# Recuperation des valeurs generer avec separation par etages
def info_values(iv):
    """ Recuperation des valeurs generer avec separation par paliers.
    prend les valeurs d'un capteur pour les ordonnées par paliers avec identification des informations
    par palier comme le nombre de paliers la longueur de chaque palier.

    Parametre :
    ----------

    iv (float) :

    return :
    -------
    une liste imbriqué de chaque info

    """
    nb_values = len(iv)
    values_sep = list([0] * nb_values)  # Donne brute avec identification des étages
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



# creation de la liste du nombre de paliers avec la taille
def make_paliers(paliers_find, plage_len_find):
    """Création d'une liste avec chaque palier, le passage est obscure sur le pourquoi :)
    je refais une liste imbriqué avec le nombre de paliers associer à ses valeurs de paliers
    utile pour les graph il me semble, car les deux biblio de graph prennent pas les mêmes structures je crois
    ...
    TBC
    """
    paliers = list([0] * paliers_find)
    for i in range(len(paliers)):
        paliers[i] = list([0] * plage_len_find[i])
    return paliers


# Passage de données separer, en liste des tableaux remplis
def paliers_values_sep(values_sep, nb_values, paliers):
    """Passage de données separer, en liste des tableaux remplis,
    je sais plus pourquoi :)
    TBC
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


# Retour une liste des données des capteurs en sous list de données par capteurs
def isol_capteurs(values):
    """Içi c'est la premiere séparation du signal par capteur, le test est si on trouve un nom de capteur
    tous ce qui suit jusqu'a l'autre nom ou la fin sont les données du capteur :p
    TBC
    """
    del values[0:23]
    last_key = None
    values_capteurs = dict()
    for value in values:
        if value == 'Invalid':  # remarque BGU 2022-08_09: impossible, ça a été filtré en amont par readColCSV &1
            #Surement un traitement antérieure au readCol :)
            value = 0.01
        if isinstance(value, str):
            values_capteurs[value] = list()
            last_key = value
        elif last_key:
            values_capteurs[last_key].append(value)
        else:
            raise KeyError("error in the first item")
    return (values_capteurs)  # retourne un dic des noms de capteur avec les valeurs


def traitement_general_donnees(paliers_find, paliers_find2, values_sep_paliers, values_sep_paliers2, entete):
    """Calcule les moyennes et écart-types pour remplir les tabs -
    Sert à la fois à l'affichage dans le GUI et à la génération de pdf
    Merci Bruno
    """

    moyenne = list([""] * paliers_find)
    moyenne2 = list([""] * paliers_find2)
    ecartype = list([""] * paliers_find)
    ecartype2 = list([""] * paliers_find2)
    donneestraitees2 = [["0"] * len(entete)] * paliers_find
    #
    if len(range(paliers_find)) == len(range(paliers_find2)):
        #
        for i, j in zip(range(paliers_find), range(paliers_find2)):
            #
            moyenne[i] = mean(values_sep_paliers[i][
                              7: -7])  # Correction, suppression des valeurs de début et de fin pour les traitements.
            ecartype[i] = pstdev(values_sep_paliers[i][7: -7]) * 1000
            #
            if values_sep_paliers2[j][7: -7]:
                # moyenne2[j] = mean(values_sep_paliers2[i][7: -7])  #BGU: ancienne formulation bizarre
                # ecartype2[j] = pstdev(values_sep_paliers2[i][7: -7])  #BGU: ancienne formulation bizarre
                moyenne2[j] = mean(values_sep_paliers2[j][7: -7])
                ecartype2[j] = pstdev(values_sep_paliers2[j][7: -7])
            else:
                moyenne2[j] = 0
                ecartype2[j] = 0
            donneestraitees2[i] = (str(round(moyenne[i], 4)), str(round(ecartype[i], 4)), str(round(moyenne2[j], 4)),
                                   str(round(ecartype2[j], 4)))
            # donneestraitees2[i] = (str(round(moyenne[j],4)),str(round(ecartype2[i],4)), str(round(moyenne2[i],4)),str(round(ecartype[j],4))) #BGU: ancienne formulation bizarre
            # Attention il y a une inversion, une mauvais attribuation des valeurs ecartype 2 correspond au premier capteur ?
            #
    else:
        for i in range(paliers_find):
            moyenne[i] = mean(values_sep_paliers[i][
                              7: -7])  # Correction, supression des valeurs de début et de fin pour les traitements.
            ecartype[i] = pstdev(values_sep_paliers[i][7: -7]) * 1000
            donneestraitees2[i] = ('Oups', str(round(moyenne[i], 4)), str(round(ecartype[i], 4)), "Oups")
    return donneestraitees2


if __name__ == "__main__":
    testmod()