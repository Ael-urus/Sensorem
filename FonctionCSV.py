# -*- coding: utf-8 -*-
"""
Created on 10/02/2024
@author: Aelurus
"""
# FonctionsCSV.py
import csv
import os
from doctest import testmod
from typing import List, Union

import pandas as pd

try:
    from FonctionsGui_V3 import log_message

except Exception as e:
    print(f"Une exception s'est produite dans le module {__name__}: {e}")
    print(f"Fichier en cours d'exécution : {os.path.basename(__file__)}")
    input('Appuyez sur Entrée pour continuer...')
    #sys.exit(1)

def invalide_values() -> list[str]:
    """
    Retourne la liste des valeurs invalides à supprimer dans un fichier ou pour le traitement.

    Cette fonction retourne une liste de chaînes de caractères qui représentent des valeurs invalides
    qui peuvent être présentes dans un fichier ou lors du traitement des données.

    Returns:
    ----------
    list[str]
        La liste des valeurs invalides à supprimer.

    Examples:
    ----------
    >>> invalide_values()
    ['Invalid', '#N/A', 'Calibration', '#DIV/0!', '#DIV/0!', '#VALEUR!']
    """
    # Liste des valeurs invalides à supprimer
    # Ces valeurs sont typiquement générées par les logiciels de tableur ou de traitement de données
    # lorsqu'une erreur se produit ou lorsqu'une cellule est vide
    return ['Invalid', '#N/A', 'Calibration', '#DIV/0!','#DIV/0 !', '#VALEUR !']

def read_col_csv(fichier: str, sep: str, colNumber: int) -> List[Union[str, float]]:
    """
    Lit la colonne spécifiée d'un fichier CSV et retourne les valeurs, en supprimant les valeurs invalides.

    Cette fonction prend en entrée le nom d'un fichier CSV, le séparateur des colonnes et le numéro de la colonne à lire.
    Elle retourne une liste de valeurs, où les valeurs non numériques sont remplacées par des chaînes de caractères et les valeurs vides sont ignorées.

    Parameters:
    ----------
    fichier : str
        Le nom du fichier CSV à lire (par exemple "mon_fichier.csv")
    sep : str
        Le séparateur des colonnes dans le fichier CSV (par exemple ";")
    colNumber : int
        Le numéro de la colonne à lire (la première colonne est à l'index 0)

    Returns:
    ----------
    List[Union[str, float]]
        Les valeurs de la colonne du fichier CSV, où les valeurs non numériques sont remplacées par des chaînes de caractères et les valeurs vides sont ignorées.

    Examples:
    ----------
    >>> read_col_csv("DebudFindeFichier.csv", ";", 2)
    ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'V1 (V)', 'Mon Capteur', 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0028, 0.0028, 0.0026, 0.0027, 0.0027, 0.0028, 0.0029, 0.003, 0.0025, 0.0025, 0.0023, 0.0055, 0.0025, 0.0025, 0.0025, 0.00285, 0.00285, 0.00285, 0.00285, 0.00285, 0.00285, 0.00285, 0.00285, 0.00285, 0.0025, 0.00295, 0.0025]

    Notes:
    -----
    Cette fonction utilise la bibliothèque `csv` pour lire le fichier CSV.
    Elle prend en charge les fichiers CSV avec des séparateurs de décimales différents (par exemple "," ou ".").
    Les valeurs non numériques sont remplacées par des chaînes de caractères.
    Les valeurs vides sont ignorées.
    """

    # Initialisation d'une liste vide pour stocker les valeurs de la colonne
    col: List[Union[str, float]] = []

    # Ouverture du fichier CSV en mode lecture
    with open(fichier, "r") as fichier_csv:
        # Détermination de l'extension du fichier
        ext = fichier.lower().split('.')[-1]

        # Si le fichier est un CSV, utilisation de la bibliothèque `csv` pour le lire
        if ext == 'csv':
            lecteur_csv = csv.reader(fichier_csv, delimiter=sep)
        # Si le fichier est un XLSX, utilisation de la bibliothèque `pandas` pour le lire
        elif ext == 'xlsx':
            df = pd.read_excel(fichier_csv, sheet_name=0)[1]
            log_message(f"Fichier xls, pas encore pris en charge!", "Warning")
            # TODO: implémenter la lecture de fichiers XLSX
            pass
        else:
            log_message(f"Fichier {fichier} non supporté!", "Error")
            return col

        # Lecture du fichier CSV ligne par ligne
        for row in lecteur_csv:
            # Vérification si la ligne a enough de colonnes
            if len(row) > colNumber:
                try:
                    # Récupération de la valeur de la colonne spécifiée
                    value = row[colNumber]

                    # Vérification si la valeur est dans la liste des valeurs invalides
                    if value in invalide_values():
                        # Si la valeur est invalide, utilisation de la dernière valeur valide
                        if len(col) > 0:
                            value = col[-1]
                        else:
                            value = float(0.0)

                    # Vérification si la valeur est une chaîne de caractères
                    if isinstance(row[colNumber], str):
                        # Remplacement du séparateur de décimale par un point
                        notation_point = row[colNumber].replace(",", ".")
                        # Conversion de la valeur en nombre flottant
                        col.append(float(notation_point))
                    else:
                        # Conversion de la valeur en nombre flottant
                        col.append(float(row[colNumber]))
                except (ValueError, IndexError):
                    # Si la conversion échoue, utilisation de la valeur d'origine
                    col.append(value)

    # Retour de la liste de valeurs
    return col

