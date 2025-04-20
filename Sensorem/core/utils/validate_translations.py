#!/usr/bin/env python3
# validate_translation.py
"""
Script pour valider et corriger les fichiers de traduction.
Vérifie que toutes les clés sont présentes dans tous les fichiers et peut ajouter les clés manquantes.
Détecte également les problèmes de casse et de formattage similaires.

Utilisation:
python validate_translations.py --add-missing  # Pour ajouter les clés manquantes
python validate_translations.py --fix-similar  # Pour détecter et suggérer des corrections pour les clés similaires
python validate_translations.py --all          # Pour exécuter toutes les vérifications et corrections
"""

import os
import re
import sys
import difflib
from collections import defaultdict
from pathlib import Path
import argparse


def extract_msgids_from_file(file_path):
    """Extrait toutes les clés de traduction (msgid) d'un fichier .po"""
    msgids = {}
    current_line = 0

    with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
        lines = file.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('msgid "') and not line.startswith('msgid ""'):
            # Extrait la clé entre guillemets
            key = line[7:-1]  # Enlève msgid " au début et " à la fin

            # Vérifie s'il y a continuation sur les lignes suivantes
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith('"') and not lines[j].strip().startswith('msgstr'):
                key += lines[j].strip()[1:-1]  # Ajoute le contenu sans les guillemets
                j += 1

            msgids[key] = i + 1  # Stocke la clé avec son numéro de ligne
        i += 1

    return msgids


def extract_translation_keys_from_code(directory):
    """Extrait toutes les clés de traduction utilisées dans le code Python avec leur emplacement."""
    keys_with_locations = defaultdict(list)

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()

                i = 0
                while i < len(lines):
                    line = lines[i]
                    line_number = i + 1

                    # Captures différents formats de chaînes de traduction
                    patterns = [
                        r'_\s*\(\s*"(.+?)"\s*(?:,|\))',  # _("text") ou _("text", ...)
                        r'_\s*\(\s*\'(.+?)\'\s*(?:,|\))',  # _('text') ou _('text', ...)
                        r'_f\s*\(\s*"(.+?)"\s*,',  # _f("text", ...)
                        r'_f\s*\(\s*\'(.+?)\'\s*,',  # _f('text', ...)
                    ]

                    # Vérifie aussi les chaînes multi-lignes
                    triple_double_start = r'_\s*\(\s*"""'
                    triple_single_start = r'_\s*\(\s*\'\'\''

                    # Traitement des chaînes standards
                    for pattern in patterns:
                        for match in re.finditer(pattern, line):
                            key = match.group(1)
                            keys_with_locations[key].append((file_path, line_number))

                    # Traitement des chaînes multi-lignes
                    if re.search(triple_double_start, line) or re.search(triple_single_start, line):
                        start_line = line_number
                        multi_line_str = ""
                        quote_type = '"""' if re.search(triple_double_start, line) else "'''"

                        # Extrait le début de la chaîne après les triples guillemets
                        start_pos = line.find(quote_type) + 3
                        multi_line_str += line[start_pos:]

                        # Continue jusqu'à trouver la fin des triples guillemets
                        i += 1
                        while i < len(lines) and quote_type not in lines[i]:
                            multi_line_str += lines[i]
                            i += 1

                        if i < len(lines):
                            end_pos = lines[i].find(quote_type)
                            if end_pos != -1:
                                multi_line_str += lines[i][:end_pos]

                        keys_with_locations[multi_line_str.strip()].append((file_path, start_line))

                    i += 1

    return keys_with_locations


