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
    import codecs
    import glob
    import FonctionGui as fgui

except Exception as e:
    print(e)
    print("main")
    sys.exit(1)

if __name__ == "__main__":
    # Initialize the GUI components
    fgui.Initialize()

    # Start the main event loop of the GUI
    fgui.run_main_loop()
