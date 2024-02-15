# -*- coding: utf-8 -*-
"""
Created on 10/02/2024
@author: Aelurus
"""
# FonctionCSV.py

try:
    import csv
    import chardet
    import pandas as pd
    import sys, os
    from doctest import testmod

except ImportError as import_error:
    module_name = import_error.name if hasattr(import_error, 'name') else None
    print(f"Erreur d'importation dans le module {module_name}: {import_error}")
    print(f"Fichier en cours d'exécution : {__file__}")
    input('Appuyez sur Entrée pour continuer...')
except Exception as e:
    print(f"Une exception s'est produite dans le module {__name__}: {e}")
    print(f"Fichier en cours d'exécution : {__file__}")
    input('Appuyez sur Entrée pour continuer...')

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']
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
    >>> supp_txt(read_col_CSV("DebudFindeFichier.csv", ";", 2))
    [0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0027, 0.0025, 0.0025, 0.0023, 0.0055, 0.0025, 0.0025, 0.0025, 0.00285, 0.0025, 0.00295, 0.0025]

    """
    col = []

    with open(fichier, "r", encoding='utf-8', newline='') as file:
        reader = csv.reader(file, delimiter=sep)

        for row in reader:
            value = row[n] if len(row) > n else None

            if value and value.lower() == 'invalid':
                col.append(0.0)
            else:
                try:
                    col.append(float(value.replace(",", ".")))
                except (ValueError, AttributeError):
                    col.append(value)

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
    >>> supp_txt(['12.3', '15.6', 'Invalid', '14.2', ''])
    [12.3, 15.6, 14.2]
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
