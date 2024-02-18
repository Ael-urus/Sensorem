# !/usr/bin/python
# !python
# -*- coding: utf-8 -*-
"""
Main script that launches the application.

Created on Mon May 4 18:02:18 2020

@author: Aelurus

@contributor: Bruno

For the version number, refer to `FonctionSignal`, `Version`.
"""
# Main.py

try:
    import sys
    import os
    import codecs
    import glob
    import FonctionGui as fgui

except ImportError as import_error:
    module_name = import_error.name if hasattr(import_error, 'name') else None
    print(f"Erreur d'importation dans le module {module_name}: {import_error}")
    print(f"Fichier en cours d'exécution : {os.path.basename(__file__)}")
    input('Appuyez sur Entrée pour continuer...')
    sys.exit(1)
except Exception as e:
    print(f"Une exception s'est produite dans le module {__name__}: {e}")
    print(f"Fichier en cours d'exécution : {os.path.basename(__file__)}")
    input('Appuyez sur Entrée pour continuer...')
    sys.exit(1)

if __name__ == "__main__":
    # Initialize the GUI components
    fgui.Initialize()

    # Start the main event loop of the GUI
    fgui.run_main_loop()