def find_similar_keys(keys1, keys2, threshold=0.85):
    """Trouve des clés similaires entre deux ensembles de clés, utile pour détecter les problèmes de casse ou d'espacement."""
    similar_pairs = []

    # Convertir dict en set si nécessaire
    if isinstance(keys1, dict):
        keys1_set = set(keys1.keys())
    else:
        keys1_set = keys1

    if isinstance(keys2, dict):
        keys2_set = set(keys2.keys())
    else:
        keys2_set = keys2

    # Pour chaque clé dans le premier ensemble
    for key1 in keys1_set:
        if key1 not in keys2_set:  # Si la clé n'est pas exactement dans le deuxième ensemble
            for key2 in keys2_set:
                # Calcule la similarité en ignorant la casse
                similarity = difflib.SequenceMatcher(None, key1.lower(), key2.lower()).ratio()

                # Calcule aussi la similarité après normalisation des espaces autour de la ponctuation
                norm_key1 = re.sub(r'\s*([:.!?])\s*', r'\1 ', key1).strip()
                norm_key2 = re.sub(r'\s*([:.!?])\s*', r'\1 ', key2).strip()
                norm_similarity = difflib.SequenceMatcher(None, norm_key1.lower(), norm_key2.lower()).ratio()

                # Prend la similarité la plus élevée
                best_similarity = max(similarity, norm_similarity)

                if best_similarity >= threshold:
                    similar_pairs.append((key1, key2, best_similarity))

    # Trie par similarité décroissante
    return sorted(similar_pairs, key=lambda x: -x[2])


def add_missing_keys_to_po(po_file_path, missing_keys, code_keys_with_locations):
    """Ajoute les clés manquantes au fichier .po avec des commentaires indiquant leur emplacement dans le code."""
    with open(po_file_path, 'r', encoding='utf-8', errors='replace') as po_file:
        content = po_file.read()

    existing_keys = extract_msgids_from_file(po_file_path)
    new_entries = []

    for key in sorted(missing_keys):
        if key not in existing_keys:
            locations = code_keys_with_locations.get(key, [])
            comment_lines = []

            for file, line in locations:
                # Crée un chemin relatif plus fiable
                try:
                    rel_path = os.path.relpath(file, Path(po_file_path).parent.parent.parent)
                    # Remplace les backslashes par des slashes avant pour uniformiser
                    rel_path = rel_path.replace('\\', '/')
                    comment_lines.append(f"#AUTOMATICALLY ADDED from : {rel_path}, line {line}")
                except ValueError:
                    # Fallback si le chemin relatif ne peut pas être calculé
                    comment_lines.append(f"#AUTOMATICALLY ADDED from : {file}, line {line}")

            # Escape des caractères spéciaux dans les chaînes
            escaped_key = key.replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t')

            new_entries.append("\n".join(comment_lines))
            new_entries.append(f'msgid "{escaped_key}"')
            new_entries.append(f'msgstr ""')
            new_entries.append("")

    if new_entries:
        with open(po_file_path, 'a', encoding='utf-8') as po_file:
            po_file.write("\n" + "\n".join(new_entries))
        print(f"Ajout de {len(missing_keys)} clés manquantes à : {po_file_path}")
        return True

    return False


def fix_similar_keys(po_file_path, similar_pairs, code_keys_with_locations):
    """Corrige les clés similaires dans un fichier .po pour correspondre à celles du code."""
    if not similar_pairs:
        return False

    with open(po_file_path, 'r', encoding='utf-8', errors='replace') as file:
        content = file.readlines()

    modifications = 0
    msgids = extract_msgids_from_file(po_file_path)

    # Pour chaque paire de clés similaires
    for code_key, po_key, similarity in similar_pairs:
        if po_key in msgids:  # Vérifie que la clé existe dans le fichier PO
            line_number = msgids[po_key]
            if line_number <= len(content):
                i = line_number - 1

                # Trouve la ligne exacte
                while i < len(content) and not content[i].strip().startswith('msgid "'):
                    i += 1

                if i < len(content) and content[i].strip().startswith('msgid "'):
                    # Remplace la clé
                    escaped_code_key = code_key.replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t')
                    new_line = f'msgid "{escaped_code_key}"\n'

                    # Ajoute un commentaire pour indiquer la modification
                    if i > 0 and not content[i - 1].strip().startswith('#'):
                        content.insert(i, f'# MODIFIED: changed from "{po_key}" to match code\n')
                        modifications += 1

                    content[i] = new_line
                    modifications += 1

    if modifications > 0:
        with open(po_file_path, 'w', encoding='utf-8') as file:
            file.writelines(content)
        print(f"Correction de {modifications} clés similaires dans : {po_file_path}")
        return True

    return False


