# !/usr/bin/env python3
# validate_translations.py
"""
Script pour valider et corriger les fichiers de traduction.
Vérifie que toutes les clés sont présentes dans tous les fichiers et peut ajouter les clés manquantes.
Détecte les problèmes de casse/formattage et supprime les clés non utilisées.
Propose de relancer avec des options de correction si des problèmes sont détectés.
Vérifie que les fichiers ne sont pas vides ou presque vides.
Empêche la suppression accidentelle si aucune clé n'est trouvée dans le code.
Valide la syntaxe des fichiers .po après chaque modification.
Évite d'ajouter des clés en double.
"""

import os
import re
import sys
import difflib
import hashlib
import json
import argparse
import subprocess
from collections import defaultdict
from pathlib import Path

# Ajuster sys.path pour inclure le répertoire racine
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Vérifier l'existence du répertoire core/
if not (BASE_DIR / 'core').exists():
    print(f"Erreur : Répertoire 'core/' introuvable dans {BASE_DIR}")
    sys.exit(1)

try:
    from core.utils.logger import logger
except ImportError as e:
    print(f"Erreur : Impossible d'importer core.utils.logger : {e}")
    sys.exit(1)


def get_file_hash(file_path):
    """Calcule le hachage MD5 d'un fichier."""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        logger.error(f"Erreur lors du calcul du hachage de {file_path} : {e}")
        return None


def load_cache(cache_file):
    """Charge le cache des hachages de fichiers."""
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        logger.error(f"Erreur lors du chargement du cache {cache_file} : {e}")
        return {}


def save_cache(cache_file, cache):
    """Sauvegarde le cache des hachages de fichiers."""
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde du cache {cache_file} : {e}")


def validate_po_syntax(po_file_path):
    """Valide la syntaxe d'un fichier .po avec msgfmt."""
    try:
        result = subprocess.run(
            ['msgfmt', '-c', '-o', os.devnull, str(po_file_path)],
            capture_output=True, text=True, check=True
        )
        logger.info(f"Syntaxe valide pour {po_file_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur de syntaxe dans {po_file_path} : {e.stderr}")
        print(f"Erreur de syntaxe dans {po_file_path} : {e.stderr}")
        return False
    except FileNotFoundError:
        logger.error("Commande 'msgfmt' introuvable. Vérifiez l'installation de gettext.")
        print("Erreur : Commande 'msgfmt' introuvable. Installez gettext.")
        return False


def extract_msgids_from_file(file_path):
    """Extrait toutes les clés de traduction (msgid) d'un fichier .po."""
    msgids = {}
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            lines = file.readlines()
        logger.info(f"Reading {file_path}, {len(lines)} lines")
    except FileNotFoundError:
        logger.error(f"Fichier {file_path} introuvable")
        return {}
    except Exception as e:
        logger.error(f"Erreur lors de la lecture de {file_path} : {e}")
        return {}

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('msgid "') and not line.startswith('msgid ""'):
            key = line[7:-1]
            logger.info(f"Found msgid: '{key}' at line {i + 1}")
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith('"') and not lines[j].strip().startswith('msgstr'):
                key += lines[j].strip()[1:-1]
                j += 1
            msgids[key] = i + 1
        i += 1
    logger.info(f"Total msgids found in {file_path}: {len(msgids)}")
    return msgids


