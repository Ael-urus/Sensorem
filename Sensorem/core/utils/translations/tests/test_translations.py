import unittest
import os
import sys
import tempfile
import shutil
import polib

# Ajuster sys.path pour inclure le répertoire racine du projet (secours)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ..po_utils import POUtils
from ..validate_translations import validate_translations
from ..constants import SUPPORTED_LANGS, SOURCE_LANG


class TestTranslations(unittest.TestCase):
    def setUp(self):
        # Créer un répertoire temporaire pour les fichiers de test
        self.temp_dir = tempfile.mkdtemp()
        self.locale_dir = os.path.join(self.temp_dir, 'locale')
        os.makedirs(self.locale_dir, exist_ok=True)

        # Initialiser POUtils avec un chemin personnalisé
        self.po_utils = POUtils(base_path=self.locale_dir)

        # Créer des fichiers messages.po de test pour en et fr
        self.create_test_po_files()

    def tearDown(self):
        # Nettoyer le répertoire temporaire
        shutil.rmtree(self.temp_dir)

    def create_test_po_files(self):
        # Créer messages.po pour en (langue source)
        en_po = polib.POFile()
        en_po.metadata = {'Language': 'en'}
        en_po.append(polib.POEntry(
            msgid="Processing file: {}",
            msgstr="Processing file: {}"
        ))
        en_po.append(polib.POEntry(
            msgid="Unit (Ref Sensor):",
            msgstr="Unit (Sensor):"  # Incohérence intentionnelle
        ))
        en_po.append(polib.POEntry(
            msgid="English",
            msgstr="English"
        ))
        en_po_path = os.path.join(self.locale_dir, 'en', 'LC_MESSAGES', 'messages.po')
        os.makedirs(os.path.dirname(en_po_path), exist_ok=True)
        en_po.save(en_po_path)

        # Créer messages.po pour fr
        fr_po = polib.POFile()
        fr_po.metadata = {'Language': 'fr'}
        fr_po.append(polib.POEntry(
            msgid="Processing file: {}",
            msgstr="Traitement du fichier : {}"
        ))
        fr_po.append(polib.POEntry(
            msgid="Unit (Ref Sensor):",
            msgstr=""  # Traduction manquante intentionnelle
        ))
        fr_po.append(polib.POEntry(
            msgid="English",
            msgstr="Anglais"
        ))
        fr_po_path = os.path.join(self.locale_dir, 'fr', 'LC_MESSAGES', 'messages.po')
        os.makedirs(os.path.dirname(fr_po_path), exist_ok=True)
        fr_po.save(fr_po_path)

    def test_load_or_create_po(self):
        # Tester le chargement d'un fichier PO existant
        po = self.po_utils.load_or_create_po('en')
        self.assertEqual(len(po), 3)
        self.assertEqual(po.find("Processing file: {}").msgstr, "Processing file: {}")

        # Tester la création d'un nouveau fichier PO
        new_lang = 'de'
        po = self.po_utils.load_or_create_po(new_lang)
        self.assertEqual(len(po), 0)
        po_path = os.path.join(self.locale_dir, 'de', 'LC_MESSAGES', 'messages.po')
        self.assertTrue(os.path.exists(po_path))

    def test_save_po(self):
        # Tester la sauvegarde d'un fichier PO
        po = self.po_utils.load_or_create_po('en')
        po.append(polib.POEntry(msgid="Test", msgstr="Test"))
        self.po_utils.save_po(po, 'en')
        reloaded_po = polib.pofile(os.path.join(self.locale_dir, 'en', 'LC_MESSAGES', 'messages.po'))
        self.assertEqual(len(reloaded_po), 4)
        self.assertEqual(reloaded_po.find("Test").msgstr, "Test")

    def test_validate_format_specifiers(self):
        # Créer un fichier PO avec une erreur de spécificateur de format
        po = polib.POFile()
        po.metadata = {'Language': 'test'}
        po.append(polib.POEntry(
            msgid="Processing file: {}",
            msgstr="Processing file: {0}"  # Spécificateur incorrect
        ))
        temp_po_path = os.path.join(self.locale_dir, 'test', 'LC_MESSAGES', 'messages.po')
        os.makedirs(os.path.dirname(temp_po_path), exist_ok=True)
        po.save(temp_po_path)

        test_po = self.po_utils.load_or_create_po('test')
        issues = self.po_utils.validate_format_specifiers(test_po)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0][0], "Processing file: {}")

    def test_validate_translations(self):
        # Tester la validation des traductions avec le base_path temporaire
        valid, corrections = validate_translations(interactive=False, base_path=self.locale_dir)

        # Attendre 2 corrections :
        # 1. source_lang_mismatch pour "Unit (Ref Sensor):" en en
        # 2. missing_translation pour "Unit (Ref Sensor):" en fr
        self.assertFalse(valid)
        self.assertEqual(len(corrections), 2)

        # Vérifier la correction pour en
        en_correction = next(c for c in corrections if c['lang'] == 'en')
        self.assertEqual(en_correction['msgid'], "Unit (Ref Sensor):")
        self.assertEqual(en_correction['old_msgstr'], "Unit (Sensor):")
        self.assertEqual(en_correction['new_msgstr'], "Unit (Ref Sensor):")
        self.assertEqual(en_correction['type'], "source_lang_mismatch")

        # Vérifier la correction pour fr
        fr_correction = next(c for c in corrections if c['lang'] == 'fr')
        self.assertEqual(fr_correction['msgid'], "Unit (Ref Sensor):")
        self.assertEqual(fr_correction['old_msgstr'], "")
        self.assertEqual(fr_correction['new_msgstr'], "Need Tr")
        self.assertEqual(fr_correction['type'], "missing_translation")

    def test_no_false_positives(self):
        # Vérifier qu'aucun faux positif inconsistent_msgstr n'est détecté pour en
        po = self.po_utils.load_or_create_po('en')
        for entry in po:
            if entry.msgid == "Processing file: {}":
                self.assertEqual(entry.msgstr, "Processing file: {}")  # msgstr == msgid est valide
        valid, corrections = validate_translations(interactive=False, base_path=self.locale_dir)
        inconsistent_corrections = [c for c in corrections if c['type'] == 'inconsistent_msgstr']
        self.assertEqual(len(inconsistent_corrections), 0)


if __name__ == "__main__":
    unittest.main()