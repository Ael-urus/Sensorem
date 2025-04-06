#!/usr/bin/env python3
"""
Script pour valider et corriger les fichiers de traduction.
Vérifie que toutes les clés sont présentes dans tous les fichiers et peut ajouter les clés manquantes.

run in the console, then check the add to complet the missing parts

python validate_translations.py --add-missing
"""

import os
import re
import sys
from collections import defaultdict
from pathlib import Path
import argparse

def extract_msgids_from_file(file_path):
    """Extrait toutes les clés de traduction (msgid) d'un fichier .po"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Utilise une regex pour trouver tous les msgid "..."
    pattern = r'msgid\s+"(.+?)"'
    matches = re.findall(pattern, content)
    return set(matches)


def extract_translation_keys_from_code(directory):
    """Extrait toutes les clés de traduction utilisées dans le code Python avec leur emplacement."""
    keys_with_locations = defaultdict(list)
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_number, line in enumerate(f, 1):
                        # Cherche les appels à _("...") ou _('...')
                        pattern1 = r'_\s*\(\s*"(.+?)"\s*\)'
                        pattern2 = r'_\s*\(\s*\'(.+?)\'\s*\)'
                        pattern3 = r'_f\s*\(\s*"(.+?)"\s*,'
                        pattern4 = r'_f\s*\(\s*\'(.+?)\'\s*,'

                        matches1 = re.findall(pattern1, line)
                        for match in matches1:
                            keys_with_locations[match].append((file_path, line_number))

                        matches2 = re.findall(pattern2, line)
                        for match in matches2:
                            keys_with_locations[match].append((file_path, line_number))

                        matches3 = re.findall(pattern3, line)
                        for match in matches3:
                            keys_with_locations[match].append((file_path, line_number))

                        matches4 = re.findall(pattern4, line)
                        for match in matches4:
                            keys_with_locations[match].append((file_path, line_number))

    return keys_with_locations


def add_missing_keys_to_po(po_file_path, missing_keys, code_keys_with_locations):
    """Ajoute les clés manquantes au fichier .po avec des commentaires indiquant leur emplacement dans le code."""
    with open(po_file_path, 'r+', encoding='utf-8') as po_file:
        content = po_file.read()
        existing_keys = extract_msgids_from_file(po_file_path)
        new_entries = []
        for key in sorted(missing_keys):
            if key not in existing_keys:
                locations = code_keys_with_locations.get(key, [])
                comment_lines = []
                for file, line in locations:
                    comment_lines.append(f"#AUTOMATICALLY ADDED from : {os.path.relpath(file, Path(po_file_path).parent.parent.parent)}, line {line}") # Ajustement du chemin relatif

                new_entries.append("\n".join(comment_lines))
                new_entries.append(f"msgid \"{key}\"")
                new_entries.append(f"msgstr \"Need translation\"")
                new_entries.append("")

        if new_entries:
            po_file.write("\n".join(new_entries))
            print(f"Ajout de {len(missing_keys)} clés manquantes à : {po_file_path}")


def main():
    parser = argparse.ArgumentParser(description="Valide et corrige les fichiers de traduction.")
    parser.add_argument("-a", "--add-missing", action="store_true", help="Ajoute automatiquement les clés manquantes aux fichiers .po.")
    args = parser.parse_args()

    # Détermine le chemin racine du projet
    project_root = Path(__file__).parent.parent.parent
    locale_dir = project_root / 'core' / 'locale'

    if not locale_dir.exists():
        print(f"Erreur: Répertoire des traductions non trouvé: {locale_dir}")
        return 1

    # Récupère tous les fichiers .po
    po_files = {}
    for lang_dir in locale_dir.iterdir():
        if lang_dir.is_dir():
            po_path = lang_dir / 'LC_messages' / 'messages.po'
            if po_path.exists():
                po_files[lang_dir.name] = po_path

    if not po_files:
        print("Aucun fichier de traduction trouvé.")
        return 1

    # Extrait les clés de chaque fichier
    keys_by_language = {}
    for lang, path in po_files.items():
        keys_by_language[lang] = extract_msgids_from_file(path)

    # Extraire les clés utilisées dans le code avec leurs emplacements
    code_keys_with_locations = extract_translation_keys_from_code(project_root / 'core')
    code_keys = set(code_keys_with_locations.keys())

    # Vérifier si toutes les langues ont les mêmes clés
    all_keys = set()
    for keys in keys_by_language.values():
        all_keys.update(keys)

    # Affiche les différences
    has_issues = False
    print(f"=== Rapport de validation des traductions ===")

    # Clés manquantes dans chaque langue
    for lang, keys in keys_by_language.items():
        missing = all_keys - keys
        if missing:
            has_issues = True
            print(f"\n[{lang}] Clés manquantes ({len(missing)}):")
            for key in sorted(missing):
                print(f"  - {key}")

    # Clés utilisées dans le code mais absentes des fichiers de traduction
    missing_in_all = code_keys - all_keys
    if missing_in_all:
        has_issues = True
        print(f"\nClés utilisées dans le code mais absentes des traductions ({len(missing_in_all)}):")
        for key in sorted(missing_in_all):
            locations = code_keys_with_locations.get(key, [])
            for file, line in locations:
                print(f"  - {key}  ||_(dans {os.path.relpath(file, project_root)}, ligne {line})")

        if args.add_missing:
            print("\n=== Ajout automatique des clés manquantes en cours... ===")
            for lang, po_file_path in po_files.items():
                add_missing_keys_to_po(po_file_path, missing_in_all, code_keys_with_locations)
            print("\n=== Fin de l'ajout automatique des clés manquantes ===")

    # Clés non utilisées dans le code
    for lang, keys in keys_by_language.items():
        unused = keys - code_keys
        if unused:
            has_issues = True
            print(f"\n[{lang}] Clés non utilisées dans le code ({len(unused)}):")
            for key in sorted(unused):
                # Rechercher l'emplacement de cette clé dans le fichier .po
                for po_lang, po_path in po_files.items():
                    if po_lang == lang:
                        with open(po_path, 'r', encoding='utf-8') as f:
                            for line_num, line in enumerate(f, 1):
                                if line.startswith(f'msgid "{key}"'):
                                    print(f"  - {key}  ||_(dans {po_path}, ligne {line_num})")
                                    break # Une fois trouvé, on passe à la clé suivante
                        break # Une fois le fichier .po de la langue trouvé, on passe à la langue suivante

    if not has_issues and not args.add_missing:
        print("Aucun problème détecté! Tous les fichiers de traduction sont synchronisés.")
        return 0
    elif not has_issues and args.add_missing:
        print("Aucun problème détecté, et les clés manquantes ont été ajoutées.")
        return 0
    elif has_issues and args.add_missing:
        print("Des problèmes ont été détectés, et les clés manquantes ont été ajoutées.")
        return 1
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())