def extract_translation_keys_from_code(directory, cache_file='translation_cache.json'):
    """Extrait les clés de traduction utilisées dans le code Python avec leur emplacement."""
    cache = load_cache(cache_file)
    keys_with_locations = defaultdict(list)
    files_to_scan = []

    logger.info(f"Scanning directory: {directory}")
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                file_hash = get_file_hash(file_path)
                if file_hash:
                    files_to_scan.append((file_path, file_hash))
                    logger.info(f"Found Python file: {file_path}")
                else:
                    logger.warning(f"Could not compute hash for: {file_path}")

    logger.info(f"Files to scan: {len(files_to_scan)}")
    if not files_to_scan:
        logger.info("Aucun fichier Python modifié, utilisation du cache.")
        return cache.get('keys', defaultdict(list))

    for file_path, file_hash in files_to_scan:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
            logger.info(f"Reading file: {file_path}, {len(lines)} lines")
        except Exception as e:
            logger.error(f"Erreur lors de la lecture de {file_path} : {e}")
            continue

        i = 0
        while i < len(lines):
            line = lines[i]
            line_number = i + 1
            patterns = [
                r'_\s*\(\s*"(.+?)"\s*(?:,|\))',
                r'_\s*\(\s*\'(.+?)\'\s*(?:,|\))',
                r'_f\s*\(\s*"(.+?)"\s*,',
                r'_f\s*\(\s*\'(.+?)\'\s*,',
                r'_\s*\(\s*"(.+?)"\s*%\s*.+?\)',
                r'_\s*\(\s*\'(.+?)\'\s*%\s*.+?\)',
            ]
            triple_double_start = r'_\s*\(\s*"""'
            triple_single_start = r'_\s*\(\s*\'\'\''

            for pattern in patterns:
                for match in re.finditer(pattern, line):
                    key = match.group(1)
                    keys_with_locations[key].append((file_path, line_number))
                    logger.info(f"Found key: '{key}' in {file_path}:{line_number}")

            if re.search(triple_double_start, line) or re.search(triple_single_start, line):
                start_line = line_number
                multi_line_str = ""
                quote_type = '"""' if re.search(triple_double_start, line) else "'''"
                start_pos = line.find(quote_type) + 3
                multi_line_str += line[start_pos:]
                i += 1
                while i < len(lines) and quote_type not in lines[i]:
                    multi_line_str += lines[i]
                    i += 1
                if i < len(lines):
                    end_pos = lines[i].find(quote_type)
                    if end_pos != -1:
                        multi_line_str += lines[i][:end_pos]
                key = multi_line_str.strip()
                if key:
                    keys_with_locations[key].append((file_path, start_line))
                    logger.info(f"Found multiline key: '{key}' in {file_path}:{start_line}")
            i += 1

        cache[file_path] = file_hash

    logger.info(f"Total keys found: {len(keys_with_locations)}")
    cache['keys'] = dict(keys_with_locations)
    save_cache(cache_file, cache)
    return keys_with_locations


def find_similar_keys(keys1, keys2, threshold=0.85):
    """Trouve des clés similaires entre deux ensembles de clés."""
    similar_pairs = []
    keys1_set = set(keys1.keys()) if isinstance(keys1, dict) else keys1
    keys2_set = set(keys2.keys()) if isinstance(keys2, dict) else keys2

    for key1 in keys1_set:
        if key1 not in keys2_set:
            for key2 in keys2_set:
                similarity = difflib.SequenceMatcher(None, key1.lower(), key2.lower()).ratio()
                norm_key1 = re.sub(r'\s*([:.!?])\s*', r'\1 ', key1).strip()
                norm_key2 = re.sub(r'\s*([:.!?])\s*', r'\1 ', key2).strip()
                norm_similarity = difflib.SequenceMatcher(None, norm_key1.lower(), norm_key2.lower()).ratio()
                best_similarity = max(similarity, norm_similarity)
                if best_similarity >= threshold:
                    similar_pairs.append((key1, key2, best_similarity))
    return sorted(similar_pairs, key=lambda x: -x[2])


def add_missing_keys_to_po(po_file_path, missing_keys, code_keys_with_locations):
    """Ajoute les clés manquantes au fichier .po avec commentaires, en évitant les doublons."""
    existing_keys = extract_msgids_from_file(po_file_path)
    new_entries = []

    added_keys = 0
    for key in sorted(missing_keys):
        if key not in existing_keys:
            locations = code_keys_with_locations.get(key, [])
            comment_lines = []
            for file, line in locations:
                try:
                    rel_path = os.path.relpath(file, Path(po_file_path).parent.parent.parent).replace('\\', '/')
                    comment_lines.append(f"#AUTOMATICALLY ADDED from : {rel_path}, line {line}")
                except ValueError:
                    comment_lines.append(f"#AUTOMATICALLY ADDED from : {file}, line {line}")
            escaped_key = key.replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t')
            new_entries.append("\n".join(comment_lines))
            new_entries.append(f'msgid "{escaped_key}"')
            new_entries.append(f'msgstr ""')
            new_entries.append("")  # Ligne vide pour séparer les entrées
            logger.info(f"Adding key '{key}' to {po_file_path}")
            added_keys += 1
        else:
            logger.info(f"Skipping key '{key}' as it already exists in {po_file_path}")

    if new_entries:
        try:
            # Valider la syntaxe avant modification
            if not validate_po_syntax(po_file_path):
                logger.error(f"Fichier {po_file_path} contient des erreurs de syntaxe avant ajout.")
                return False
            with open(po_file_path, 'a', encoding='utf-8') as po_file:
                po_file.write("\n" + "\n".join(new_entries))
            logger.info(f"Ajout de {added_keys} clés manquantes à : {po_file_path}")
            # Valider la syntaxe après modification
            if not validate_po_syntax(po_file_path):
                logger.error(f"Échec de la validation de la syntaxe pour {po_file_path} après ajout")
                return False
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout des clés à {po_file_path} : {e}")
            return False
    logger.info(f"Aucune nouvelle clé à ajouter à {po_file_path}")
    return False


