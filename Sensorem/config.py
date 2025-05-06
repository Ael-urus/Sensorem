# config.py
from pathlib import Path
import logging

BASE_DIR = Path(__file__).resolve().parent
LOCALE_DIR = BASE_DIR / "core" / "locale"
CSV_DIR = BASE_DIR  # Les fichiers CSV sont dans le même répertoire

def setup_logging(level=logging.DEBUG):
    logger = logging.getLogger('Sensorem')
    logger.setLevel(level)
    # Ajouter un handler pour écrire dans un fichier
    log_file = BASE_DIR / 'sensorem.log'
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger