# core/utils/logger.py
import tkinter as tk
from datetime import datetime


class LogManager:
    def __init__(self):
        self.outputs = []
        self._setup_colors()

    def _setup_colors(self):
        self.colors = {
            'INFO': 'blue',  # Changé de 'black' à 'blue'
            'DEBUG': 'gray',
            'WARNING': 'orange',
            'ERROR': 'red',
            'CRITICAL': 'darkred'
        }

    def add_output(self, output_widget):
        """Ajoute un widget de sortie pour les logs"""
        self.outputs.append(output_widget)
        self._configure_widget(output_widget)

    def _configure_widget(self, widget):
        """Configure les tags de couleur pour un widget"""
        for level, color in self.colors.items():
            widget.tag_config(level, foreground=color)

    def log(self, message, level='INFO'):
        """Enregistre un message de log"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        formatted = f"[{timestamp}] [{level}] {message}\n"

        # Affichage console
        print(formatted, end='')

        # Affichage dans les widgets
        for widget in self.outputs:
            # S'assurer que les tags de couleur sont configurés
            self._configure_widget(widget)

            widget.config(state=tk.NORMAL)
            widget.insert(tk.END, formatted, level)
            widget.see(tk.END)
            widget.config(state=tk.DISABLED)

    # Méthodes raccourcis
    def debug(self, message):
        self.log(message, 'DEBUG')

    def info(self, message):
        self.log(message, 'INFO')

    def warning(self, message):
        self.log(message, 'WARNING')

    def error(self, message):
        self.log(message, 'ERROR')

    def critical(self, message):
        self.log(message, 'CRITICAL')