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
    from typing import List, Union

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

def invalide_values() -> list[str]:
    """Retourn la list des valeurs invalide à supprimer dans un fichier ou pour le traitement"""
    list = ('Invalid', '#N/A', 'Calibration', '#DIV/0 !')
    return (list)

def read_col_CSV(fichier:str, sep:str, n:int)-> List[Union[str, float]]:
    """
    Lit la colonne spécifiée d'un fichier CSV et retourne les valeurs.

    Parameters:
    ----------
    :fichier : str
        Le nom du fichier -> "mon_fichier.csv"
    :sep: str
        Le séparateur des colonnes, par exemple -> ";"
    :n: int
        Le numéro de la colonne à lire

    Returns:
    ----------
    list
        Les valeurs de la colonne du fichier, remplaçant les séparateurs de décimales de "," à "." si nécessaire.
        Ignore les valeurs non entières, échappe les valeurs vides de la colonne.

    Examples:
    ----------
    >>> read_col_CSV("DebudFindeFichier.csv", ";", 2)
    ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'V1 (V)', 'Mon Capteur', 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0028, 0.0028, 0.0026, 0.0027, 0.0027, 0.0028, 0.0029, 0.003, 0.0025, 0.0025, 0.0023, 0.0055, 0.0025, 0.0025, 0.0025, 0.00285, 0.00285, 0.00285, 0.00285, 0.00285, 0.00285, 0.00285, 0.00285, 0.00285, 0.0025, 0.00295, 0.0025]
   """
    col: List[Union[str, float]] = []

    with open(fichier, "r") as fichier_csv:
        lecteur_csv = csv.reader(fichier_csv, delimiter=sep)

        for row in lecteur_csv:
            if len(row) > n:
                try:
                    value = row[n]
                    if value in invalide_values():
                        if len(col) > 0:
                            value = col[-1]
                        else:
                            value = float(0.0)
                    if isinstance(row[n], str):
                        notation_point = row[n].replace(",", ".")
                        col.append(float(notation_point))
                    else:
                        col.append(float(row[n]))
                except (ValueError, IndexError):
                    col.append(value)
        return col


def supp_txt(data0: list[str]) -> list[float]:
    """
    Enlève les noms des capteurs des données brutes pour éviter de faire planter le tracé 'Données brutes du Gui'.

    Parameters:
    ----------
        :data0 : list
            Les données de la mesure du capteur avec des valeurs str et float.

    Returns:
    ----------
        list
        Les données de la mesure du capteur où toutes les valeurs str et ligne vide sont supprimées.

    Examples:
    ----------
    >>> supp_txt(['Capteur', '12.3', '15.6', '15.6', '14.2', ''])
    [12.3, 15.6, 15.6, 14.2]
    >>> supp_txt(read_col_CSV("DebudFindeFichier.csv", ";", 2))
    [0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0028, 0.0028, 0.0026, 0.0027, 0.0027, 0.0028, 0.0029, 0.003, 0.0025, 0.0025, 0.0023, 0.0055, 0.0025, 0.0025, 0.0025, 0.00285, 0.00285, 0.00285, 0.00285, 0.00285, 0.00285, 0.00285, 0.00285, 0.00285, 0.0025, 0.00295, 0.0025]
   """
    data = []
    for i in data0:
        try:
            data.append(float(i))
        except ValueError:
            pass

    return data

def main() ->None:
    """ Lance tout une toutouille, positionné à chaque script"""
    testmod()  # Exécute les tests doctest lorsqu'il est exécuté en tant que script principal

if __name__ == "__main__":
    main()