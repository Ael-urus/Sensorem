# file_utils.py
import os

_DOSSIER_ACTUEL = "../"

def dossier_actuel(new_folder=None):
    global _DOSSIER_ACTUEL
    if new_folder is not None:
        if not new_folder:
            raise ValueError("Le nouveau dossier ne peut pas être vide")
        _DOSSIER_ACTUEL = new_folder
    return _DOSSIER_ACTUEL

def normaliser(chemin, *args):
    return os.path.normpath(os.path.join(chemin, *args))