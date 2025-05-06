# log_manager.py
import customtkinter as ctk
from datetime import datetime

class LogManager:
    LEVELS = {
        'DEBUG': 0,
        'INFO': 1,
        'WARNING': 2,
        'ERROR': 3,
        'CRITICAL': 4
    }

    def __init__(self, zone_texte):
        self.zone_texte = zone_texte
        self.messages = []
        self.current_context = None

    def start_context(self, context_name):
        self.current_context = context_name
        self._log(f"=== Début {context_name} ===", 'INFO')

    def end_context(self):
        if self.current_context:
            self._log(f"=== Fin {self.current_context} ===", 'INFO')
        self.current_context = None

    def _log(self, message, level):
        timestamp = datetime.now().strftime('%H:%M:%S')
        context_prefix = f"[{self.current_context}] " if self.current_context else ""
        formatted_message = f"{timestamp} [{level}] {context_prefix}{message}\n"
        if self.zone_texte:
            self.zone_texte.configure(state="normal")
            self.zone_texte.insert("end", formatted_message)
            self.zone_texte.see("end")
            self.zone_texte.configure(state="disabled")
        else:
            print(formatted_message)
        self.messages.append((timestamp, level, self.current_context, message))

    def debug(self, message):
        self._log(message, 'DEBUG')

    def info(self, message):
        self._log(message, 'INFO')

    def warning(self, message):
        self._log(message if message else "Message vide ou absent", "WARNING")

    def error(self, message):
        self._log(message, 'ERROR')

    def critical(self, message):
        self._log(message, 'CRITICAL')

    def get_summary(self):
        summary = {level: 0 for level in self.LEVELS}
        for _, level, _, _ in self.messages:
            summary[level] += 1
        return summary