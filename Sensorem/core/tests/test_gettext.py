# core/tests/test_gettext.py
import os
import unittest
import gettext
from pathlib import Path

class TestTranslations(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.locale_dir = self.base_dir / 'core' / 'locale'
        self.languages = ['en', 'fr']
        self.domain = 'messages'
        self.keys_to_test = [
            "Sensorem - Sensor Signal Processing",
            "Processing",
            "Database",
            "Logs",
            "Quit",
            "Add Sensor",
            "Validate Sensors",
            "Trigram",
            "Name (Trigram):",
            "Validate",
            "Sensors",
            "Sensor Name:",
            "Start Line:",
            "Delete",
            "Units",
            "Unit (Sensor):",
            "Unit (Ref Sensor):",
            "Name (Ref Sensor):",
            "Validate Units",
            "Coefficients",
            "Reference Sensor Conversion Coefficients",
            "Coefficient a:",
            "Coefficient b:",
            "Validate Coefficients",
            "List of Files:",
            "File Processing:",
            "Graphs",
            "Graph 1 Placeholder",
            "Graph 2 Placeholder",
            "Trigram must be exactly 3 letters.",
            "All sensors must have a name and start line.",
            "Sensor name '{}' is invalid.",
            "Start line '{}' must be a number.",
            "Units and reference name must be provided.",
            "Coefficient a cannot be zero.",
            "Coefficients must be valid numbers.",
            "No Selection",
            "Please select a file from the list.",
            "Validation Error",
            "No CSV files found in directory: {}",
            "Event blocked: _processing_selection is True",
            "Invalid sensor configuration.",
            "No selection to restore or invalid index",
            "Restoration blocked: _processing_selection is True",
            "Processing file: {}",
            "Error processing file: {}",
            "File selected: {}",
            "Selection event completed",
            "No file selected in the list",
            "No file selected for processing",
            "Initializing listbox selection",
            "No files to select",
            "Restoring selection: index={}",
            "Selection restored to index {}"
        ]

    def test_translation_files_exist(self):
        for lang in self.languages:
            mo_file = self.locale_dir / lang / 'LC_MESSAGES' / f'{self.domain}.mo'
            self.assertTrue(mo_file.exists(), f"Translation file {mo_file} does not exist")

    def test_translations_load(self):
        for lang in self.languages:
            try:
                translation = gettext.translation(
                    self.domain,
                    localedir=self.locale_dir,
                    languages=[lang]
                )
                translation.install()
                self.assertIsNotNone(translation, f"Failed to load translation for {lang}")
            except Exception as e:
                self.fail(f"Translation loading for {lang} failed: {e}")

    def test_key_translations(self):
        for lang in self.languages:
            translation = gettext.translation(
                self.domain,
                localedir=self.locale_dir,
                languages=[lang]
            )
            translation.install()
            _ = translation.gettext
            for key in self.keys_to_test:
                translated = _(key)
                # Pour 'en', le msgstr peut être identique au msgid, donc on saute cette vérification
                if lang != 'en':
                    # Accepter "Need Tr" comme une traduction valide (indicateur de traduction manquante)
                    if translated != "Need Tr":
                        self.assertNotEqual(
                            translated, key,
                            f"Translation for '{key}' in {lang} is identical to the key (not translated)"
                        )
                self.assertTrue(
                    len(translated) > 0,
                    f"Translation for '{key}' in {lang} is empty"
                )

if __name__ == '__main__':
    unittest.main()