def supp_txt(data0: list[str]) -> list[float]:
    """
    Enlève les noms des capteurs et les valeurs non numériques des données brutes pour éviter de faire planter le tracé 'Données brutes du Gui'.

    Cette fonction prend en entrée une liste de chaînes de caractères représentant les données brutes du capteur,
    et retourne une liste de nombres flottants représentant les valeurs numériques des données.

    Parameters:
    ----------
        data0: list[str]
            Les données de la mesure du capteur avec des valeurs str et float.

    Returns:
    ----------
        list[float]
        Les données de la mesure du capteur où toutes les valeurs str et ligne vide sont supprimées.

    Examples:
    ----------
    >>> supp_txt(['Capteur', '12.3', '15.6', '15.6', '14.2', ''])
    [12.3, 15.6, 15.6, 14.2]
    >>> supp_txt(read_col_csv("DebudFindeFichier-V1.csv", ";", 2))
   [0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0025, 0.0028, 0.0028, 0.0026, 0.0027, 0.0027, 0.0028, 0.0029, 0.003, 0.0025, 0.0025, 0.0023, 0.0055, 0.0025, 0.0025, 0.0025, 0.00285, 0.00285, 0.00285, 0.00285, 0.00285, 0.00285, 0.00285, 0.00285, 0.00285, 0.0025, 0.00295, 0.0025]
    >>> supp_txt(['12.3a', '15.6', '-3.14']) # Les chaînes non numériques sont ignorées
    [15.6, -3.14]

    Notes:
    -----
    Cette fonction utilise une boucle pour itérer sur les éléments de la liste d'entrée.
    Pour chaque élément, elle tente de le convertir en nombre flottant en utilisant la fonction float().
    Si la conversion échoue (par exemple, si l'élément est une chaîne de caractères non numérique),
    la fonction ValueError est levée et l'élément est ignoré.
    """

    # Initialisation d'une liste vide pour stocker les valeurs numériques
    data = []

    # Boucle pour itérer sur les éléments de la liste d'entrée
    for i in data0:
        try:
            # Tentative de conversion de l'élément en nombre flottant
            data.append(float(i))
        except ValueError:
            # Si la conversion échoue, l'élément est ignoré
            pass

    # Retour de la liste de valeurs numériques
    return data

def main() -> None:
    """
    Lance l'exécution principale de l'application.

    Cette fonction est le point d'entrée de l'application et est appelée lorsque
    le script est exécuté directement (et non importé en tant que module).

    Elle exécute les tests doctest pour vérifier la validité du code.

    Returns:
        None
    """
    testmod()  # Exécute les tests doctest lorsqu'il est exécuté en tant que script principal

if __name__ == "__main__":
    main()
