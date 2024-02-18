# -*- coding: utf-8 -*-
"""
Created on 10/02/2024
@author: Aelurus
"""
# FonctionCSV.py

try:
    import csv
    import sys, os
    from doctest import testmod

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


def read_col_CSV(fichier, sep, n):
    """
    Lit la colonne spécifiée d'un fichier CSV et retourne les valeurs.

    Parameters:
    ----------
    fichier : str
        Le nom du fichier -> "mon_fichier.csv"
    sep : str
        Le séparateur des colonnes, par exemple -> ";"
    n : int
        Le numéro de la colonne à lire

    Returns:
    ----------
    list
        Les valeurs de la colonne du fichier, remplaçant les séparateurs de décimales de "," à "." si nécessaire.
        Ignore les valeurs non entières, échappe les valeurs vides de la colonne.

    Examples:
    ----------
    >>> read_col_CSV("DebudFindeFichier.csv", ";", 2)
    ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'V1 (V)', 'Mon Capteur', 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0026, 0.0026, 0.0026, 0.0026, 0.0025, 0.0025, 0.0025, 0.0025, 0.0027, 0.0025, 0.0025, 0.0023, 0.0055, 0.0025, 0.0025, 0.0025, 0.00285, 0.0025, 0.00295, 0.0025]
   """
    file = open(fichier, "r")
    reader = csv.reader(file, delimiter=sep)
    col = []

    for row in reader:
        if (len(row) > n):
            d = len(col)
            #if len(col)> 1 :
                #print(d)
                #print(col[d-1])
            if row[n] == 'Invalid' or row[n] == '#N/A' or row[n] == 'Calibration':
                if d > 1:
                    #print(d)
                    row[n] = col[d-1]
                else:
                    row[n] = float(0.0)  # Supprimer ? car row[n] peut planter (or try/except), notamment sur une ligne vide
            try:
                notation_point = row[n].replace(",", ".")
                col.append(float(notation_point))
            except:
               # if row[n] == 'Invalid':
                    #col.append(0.0)
                col.append(row[n])

    file.close()
    return col


def supp_txt(data0):
    """
    Enlève les noms des capteurs des données brutes pour éviter de faire planter le tracé 'Données brutes du Gui'.

    Parameters:
    ----------
    data0 : list
        Les données de la mesure du capteur avec des valeurs str et float

    Returns:
    ----------
    list
        Les données de la mesure du capteur où toutes les valeurs str sont supprimées

    Examples:
    ----------
    >>> supp_txt(['Capteur', '12.3', '15.6', '15.6', '14.2', ''])
    [12.3, 15.6, 15.6, 14.2]
    """
    data = []
    for i in data0:
        try:
            data.append(float(i))
        except:
            pass

    return data


if __name__ == "__main__":
    testmod()  # Exécute les tests doctest lorsqu'il est exécuté en tant que script principal
