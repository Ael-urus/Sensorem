# constants.py
import os
import json

BASE_DIR = "D:/PycharmGitSensorem/Sensorem-1/Sensorem"
LOCALE_DIR = os.path.join(BASE_DIR, "core", "locale")
SOURCE_DIR = BASE_DIR

CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
DEFAULT_CONFIG = {
    "supported_langs": ["en", "fr"],
    "source_lang": "en"
}

if not os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_CONFIG, f, indent=4)

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

SOURCE_LANG = config["source_lang"]
SUPPORTED_LANGS = config["supported_langs"]

PO_DIR = lambda lang: os.path.join(LOCALE_DIR, lang, "LC_MESSAGES")
PO_FILE = lambda lang: os.path.join(PO_DIR(lang), "messages.po")
MO_FILE = lambda lang: os.path.join(PO_DIR(lang), "messages.mo")