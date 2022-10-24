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
try:
    import sys, os
    import codecs
    import glob
    import FonctionGui as fgui

except Exception as e:
    print(e)
    input('***')

if __name__ == "__main__":
    fgui.Initialize()
    fgui.MainLoop()
