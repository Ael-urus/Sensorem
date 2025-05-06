# core/models/data_model.py
from core.utils.logger import logger

class DataModel:
    def __init__(self):
        self.csv_data = None
        self.controller = None
        self.trigram = None
        self.trigram_valid = False
        self.sensors = []
        self.sensors_valid = False
        self.units = None
        self.units_valid = False
        self.coefficients = None
        self.coefficients_valid = False

    def set_csv_data(self, data):
        self.csv_data = data
        self.notify_controller()

    def set_controller(self, controller):
        self.controller = controller

    def set_trigram(self, trigram):
        self.trigram = trigram
        self.trigram_valid = True
        self.notify_controller()

    def set_sensors(self, sensors):
        self.sensors = sensors
        self.sensors_valid = True
        self.notify_controller()

    def set_units(self, unit_sensor, unit_ref, ref_name):
        self.units = (unit_sensor, unit_ref, ref_name)
        self.units_valid = True
        self.notify_controller()

    def set_coefficients(self, coef_a, coef_b):
        self.coefficients = (coef_a, coef_b)
        self.coefficients_valid = True
        self.notify_controller()

    def reset_validations(self):
        self.trigram_valid = False
        self.sensors_valid = False
        self.units_valid = False
        self.coefficients_valid = False
        self.notify_controller()

    def notify_controller(self):
        if self.controller and self.controller.view:
            self.controller.view.refresh_ui()