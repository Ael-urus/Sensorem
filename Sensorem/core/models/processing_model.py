# processing_model
import re
from ..utils.i18n import _

class ProcessingModel:
    def validate_trigram(self, trigram):
        if len(trigram) != 3 or not trigram.isalpha():
            raise ValueError(_("Trigram must be exactly 3 letters."))

    def validate_sensors(self, sensors):
        if any(not nom or not debut for nom, debut in sensors):
            raise ValueError(_("All sensors must have a name and start line."))
        for nom, debut in sensors:
            if not re.match(r'^[a-zA-Z0-9_]+$', nom):
                raise ValueError(_("Sensor name '{}' is invalid.").format(nom))
            if not debut.isdigit():
                raise ValueError(_("Start line '{}' must be a number.").format(debut))

    def validate_units(self, unit_sensor, unit_ref, ref_name):
        if not unit_sensor or not unit_ref or not ref_name:
            raise ValueError(_("Units and reference name must be provided."))

    def validate_coefficients(self, coef_a, coef_b):
        try:
            coef_a = float(coef_a)
            coef_b = float(coef_b)
            if coef_a == 0:
                raise ValueError(_("Coefficient a cannot be zero."))
        except ValueError:
            raise ValueError(_("Coefficients must be valid numbers."))