# logger_config.py
import logging
import os
import sys
import time
from datetime import datetime


# Couleurs pour les logs dans le terminal
class ColoredFormatter(logging.Formatter):
    """Formateur personnalisé pour ajouter des couleurs aux logs."""
    COLORS = {
        'DEBUG': '\033[94m',  # Bleu
        'INFO': '\033[92m',  # Vert
        'WARNING': '\033[93m',  # Jaune
        'ERROR': '\033[91m',  # Rouge
        'CRITICAL': '\033[95m',  # Magenta
        'RESET': '\033[0m'  # Réinitialiser
    }

    def format(self, record):
        log_message = super().format(record)
        if record.levelname in self.COLORS:
            if sys.platform.lower() == 'win32':
                # Windows ne supporte pas les codes ANSI par défaut
                return log_message
            return f"{self.COLORS[record.levelname]}{log_message}{self.COLORS['RESET']}"
        return log_message


def setup_logger(name, verbose_level=0, log_file=None):
    """
    Configure un logger avec un format spécifique.

    Args:
        name (str): Nom du logger.
        verbose_level (int): Niveau de verbosité (0=INFO, 1=DEBUG).
        log_file (str, optional): Chemin du fichier de log.

    Returns:
        logging.Logger: Le logger configuré.
    """
    # Déterminer le niveau de log en fonction de la verbosité
    log_level = logging.INFO
    if verbose_level >= 1:
        log_level = logging.DEBUG

    # Créer le logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Vérifier si le logger a déjà des handlers pour éviter les doublons
    if logger.handlers:
        return logger

    # Format pour la console
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )

    # Handler pour la console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Handler pour le fichier de log si spécifié
    if log_file:
        # Créer le répertoire si nécessaire
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Format pour le fichier (plus détaillé)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


# Classe pour mesurer le temps d'exécution
class TimedOperation:
    """Classe utilitaire pour mesurer le temps d'exécution d'une opération."""

    def __init__(self, name, logger=None):
        """
        Initialise un minuteur pour une opération.

        Args:
            name (str): Nom de l'opération.
            logger (logging.Logger, optional): Logger pour enregistrer les temps.
        """
        self.name = name
        self.logger = logger
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed_time = time.time() - self.start_time
        if self.logger:
            self.logger.info(f"Operation '{self.name}' completed in {elapsed_time:.2f} seconds")
        return False  # Ne pas supprimer les exceptions


# Exemple d'utilisation:
if __name__ == "__main__":
    logger = setup_logger("LoggerTest", verbose_level=1)
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")

    with TimedOperation("Test Operation", logger):
        # Opération longue
        time.sleep(1.5)