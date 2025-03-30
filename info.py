# info.py
"""
 * Sensorem - Documentation du module info.py

Ce module contient les informations relatives à la version du logiciel,
les notes de version et la description des modules.

nom_projet = "Analyse de signaux ECG"
description_projet = "Ce projet analyse les signaux ECG et détecte les anomalies."
auteurs = ["Aelurus", "Autre Nom"]
contributeur = [Bruno]
date_creation = "2024-06-14"

date = "19/01/2025"
version = "0.4.3.8"


__notes_de_version__ =
Pretraitement des données de raccordement de capteur (s).

Plusieurs modifications :
*   Ajout d'une base de données et de sa gestion avec insertion des capteurs a la génération d'un PDF (02/02/2025)
*   Ajout du traitement de regression avec un coefficient de conversion (19/01/2025)
*   Remise à niveau de le génération du PDF : Adaptation des fonctions au nouveau GUI (28/12/2024).
*   Refonte générale de l'interface graphique (GUI) : Implémentation fonctionnelle (25/12/2024).
*   Gestion des noms et positions des capteurs depuis l'interface graphique (GUI) : Implémentation fonctionnelle (09/12/2024).
*   Correction du seuil de détection pour le venturi : Ajustement du seuil (06/12/2024).
*   Corrections de bugs : Diverses corrections de bugs non spécifiés.
*   Nettoyage des données : Suppression des chaînes "#N/A" et "Calibration" lors de la récupération des données (18/02).
*   Amélioration des graphiques : Ajout de légendes aux graphiques dans l'interface graphique (18/02).
*   Affichage des données brutes : Affichage des valeurs des capteurs dans la fenêtre "Voici les données trouvées" (18/02).
*   Moyenne mobile : Ajout d'une moyenne mobile avec un pas de 2 avant la détection des paliers. L'ajout d'une option pour manipuler ce paramètre dans l'interface graphique est prévu (24/03/2024).

Bugs corrigés et restants :

*   Détection des paliers : Augmentation du nombre de points pour la détection des paliers (de 10 à 13) pour résoudre les problèmes rencontrés lors de certaines descentes (18/02).
*   Décalage dans les tableaux de valeurs : Correction d'un décalage dans le remplissage des tableaux de valeurs (moyenne et écart) en cas de traitement avec plusieurs capteurs, causé par des valeurs différentes dans les paliers (15/02).
*   Inversion des couleurs dans la légende PDF : Correction de l'inversion des couleurs dans la légende des mesures du rapport PDF (18/02).
*   Affichage d'un seul capteur : Correction du bug qui n'affichait qu'un seul capteur dans la fenêtre "Voici les données trouvées" (25/02).
*   Nettoyage des erreurs #DIV/! : Ajout d'un nettoyage pour les valeurs #DIV/! (25/02).
*   Perte du fichier sélectionné : Bug persistant : Lors de la validation du nom de l'utilisateur, le fichier sélectionné est perdu et le premier fichier de la liste est traité à la place.


__modules_description__ =
Récapitulatif des modules actuels et de leurs rôles :

*   `main.py` : Point d'entrée de l'application. Lance l'interface graphique.
*   `gui_V3.py` : Gère l'interface graphique, l'interaction utilisateur, l'affichage des graphiques et l'appel aux autres modules.
*   `FonctionsCSV.py` : Gère la lecture et le traitement des fichiers CSV.
*   `FonctionsSignal.py` : Contient les fonctions de traitement du signal (filtrage, détection des paliers, etc.).
*   `FonctionPdf.py` : Génère les rapports PDF.
*   `FonctionsGui_V3.py` : Fournit des fonctions utilitaires pour l'interface graphique (gestion des logs, etc.).
*   `FonctionsBD.py` : Gere la fenetre Base de données et toutes les fonctions pour la bases de données

Objectifs :

Sensorem/
│
├── main.py
├── requirements.txt
├── .env
├── README.md
├── core/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── csv_handler.py     (Refactorisation de FonctionsCSV.py)
│   │   └── database_manager.py (Refactorisation de FonctionsDB.py)
│   ├── processing/
│   │   ├── __init__.py
│   │   └── signal_processor.py (Refactorisation de FonctionsSignal.py)
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── main_window.py      (Refactorisation de gui_V3.py)
│   │   └── utils.py            (Partie de FonctionsGui_V3.py)
│   ├── reporting/
│   │   ├── __init__.py
│   │   └── pdf_generator.py    (Refactorisation de FonctionsPdf.py)
│   ├── utils/
│   │   ├── __init__.py
│   │   └── logger.py           (Partie de FonctionsGui_V3.py, gestion des logs)
│   └── tests/
│       ├── __init__.py
│       ├── test_csv_handler.py
│       ├── test_database_manager.py
│       ├── test_signal_processor.py
│       └── test_pdf_generator.py
"""

