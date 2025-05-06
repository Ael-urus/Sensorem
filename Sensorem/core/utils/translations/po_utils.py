import os
import sys
import polib
import re
import logging

# Ajuster sys.path pour inclure le répertoire racine du projet
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.utils.translations.logger_config import setup_logger

class POUtils:
    def __init__(self, base_path=None):
        self.logger = setup_logger("POUtils")
        self.base_path = base_path if base_path else os.path.join(os.path.dirname(__file__), '..', '..', 'locale')

    def load_or_create_po(self, lang):
        po_path = os.path.join(self.base_path, lang, 'LC_MESSAGES', 'messages.po')
        os.makedirs(os.path.dirname(po_path), exist_ok=True)
        if os.path.exists(po_path):
            try:
                po = polib.pofile(po_path)
                self.logger.info(f"Loaded PO file: {po_path}")
            except Exception as e:
                self.logger.error(f"Error loading PO file {po_path}: {e}")
                po = polib.POFile()
                po.metadata = {'Language': lang}
        else:
            po = polib.POFile()
            po.metadata = {'Language': lang}
            self.logger.info(f"Created new PO file: {po_path}")
            # Sauvegarde explicite pour garantir que le fichier existe
            self.save_po(po, lang)
        return po

    def save_po(self, po, lang):
        po_path = os.path.join(self.base_path, lang, 'LC_MESSAGES', 'messages.po')
        try:
            self.logger.info(f"Saving PO file: {po_path}")
            po.save(po_path)
            self.logger.info(f"PO file saved: {po_path}")
        except Exception as e:
            self.logger.error(f"Error saving PO file {po_path}: {e}")

    def remove_duplicates(self, po):
        seen = set()
        unique_entries = []
        for entry in po:
            if entry.msgid not in seen:
                seen.add(entry.msgid)
                unique_entries.append(entry)
        po[:] = unique_entries
        return po

    def validate_format_specifiers(self, po):
        issues = []
        for entry in po:
            msgid_specs = re.findall(r'\{[^}]*\}', entry.msgid)
            msgstr_specs = re.findall(r'\{[^}]*\}', entry.msgstr) if entry.msgstr else []
            if msgid_specs != msgstr_specs:
                issues.append((entry.msgid, entry.msgstr, msgid_specs, msgstr_specs))
        return issues

    def get_format_specifier_corrections(self, po):
        corrections = []
        for entry in po:
            msgid_specs = re.findall(r'\{[^}]*\}', entry.msgid)
            msgstr_specs = re.findall(r'\{[^}]*\}', entry.msgstr) if entry.msgstr else []
            if msgid_specs != msgstr_specs:
                corrections.append({
                    "lang": po.metadata.get('Language', 'unknown'),
                    "msgid": entry.msgid,
                    "old_msgstr": entry.msgstr,
                    "new_msgstr": entry.msgid,
                    "type": "format_specifier_mismatch"
                })
        return corrections