def fix_similar_keys(po_file_path, similar_pairs, code_keys_with_locations, auto_fix=False):
    """Corrige les clés similaires dans un fichier .po."""
    if not similar_pairs:
        return False

    try:
        with open(po_file_path, 'r', encoding='utf-8', errors='replace') as file:
            content = file.readlines()
    except Exception as e:
        logger.error(f"Erreur lors de la lecture de {po_file_path} : {e}")
        return False

    modifications = 0
    msgids = extract_msgids_from_file(po_file_path)

    for code_key, po_key, similarity in similar_pairs:
        if po_key in msgids:
            line_number = msgids[po_key]
            if line_number <= len(content):
                i = line_number - 1
                while i < len(content) and not content[i].strip().startswith('msgid "'):
                    i += 1
                if i < len(content) and content[i].strip().startswith('msgid "'):
                    escaped_code_key = code_key.replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t')
                    new_line = f'msgid "{escaped_code_key}"\n'
                    # Vérifier si un msgstr existe
                    j = i + 1
                    msgstr_line = ""
                    while j < len(content) and not content[j].strip().startswith('msgid ') and content[j].strip():
                        if content[j].strip().startswith('msgstr '):
                            msgstr_line = content[j]
                            break
                        j += 1
                    if not msgstr_line:
                        msgstr_line = 'msgstr ""\n'
                    if i > 0 and not content[i - 1].strip().startswith('#'):
                        content.insert(i, f'# MODIFIED: changed from "{po_key}" to match code\n')
                        modifications += 1
                    content[i] = new_line
                    # S'assurer que msgstr suit
                    if j < len(content) and not content[j].strip().startswith('msgstr '):
                        content.insert(j, msgstr_line)
                        modifications += 1
                    modifications += 1

    if modifications > 0:
        try:
            # Valider la syntaxe avant écriture
            if not validate_po_syntax(po_file_path):
                logger.error(f"Fichier {po_file_path} contient des erreurs de syntaxe avant correction.")
                return False
            with open(po_file_path, 'w', encoding='utf-8') as file:
                file.writelines(content)
            logger.info(f"Correction de {modifications} clés similaires dans : {po_file_path}")
            # Valider la syntaxe après modification
            if not validate_po_syntax(po_file_path):
                logger.error(f"Échec de la validation de la syntaxe pour {po_file_path} après correction")
                return False
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'écriture de {po_file_path} : {e}")
            return False
    return False


