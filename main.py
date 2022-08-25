# !/usr/bin/python
# !python
# -*- coding: utf-8 -*-
"""
Created on Mon May 4 18:02:18 2020
@author : Aelurus
@contributor: Bruno

Il faut sortir les fonctions du 'main.py' et les appeler depuis le fichier FonctionGui,
mais je rencontre plein de bug en faisant la manip, quelque chose m'échappe. Mais super bruno à la soluce...

"""
try:
    import sys,os
    import codecs
    import glob
    
    import FonctionGui as fgui

except Exception as e:
    print(e)
    input('***')

print('coucou')

fgui.Initialize()
fgui.MainLoop()