def main():
    parser = argparse.ArgumentParser(description="Valide et corrige les fichiers de traduction.")
    parser.add_argument("-a", "--add-missing", action="store_true",
                        help="Ajoute automatiquement les clés manquantes aux fichiers .po.")
    parser.add_argument("-f", "--fix-similar", action="store_true",
                        help="Suggère des corrections pour les clés similaires (différences de casse, etc.).")
    parser.add_argument("--all", action="store_true", help="Exécute toutes les vérifications et corrections.")
    parser.add_argument("--threshold", type=float, default=0.85,
                        help="Seuil de similarité pour la détection des clés similaires (0.0-1.0).")
    args = parser.parse_args()

    if args.all:
        args.add_missing = True
        args.fix_similar = True

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
            lc_messages_dir = lang_dir / 'LC_MESSAGES'
            if not lc_messages_dir.exists():
                lc_messages_dir = lang_dir / 'LC_messages'  # Vérifie les deux orthographes possibles

            if lc_messages_dir.exists():
                po_path = lc_messages_dir / 'messages.po'
                if po_path.exists():
                    po_files[lang_dir.name] = po_path

    if not po_files:
        print("Aucun fichier de traduction trouvé.")
        return 1

    # Extrait les clés de chaque fichier avec leur numéro de ligne
    keys_by_language = {}
    for lang, path in po_files.items():
        keys_by_language[lang] = extract_msgids_from_file(path)

    # Extraire les clés utilisées dans le code avec leurs emplacements
    print("Extraction des clés de traduction du code source...")
    code_keys_with_locations = extract_translation_keys_from_code(project_root / 'core')
    code_keys = set(code_keys_with_locations.keys())

    # Vérifier si toutes les langues ont les mêmes clés
    all_keys_in_po = set()
    for keys in keys_by_language.values():
        all_keys_in_po.update(keys.keys())

    # Affiche les différences
    has_issues = False
    print(f"\n=== Rapport de validation des traductions ===")

    # Clés manquantes dans chaque langue
    for lang, keys in keys_by_language.items():
        missing = all_keys_in_po - set(keys.keys())
        if missing:
            has_issues = True
            print(f"\n[{lang}] Clés manquantes ({len(missing)}):")
            for key in sorted(missing):
                print(f"  - {key}")

    # Clés utilisées dans le code mais absentes des fichiers de traduction
    missing_in_all = code_keys - all_keys_in_po
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

    # Recherche des clés similaires (problèmes de casse, espaces, etc.)
    if args.fix_similar:
        print("\n=== Recherche des problèmes de casse et de formatage ===")
        for lang, keys in keys_by_language.items():
            # Trouve les clés similaires entre le code et le fichier .po
            similar_pairs = find_similar_keys(code_keys, keys.keys(), args.threshold)

            if similar_pairs:
                has_issues = True
                print(f"\n[{lang}] Clés potentiellement similaires ({len(similar_pairs)}):")
                for code_key, po_key, similarity in similar_pairs:
                    print(f"  - Code: \"{code_key}\" | PO: \"{po_key}\" | Similarité: {similarity:.2f}")

                # Si l'option de correction est activée
                if args.fix_similar:
                    answer = input(f"\nVoulez-vous corriger ces problèmes dans le fichier {lang}? (o/n): ")
                    if answer.lower().startswith('o'):
                        fix_similar_keys(po_files[lang], similar_pairs, code_keys_with_locations)

    # Clés non utilisées dans le code
    for lang, keys in keys_by_language.items():
        unused = set(keys.keys()) - code_keys
        if unused:
            has_issues = True
            print(f"\n[{lang}] Clés non utilisées dans le code ({len(unused)}):")
            for key in sorted(unused):
                line_number = keys[key]
                print(f"  - {key}  ||_(dans {po_files[lang]}, ligne {line_number})")

    if not has_issues:
        print("\nAucun problème détecté! Tous les fichiers de traduction sont synchronisés.")
        return 0
    else:
        print("\nCertains problèmes ont été détectés. Consultez le rapport ci-dessus.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
