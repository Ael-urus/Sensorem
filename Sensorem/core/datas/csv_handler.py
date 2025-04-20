# core/datas/csv_handler.py
import pandas as pd

def read_csv(file_path):
    """Lire un fichier CSV et retourner ses données."""
    return pd.read_csv(file_path).to_dict(orient="records")