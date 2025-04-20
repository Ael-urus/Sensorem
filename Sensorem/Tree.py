# tree.py
import os
import sys
from datetime import datetime

def list_directory_contents(directory_path, indent=""):
    """
    Liste le contenu d'un répertoire en affichant d'abord les fichiers
    puis les dossiers, tous triés par ordre alphabétique, en ignorant
    les fichiers cachés et les dossiers __pycache__.

    Args:
        directory_path (str): Chemin du répertoire à lister
        indent (str): Indentation pour représenter la hiérarchie
    """
    try:
        # Récupérer tous les éléments du répertoire
        items = os.listdir(directory_path)

        # Séparer les fichiers et les dossiers, en ignorant les fichiers/dossiers cachés et __pycache__
        files = []
        directories = []

        for item in items:
            # Ignorer les fichiers/dossiers cachés (commençant par un point)
            if item.startswith('.'):
                continue

            # Ignorer les dossiers __pycache__
            if item == '__pycache__':
                continue

            full_path = os.path.join(directory_path, item)
            if os.path.isfile(full_path):
                files.append(item)
            elif os.path.isdir(full_path):
                directories.append(item)

        # Trier les fichiers et les dossiers par ordre alphabétique
        files.sort()
        directories.sort()

        # Afficher les fichiers d'abord
        for file in files:
            print(f"{indent}├── {file}")

        # Puis afficher les dossiers et leur contenu
        for i, directory in enumerate(directories):
            full_dir_path = os.path.join(directory_path, directory)

            # Si c'est le dernier répertoire, utiliser '└──' au lieu de '├──'
            if i == len(directories) - 1 and len(directories) > 0:
                print(f"{indent}└── {directory}/")
                list_directory_contents(full_dir_path, indent + "    ")
            else:
                print(f"{indent}├── {directory}/")
                list_directory_contents(full_dir_path, indent + "│   ")

    except PermissionError:
        print(f"{indent}├── [Permission refusée]")
    except Exception as e:
        print(f"{indent}├── [Erreur: {str(e)}]")


if __name__ == "__main__":
    # Utiliser le répertoire passé en argument ou le répertoire courant
    directory_to_list = sys.argv[1] if len(sys.argv) > 1 else "."

    # Obtenir la date actuelle
    now = datetime.now()
    date_string = now.strftime("%Y-%m-%d %H:%M:%S")

    # Rediriger la sortie standard vers un buffer
    import io
    buffer = io.StringIO()
    sys.stdout = buffer

    # Afficher le nom du répertoire principal
    print(f"{os.path.basename(os.path.abspath(directory_to_list))}/")

    # Lister son contenu
    list_directory_contents(directory_to_list)

    # Rétablir la sortie standard
    sys.stdout = sys.__stdout__

    # Récupérer le contenu du buffer
    output_content = buffer.getvalue()

    # Ajouter la date au début du contenu
    output_content = f"Rapport du {date_string}:\n\n{output_content}"

    # Enregistrer le contenu dans un fichier
    with open("tree.txt", "w", encoding="utf-8") as file:
        file.write(output_content)

    #_confirmation de bonne execution
    print("\nLe rapport a été enregistré dans tree.txt avec succès.")
    input("Appuyez sur une touche pour continuer...")