# !/usr/bin/python
# !python
# -*- coding: utf-8 -*-
"""
Created on Mon May 4 18:02:18 2020

@author : Aelurus

@contributor: Bruno

Fichier main qui lance toute la toutouille ...

Pour le numéro de version voir `FonctionSignal`, `Version`
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
    fgui.Initialize()
    fgui.MainLoop()