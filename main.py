# !/usr/bin/python
# !python
# -*- coding: utf-8 -*-
"""
Created on Mon May 4 18:02:18 2020

@author : Aelurus

@contributor: Bruno

Fichier main qui lance toute la toutouille ...
"""
try:
    import sys,os
    import codecs
    import glob
    
    import FonctionGui as fgui

except Exception as e:
    print(e)
    input('***')

fgui.Initialize()
fgui.MainLoop()