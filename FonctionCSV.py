# -*- coding: utf-8 -*-
"""
Created on 10/02/2024
@author : Aelurus
"""
# FonctionCSV.py
try:
    import csv
    import sys,os
    from doctest import testmod

except Exception as e:
    print(e)
    input('***')

def read_col_CSV(fichier, sep, n):
    """Pour les deux premiers paramètres attention à bien utiliser les guillements
    car la fonction attend des chaines de caractères.
    fichier <str> : Le nom du fichier -> "mon_fichier.csv"
    sep <str> : Le séparateur des colonnes par exemple -> ";"
    n <int> : Le numéro de la colonne à lire

    Retourne les valeurs de la colone du fichier en remplacant le separateur de
    decimal de , a . si besoin.
    Ignore les valeurs non int
    Echappe les valeurs vide de la colonne comme les fin de fichier de fin de fichier

    >>> supp_txt(read_col_CSV ("DebudFindeFichier.csv", ";", 2))
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

def supp_txt(data0):
    """Fonction qui permet d'enlever les noms des capteurs des données brutes,
    pour ne pas faire planter le tracé 'Données brutes du Gui'.

    Variable :
    ----------

    data : list

    les données de la mesure du capteur avec des valeurs str et float

     Return :
    ----------

    data : list
        les données de la mesure du capteur ou toutes les valeurs str sont supprimés
    """
    data = []
    for i in data0:
        try:
            data.append(float(i))
        except:
            pass

    return data

if __name__ == "__main__":
    testmod()