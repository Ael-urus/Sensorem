# file_manager.py
from ...utils.file_utils import normaliser, dossier_actuel

def num_colonne_lire(capteur: str) -> int:
    capteurs = {
        "capteur1": 2,
        "capteurRef": 10
    }
    try:
        return capteurs[capteur]
    except KeyError:
        raise ValueError(f"Capteur '{capteur}' non trouvé dans la liste des capteurs")

def num_ligne_lire(first_ligne: int = 24) -> int:
    return first_ligne

def get_data_from_file(fichier: str) -> tuple:
    # À implémenter avec FonctionsCSV
    pass