def remove_unused_keys(po_file_path, unused_keys):
    """Supprime les clés non utilisées d'un fichier .po."""
    try:
        with open(po_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except Exception as e:
        logger.error(f"Erreur lors de la lecture de {po_file_path} : {e}")
        return False

    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('msgid "'):
            key = line[7:-1]
            if key in unused_keys:
                while i < len(lines) and not lines[i].strip() == "":
                    i += 1
                i += 1
                continue
        new_lines.append(lines[i])
        i += 1

    try:
        # Valider la syntaxe avant écriture
        if not validate_po_syntax(po_file_path):
            logger.error(f"Fichier {po_file_path} contient des erreurs de syntaxe avant suppression.")
            return False
        with open(po_file_path, 'w', encoding='utf-8') as file:
            file.writelines(new_lines)
        logger.info(f"Suppression de {len(unused_keys)} clés non utilisées dans {po_file_path}")
        # Valider la syntaxe après modification
        if not validate_po_syntax(po_file_path):
            logger.error(f"Échec de la validation de la syntaxe pour {po_file_path} après suppression")
            return False
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'écriture de {po_file_path} : {e}")
        return False


def suggest_and_rerun(issues):
    """Propose de relancer le script avec des options de correction si des problèmes sont détectés."""
    if not issues:
        return

    print("\n=== Proposition de correction ===")
    print(
        "Des problèmes ont été détectés dans les traductions. Vous pouvez relancer le script avec les options suivantes pour les corriger :")

    options = []
    if "missing_in_lang" in issues or "missing_in_all" in issues or "empty_file" in issues:
        options.append("--add-missing (ajouter les clés manquantes)")
    if "similar_keys" in issues:
        options.append("--auto-fix-similar (corriger automatiquement les clés similaires)")
    if "unused_keys" in issues:
        options.append("--remove-unused (supprimer les clés non utilisées)")
    options.append("--all (exécuter toutes les corrections)")

    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")

    print("\nEntrez le numéro de l'option à exécuter (ou 0 pour quitter) : ")
    try:
        choice = int(input("> "))
    except ValueError:
        print("Entrée invalide. Aucune relance effectuée.")
        return

    if choice == 0:
        print("Aucune relance effectuée. Vous pouvez exécuter manuellement avec les options suggérées.")
        return

    if choice < 1 or choice > len(options):
        print("Choix invalide. Aucune relance effectuée.")
        return

    selected_option = options[choice - 1].split()[0]
    if selected_option == "--all":
        args = ["--all"]
    elif selected_option == "--add-missing":
        args = ["--add-missing"]
    elif selected_option == "--auto-fix-similar":
        args = ["--auto-fix-similar"]
    elif selected_option == "--remove-unused":
        args = ["--remove-unused"]
    else:
        print("Option non reconnue. Aucune relance effectuée.")
        return

    # Confirmer avant relance
    print(f"\nVous allez relancer le script avec : python {sys.argv[0]} {' '.join(args)}")
    print("Voulez-vous continuer ? (o/n) : ")
    confirmation = input("> ").lower()
    if confirmation != 'o':
        print("Relance annulée.")
        return

    # Relancer le script
    try:
        logger.info(f"Relance du script avec les arguments : {' '.join(args)}")
        result = subprocess.run([sys.executable, sys.argv[0]] + args, check=False)
        if result.returncode == 0:
            print("Relance terminée avec succès.")
        else:
            print(f"Erreur lors de la relance. Code de sortie : {result.returncode}")
    except Exception as e:
        logger.error(f"Erreur lors de la relance du script : {e}")
        print(f"Erreur lors de la relance : {e}")


def main():
    parser = argparse.ArgumentParser(description="Valide et corrige les fichiers de traduction.")
    parser.add_argument("-a", "--add-missing", action="store_true",
                        help="Ajoute automatiquement les clés manquantes aux fichiers .po.")
    parser.add_argument("-f", "--fix-similar", action="store_true",
                        help="Suggère des corrections pour les clés similaires.")
    parser.add_argument("--auto-fix-similar", action="store_true",
                        help="Corrige automatiquement les clés similaires sans confirmation.")
    parser.add_argument("-r", "--remove-unused", action="store_true",
                        help="Supprime automatiquement les clés non utilisées des fichiers .po.")
    parser.add_argument("--all", action="store_true", help="Exécute toutes les vérifications et corrections.")
    parser.add_argument("--threshold", type=float, default=0.85,
                        help="Seuil de similarité pour la détection des clés similaires (0.0-1.0).")
    args = parser.parse_args()

    if args.all:
        args.add_missing = True
        args.fix_similar = True
        args.remove_unused = True
        args.auto_fix_similar = True

    project_root = Path(__file__).parent.parent.parent
    locale_dir = project_root / 'core' / 'locale'

    if not locale_dir.exists():
        logger.error(f"Répertoire des traductions non trouvé : {locale_dir}")
        print(f"Erreur : Répertoire des traductions non trouvé : {locale_dir}")
        return 1

    po_files = {}
    for lang_dir in locale_dir.iterdir():
        if lang_dir.is_dir():
            for lc_dir in [lang_dir / 'LC_MESSAGES', lang_dir / 'LC_messages']:
                if lc_dir.exists():
                    po_path = lc_dir / 'messages.po'
                    if po_path.exists():
                        po_files[lang_dir.name] = po_path
                    break

    if not po_files:
        logger.error("Aucun fichier de traduction trouvé.")
        print("Erreur : Aucun fichier de traduction trouvé.")
        return 1

    logger.info("Extraction des clés de traduction du code source...")
    print("Extraction des clés de traduction du code source...")
    code_keys_with_locations = extract_translation_keys_from_code(project_root)  # Scanner tout le projet
    code_keys = set(code_keys_with_locations.keys())

    # Vérifier si aucune clé n'a été trouvée dans le code
    if not code_keys:
        logger.error(
            "Aucune clé de traduction trouvée dans le code source. Vérifiez les fichiers Python et les motifs de traduction.")
        print("Erreur : Aucune clé de traduction trouvée dans le code source. Abandon de la validation.")
        return 1

    # Valider la syntaxe des fichiers .po avant traitement
    for lang, po_file_path in po_files.items():
        if not validate_po_syntax(po_file_path):
            print(f"Erreur : Fichier {po_file_path} contient des erreurs de syntaxe. Corrigez-les avant de continuer.")
            return 1

    keys_by_language = {}
    for lang, path in po_files.items():
        keys_by_language[lang] = extract_msgids_from_file(path)

    # Vérifier si les fichiers .po sont vides ou presque vides
    has_issues = False
    issues = set()
    for lang, keys in keys_by_language.items():
        if len(keys) < 0.9 * len(code_keys):  # Seuil : moins de 90% des clés du code
            has_issues = True
            issues.add("empty_file")
            print(
                f"\n[{lang}] Erreur : Fichier de traduction {po_files[lang]} vide ou presque vide ({len(keys)} clés trouvées, {len(code_keys)} attendues).")
            logger.error(
                f"Fichier {po_files[lang]} contient seulement {len(keys)} clés contre {len(code_keys)} attendues.")

    all_keys_in_po = set()
    for keys in keys_by_language.values():
        all_keys_in_po.update(keys.keys())

    for lang, keys in keys_by_language.items():
        missing = all_keys_in_po - set(keys.keys())
        if missing:
            has_issues = True
            issues.add("missing_in_lang")
            print(f"\n[{lang}] Clés manquantes ({len(missing)}):")
            for key in sorted(missing):
                print(f"  - {key}")

    missing_in_all = code_keys - all_keys_in_po
    if missing_in_all:
        has_issues = True
        issues.add("missing_in_all")
        print(f"\nClés utilisées dans le code mais absentes des traductions ({len(missing_in_all)}):")
        for key in sorted(missing_in_all):
            locations = code_keys_with_locations.get(key, [])
            for file, line in locations:
                print(f"  - {key}  ||_(dans {os.path.relpath(file, project_root)}, ligne {line})")

        if args.add_missing:
            print("\n=== Ajout automatique des clés manquantes ===")
            for lang, po_file_path in po_files.items():
                add_missing_keys_to_po(po_file_path, missing_in_all, code_keys_with_locations)
            print("=== Fin de l'ajout ===")

    if args.fix_similar or args.auto_fix_similar:
        print("\n=== Recherche des problèmes de casse et de formatage ===")
        for lang, keys in keys_by_language.items():
            similar_pairs = find_similar_keys(code_keys, keys.keys(), args.threshold)
            if similar_pairs:
                has_issues = True
                issues.add("similar_keys")
                print(f"\n[{lang}] Clés potentiellement similaires ({len(similar_pairs)}):")
                for code_key, po_key, similarity in similar_pairs:
                    print(f"  - Code: \"{code_key}\" | PO: \"{po_key}\" | Similarité: {similarity:.2f}")
                if args.auto_fix_similar:
                    fix_similar_keys(po_files[lang], similar_pairs, code_keys_with_locations, auto_fix=True)
                elif args.fix_similar:
                    answer = input(f"\nVoulez-vous corriger ces problèmes dans le fichier {lang}? (o/n): ")
                    if answer.lower().startswith('o'):
                        fix_similar_keys(po_files[lang], similar_pairs, code_keys_with_locations)

    for lang, keys in keys_by_language.items():
        unused = set(keys.keys()) - code_keys
        if unused:
            has_issues = True
            issues.add("unused_keys")
            print(f"\n[{lang}] Clés non utilisées dans le code ({len(unused)}):")
            for key in sorted(unused):
                line_number = keys[key]
                print(f"  - {key}  ||_(dans {po_files[lang]}, ligne {line_number})")
            if args.remove_unused:
                print(f"\n=== Suppression des clés non utilisées dans {lang} ===")
                remove_unused_keys(po_files[lang], unused)
                print("=== Fin de la suppression ===")

    if not has_issues:
        logger.info("Aucun problème détecté. Tous les fichiers de traduction sont synchronisés.")
        print("\nSuccès : Aucun problème détecté ! Tous les fichiers de traduction sont synchronisés.")
        return 0
    else:
        logger.warning("Problèmes détectés dans les traductions. Consultez le rapport ci-dessus.")
        print("\nErreur : Problèmes détectés. Consultez le rapport ci-dessus pour les détails.")
        # Proposer de relancer avec des options de correction
        suggest_and_rerun(issues)
        return 1


if __name__ == "__main__":
    sys.exit(main())