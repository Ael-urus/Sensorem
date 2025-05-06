#!/usr/bin/env python3
# compile_translations.py
import polib
from logger_config import setup_logger
from constants import SUPPORTED_LANGS, PO_FILE, MO_FILE

def compile_translations():
    logger = setup_logger("Compiler")
    logger.info("Compiling translations...")

    for lang in SUPPORTED_LANGS:
        po_path = PO_FILE(lang)
        mo_path = MO_FILE(lang)
        try:
            po = polib.pofile(po_path)
            po.save_as_mofile(mo_path)
            logger.info(f"Compiled {po_path} to {mo_path}")
        except Exception as e:
            logger.error(f"Error compiling {po_path}: {str(e)}")

if __name__ == "__main__":
    compile_translations()