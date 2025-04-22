# core/models/data_model.py
from core.utils.logger import logger

class DataModel:
    def __init__(self):
        self.csv_data = None
        self.view = None

    def set_csv_data(self, data):
        self.csv_data = data

    def set_view(self, view):
        self.view = view

    def notify_view(self):
        if self.view:
            current_tab = self.view.tab_view.get()
            current_tab_key = next(
                (key for key, value in self.view.tab_name_map.items() if value == current_tab),
                "Processing"
            )
            self.view.refresh_ui(current_tab_key)