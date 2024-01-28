# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 11:10:34 2020

@author: windows
"""
try:
    from statistics import mean, pstdev
    import csv
    import FonctionPdf as pdf
    from reportlab.graphics.charts.lineplots import LinePlot
    from reportlab.graphics.shapes import Drawing, String
    from reportlab.graphics.widgets.markers import makeMarker
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle
    from reportlab.graphics.charts.textlabels import Label
    from doctest import testmod
    from reportlab.graphics.charts.legends import Legend
    from reportlab.graphics.shapes import _DrawingEditorMixin
    # from reportlab.graphics.widgets.markers import makeMarker
    #from reportlab.graphics.charts.textlabels import Label
    from reportlab.graphics.samples.excelcolors import *

except Exception as e:
    print(e)
    input('***')
##### 1

def version():
    # definition et passage du numéro de version du traitement
    version = str(" (0.4.3 Bêta_c)")
    return version
def make_stat(values_sep_paliers,paliers_find):
    moyenne = list([""]*paliers_find)
    ecartype = [""]*paliers_find
    coeff_gen = gen_nom_paliers(paliers_find)
    for i in range(paliers_find):
        moyenne[i]= mean(values_sep_paliers[i][7 : -7])
        ecartype[i] = pstdev(values_sep_paliers[i][7 : -7])*1000
        return (i+1,str(coeff_gen[i]), str(round(len(values_sep_paliers[i]),3)),str(round(ecartype[i]/moyenne[i]/10,2)) )

def prep_donnees_graph(donnees):
    """
    retourne une liste d'éléments en listes d'éléments incrémentée,
    >>> prep_donnees_graph([1,2,3,4,5])
    [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]]
    """
    return [[i,donnee] for i, donnee in enumerate (donnees)]
######
def traitement_signal(data):
    #identification des paliers
    values_sep = sep_values(data)
    paliers_find,plage_len_find,nb_values,values_sep = info_values(values_sep)
    paliers = make_paliers(paliers_find,plage_len_find)
    values_sep_paliers = paliers_values_sep(values_sep,nb_values,paliers)
    return values_sep_paliers,data, values_sep,paliers_find

def traitement_signal2(data):
    #identification des paliers
    values_sep = sep_values2(data)
    paliers_find,plage_len_find,nb_values,values_sep = info_values(values_sep)
    paliers = make_paliers(paliers_find,plage_len_find)
    values_sep_paliers = paliers_values_sep(values_sep,nb_values,paliers)
    return values_sep_paliers,data, values_sep,paliers_find
#recuperation des valeurs à traiter
def readColCSV1( fichier , sep , n) :
    '''
    Lecture complete du fichier
    Pour les deux premiers paramètres attention à bien utiliser les guillements
    car la fonction attend des chaines de caractères.
    fichier <str> : Le nom du fichier -> "mon_fichier.csv"
    sep <str> : Le séparateur des colonnes par exemple -> ";"
    n <int> : Le numéro de la colonne à lire
    '''
    file = open(fichier, "r")
    reader = csv.reader(file , delimiter = sep)
    col = []
    for row in reader:
        #if row[n] == "Invalid": row[n]=float(0.0)
        if n < len(row) and row[n] == 'Invalid': row[n]=float(0.0)
        try:
            notation_point = row[n].replace ("," , ".")
            col.append(float(notation_point))
        except Exception as e:
            if n < len(row) and row[n] == 'Invalid': col.append(0.0)
            #print(e, n)
            #print(row[n])
            #pass
            col.append(row[n])  #la différence est içi entre readColCSV &1 y a une couille mais .....
            #input('***')
    file . close ()
    return col
def readColCSV( fichier , sep , n ) :
    """
    Pour les deux premiers paramètres attention à bien utiliser les guillements
    car la fonction attend des chaines de caractères.
    fichier <str> : Le nom du fichier -> "mon_fichier.csv"
    sep <str> : Le séparateur des colonnes par exemple -> ";"
    n <int> : Le numéro de la colonne à lire
    
    retourne les valeurs de la colone du fichier en remplacant le separateur de
    decimal de , a . si besoin. 
    Ignore les valeurs non int
    Echappe les valeurs vide de la colonne comme les fin de fichier de fin de fichier
    
    >>> readColCSV ("DebudFindeFichier.csv", ";", 2)
    [0.0154, 0.0154, 0.0154, 0.0, 0.0154, 0.0]
    """
    file = open(fichier, "r")
    reader = csv.reader(file , delimiter = sep)
    col = []
    for row in reader :
        for row in reader:
            try:
                notation_point = row[n].replace(",", ".")
                col.append(float(notation_point))
            except:
                if n < len(row) and row[n] == 'Invalid': col.append(0.0)
                pass
    file . close ()
    return col
#determination des coefficients en fonction du nombre de paliers pour la génération de paliers ascendents et descendants
def gen_nom_paliers(n):
    """
    retourne une liste incrémentée ascendant et descendant axée sur le
    milleu du nombe passé en argument
    >>> print (gen_nom_paliers(9))
    (0, 1, 2, 3, 4, 3, 2, 1, 0)
    """
    return tuple(range(int(n/2+1))) + tuple(range(int(n/2-1), -1, -1))

#Recuperation des valeurs pour detection separation des paliers avec
paliers_mark = -0.03 #Valeur pour marquer la séparation des paliers
def sep_values(sv):
    """
    Parameters
    ----------
    sv : TYPE,list
        DESCRIPTION.
        Liste de valeurs décimales, ayant la forme d'un signal carré ascendant puis descendant
        (données expérimentales).
    >>> a = [0.0015  ,0.0015 ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015 , 0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015 , 0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015 , 0.0015 , 0.0015 , 0.0015 , 0.0015 , 0.0015 , 0.0015 , 0.0206 , 0.0779 , 0.1577 , 0.1747 , 0.1769 , 0.1675 , 0.1447 , 0.1294 , 0.1219 , 0.1193 , 0.1187 , 0.1179 , 0.1174 , 0.1175 , 0.1172 , 0.1168 , 0.1169 , 0.1165 , 0.1166 , 0.1167 , 0.1168 , 0.1173 , 0.1176 , 0.1168 , 0.1176 , 0.1172 , 0.1173 , 0.1171 , 0.1165 , 0.1172 , 0.1173 , 0.1174 , 0.1172 , 0.1175 , 0.1177 , 0.1172 , 0.1173 , 0.1173 , 0.1176 , 0.1178 , 0.1173 , 0.1174 , 0.1174 , 0.1172 , 0.1173 , 0.1173 , 0.1174 , 0.1173 , 0.1169 , 0.1171 , 0.1174 , 0.1171 , 0.1172 , 0.1173 , 0.1164 , 0.1164 , 0.1165 , 0.1164 , 0.1165 , 0.1168 , 0.1171 , 0.1172 , 0.1171 , 0.1172 , 0.1177 , 0.1175 , 0.1174 , 0.1176 , 0.1173 , 0.1173 , 0.1171 , 0.1171 , 0.1168 , 0.1167 , 0.1169 , 0.1169 , 0.1169 , 0.1171 , 0.1172 , 0.1173 , 0.2008 , 0.2177 , 0.2205 , 0.2219 , 0.2236 , 0.2237 , 0.2216 , 0.2217 , 0.2216 , 0.2225 , 0.2242 , 0.2231 , 0.2226 , 0.2233 , 0.2225 , 0.2228 , 0.2239 , 0.2239 , 0.2245 , 0.2231 , 0.2228 , 0.2233 , 0.2237 , 0.2238 , 0.2232 , 0.2228 , 0.2236 , 0.3808 , 0.4189 , 0.4319 , 0.4338 , 0.4339 , 0.4307 , 0.4313 , 0.4342 , 0.4319 , 0.4332 , 0.4333 , 0.4329 , 0.4358 , 0.4366 , 0.4353 , 0.4343 , 0.4343 , 0.4337 , 0.4341 , 0.4363 , 0.4318 , 0.4319 , 0.4322 , 0.4312 , 0.4334 , 0.4333 , 0.4334 , 0.4322 , 0.4359 , 0.4337 , 0.4319 , 0.4313 , 0.4325 , 0.4317 , 0.4313 , 0.4307 , 0.4318 , 0.4283 , 0.5441 , 0.6355 , 0.6491 , 0.6531 , 0.6504 , 0.6537 , 0.6538 , 0.6546 , 0.6529 , 0.6537 , 0.6538 , 0.6539 , 0.6539 , 0.6538 , 0.6539 , 0.6539 , 0.6539 , 0.6539 , 0.6534 , 0.6538 , 0.6539 , 0.6534 , 0.6535 , 0.6534 , 0.6525 , 0.6528 , 0.6529 , 0.6554 , 0.6558 , 0.6559 , 0.5521 , 0.4593 , 0.4364 , 0.4325 , 0.4279 , 0.4299 , 0.4287 , 0.4307 , 0.4308 , 0.4309 , 0.4311 , 0.4321 , 0.4328 , 0.4282 , 0.4285 , 0.4324 , 0.4331 , 0.4317 , 0.4328 , 0.4328 , 0.4313 , 0.4332 , 0.4321 , 0.4321 , 0.4351 , 0.4287 , 0.4336 , 0.4304 , 0.4318 , 0.4275 , 0.4271 , 0.4239 , 0.4237 , 0.4054 , 0.2998 , 0.2448 , 0.2449 , 0.2193 , 0.2205 , 0.2189 , 0.2175 , 0.2191 , 0.2197 , 0.2202 , 0.2194 , 0.2189 , 0.2184 , 0.2174 , 0.2179 , 0.2180 , 0.2179 , 0.2195 , 0.2194 , 0.2187 , 0.2211 , 0.2206 , 0.2207 , 0.2212 , 0.2205 , 0.2207 , 0.2208 , 0.2206 , 0.2204 , 0.2195 , 0.2209 , 0.2210 , 0.2203 , 0.2204 , 0.2116 , 0.1881 , 0.18 , 0.1771 , 0.1754 , 0.1606 , 0.1391 , 0.1261 , 0.1209 , 0.1192 , 0.1181 , 0.1181 , 0.1182 , 0.1178 , 0.1175 , 0.1176 , 0.1167 , 0.1179 , 0.1180 , 0.1174 , 0.1174 , 0.1177 , 0.1178 , 0.1176 , 0.1178 , 0.1172 , 0.1178 , 0.1177 , 0.1184 , 0.1182 , 0.1183 , 0.1184 , 0.1181 , 0.1173 , 0.0015 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0015 , 0.0017 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0009 , 0.0010 , 0.0011 , 0.0011 , 0.0011 , 0.0012 , 0.0009 , 0.0005 , 0.0007 , 0.0007 , 0.0005 , 0.0005 , 0.0008 , 0.0008 , 0.0007 , 0.0004 , 0.0005 , 0.0004 , 0.0004 , 0.0004 , 0.0009 , 0.0008 , 0.0009 , ]

    Returns
    -------
    values_sep : TYPE, list
        DESCRIPTION.
        La liste de sortie est l'identification des paliers par le remplacement de sa première
        valeur par paliers_mark. Une première boucle nettoie le signal des valeurs aberrantes
        Dû à la mesure.
        La deuxième boucle identifie les paliers
    >>> type(sep_values(a))
    <class 'list'>

    """
    seuil = 0.052 #seuil de détection des changements de paliers
    sensibilite = 0.014 #seuil de nettoyage
    nb_values = len(sv)
    values_sep = list()#Donne brute avec identification des étages
    nb_remplacement = 1

    for i in range(nb_values-abs(nb_remplacement)-5):
        if abs(sv[i+5]-sv[i])<sensibilite:#attention le i+x (5) est à mettre en accord avec les valeurs d'exclusion des moyenne et ecartype du pdf et de l'interface graphique
            sv[i]=sv[i]
        else:
            sv[i]=sv[i-nb_remplacement]

    for i in range(nb_values-1):
        if  abs(sv[i+1]-sv[i])>seuil or abs(sv[i]-sv[i+1])>seuil:
            values_sep.append(paliers_mark)
        else:
            values_sep.append(sv[i])
    return values_sep
def sep_values2(sv):
    """
    Parameters
    ----------
    sv : TYPE,list
        DESCRIPTION.
        Liste de valeurs décimales, ayant la forme d'un signal carré ascendant puis descendant
        (données expérimentales).
    >>> a = [0.0015  ,0.0015 ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015 , 0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015 , 0.0015  ,0.0015  ,0.0015  ,0.0015  ,0.0015 , 0.0015 , 0.0015 , 0.0015 , 0.0015 , 0.0015 , 0.0015 , 0.0206 , 0.0779 , 0.1577 , 0.1747 , 0.1769 , 0.1675 , 0.1447 , 0.1294 , 0.1219 , 0.1193 , 0.1187 , 0.1179 , 0.1174 , 0.1175 , 0.1172 , 0.1168 , 0.1169 , 0.1165 , 0.1166 , 0.1167 , 0.1168 , 0.1173 , 0.1176 , 0.1168 , 0.1176 , 0.1172 , 0.1173 , 0.1171 , 0.1165 , 0.1172 , 0.1173 , 0.1174 , 0.1172 , 0.1175 , 0.1177 , 0.1172 , 0.1173 , 0.1173 , 0.1176 , 0.1178 , 0.1173 , 0.1174 , 0.1174 , 0.1172 , 0.1173 , 0.1173 , 0.1174 , 0.1173 , 0.1169 , 0.1171 , 0.1174 , 0.1171 , 0.1172 , 0.1173 , 0.1164 , 0.1164 , 0.1165 , 0.1164 , 0.1165 , 0.1168 , 0.1171 , 0.1172 , 0.1171 , 0.1172 , 0.1177 , 0.1175 , 0.1174 , 0.1176 , 0.1173 , 0.1173 , 0.1171 , 0.1171 , 0.1168 , 0.1167 , 0.1169 , 0.1169 , 0.1169 , 0.1171 , 0.1172 , 0.1173 , 0.2008 , 0.2177 , 0.2205 , 0.2219 , 0.2236 , 0.2237 , 0.2216 , 0.2217 , 0.2216 , 0.2225 , 0.2242 , 0.2231 , 0.2226 , 0.2233 , 0.2225 , 0.2228 , 0.2239 , 0.2239 , 0.2245 , 0.2231 , 0.2228 , 0.2233 , 0.2237 , 0.2238 , 0.2232 , 0.2228 , 0.2236 , 0.3808 , 0.4189 , 0.4319 , 0.4338 , 0.4339 , 0.4307 , 0.4313 , 0.4342 , 0.4319 , 0.4332 , 0.4333 , 0.4329 , 0.4358 , 0.4366 , 0.4353 , 0.4343 , 0.4343 , 0.4337 , 0.4341 , 0.4363 , 0.4318 , 0.4319 , 0.4322 , 0.4312 , 0.4334 , 0.4333 , 0.4334 , 0.4322 , 0.4359 , 0.4337 , 0.4319 , 0.4313 , 0.4325 , 0.4317 , 0.4313 , 0.4307 , 0.4318 , 0.4283 , 0.5441 , 0.6355 , 0.6491 , 0.6531 , 0.6504 , 0.6537 , 0.6538 , 0.6546 , 0.6529 , 0.6537 , 0.6538 , 0.6539 , 0.6539 , 0.6538 , 0.6539 , 0.6539 , 0.6539 , 0.6539 , 0.6534 , 0.6538 , 0.6539 , 0.6534 , 0.6535 , 0.6534 , 0.6525 , 0.6528 , 0.6529 , 0.6554 , 0.6558 , 0.6559 , 0.5521 , 0.4593 , 0.4364 , 0.4325 , 0.4279 , 0.4299 , 0.4287 , 0.4307 , 0.4308 , 0.4309 , 0.4311 , 0.4321 , 0.4328 , 0.4282 , 0.4285 , 0.4324 , 0.4331 , 0.4317 , 0.4328 , 0.4328 , 0.4313 , 0.4332 , 0.4321 , 0.4321 , 0.4351 , 0.4287 , 0.4336 , 0.4304 , 0.4318 , 0.4275 , 0.4271 , 0.4239 , 0.4237 , 0.4054 , 0.2998 , 0.2448 , 0.2449 , 0.2193 , 0.2205 , 0.2189 , 0.2175 , 0.2191 , 0.2197 , 0.2202 , 0.2194 , 0.2189 , 0.2184 , 0.2174 , 0.2179 , 0.2180 , 0.2179 , 0.2195 , 0.2194 , 0.2187 , 0.2211 , 0.2206 , 0.2207 , 0.2212 , 0.2205 , 0.2207 , 0.2208 , 0.2206 , 0.2204 , 0.2195 , 0.2209 , 0.2210 , 0.2203 , 0.2204 , 0.2116 , 0.1881 , 0.18 , 0.1771 , 0.1754 , 0.1606 , 0.1391 , 0.1261 , 0.1209 , 0.1192 , 0.1181 , 0.1181 , 0.1182 , 0.1178 , 0.1175 , 0.1176 , 0.1167 , 0.1179 , 0.1180 , 0.1174 , 0.1174 , 0.1177 , 0.1178 , 0.1176 , 0.1178 , 0.1172 , 0.1178 , 0.1177 , 0.1184 , 0.1182 , 0.1183 , 0.1184 , 0.1181 , 0.1173 , 0.0015 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0015 , 0.0017 , 0.0014 , 0.0014 , 0.0014 , 0.0014 , 0.0009 , 0.0010 , 0.0011 , 0.0011 , 0.0011 , 0.0012 , 0.0009 , 0.0005 , 0.0007 , 0.0007 , 0.0005 , 0.0005 , 0.0008 , 0.0008 , 0.0007 , 0.0004 , 0.0005 , 0.0004 , 0.0004 , 0.0004 , 0.0009 , 0.0008 , 0.0009 , ]

    Returns
    -------
    values_sep : TYPE, list
        DESCRIPTION. Pour le traitement d'un type de capteur (Mac Soufflerie)
        La liste de sortie est l'identification des paliers par le remplacement de sa première
        valeur par paliers_mark. Une première boucle nettoie le signal des valeurs aberrantes
        Dû à la mesure.
        La deuxième boucle identifie les paliers
    >>> type(sep_values(a))
    <class 'list'>

    """
    seuil = 0.5 #seuil de détection des changements de paliers
    sensibilite = 0.21 #seuil de nettoyage
    nb_values = len(sv)
    values_sep = list()#Donne brute avec identification des étages
    nb_remplacement = 1

    for i in range(nb_values-abs(nb_remplacement)-5):
        if abs(sv[i+5]-sv[i])<sensibilite:#attention le i+x (5) est à mettre en accord avec les valeurs d'exclusion des moyenne et ecartype du pdf et de l'interface graphique
            sv[i]=sv[i]
        else:
            sv[i]=sv[i-nb_remplacement]

    for i in range(nb_values-1):
        if  abs(sv[i+1]-sv[i])>seuil or abs(sv[i]-sv[i+1])>seuil:
            values_sep.append(paliers_mark)
        else:
            values_sep.append(sv[i])
    return values_sep
#Recuperation des valeurs generer avec separation par etages
def info_values(iv):
    nb_values = len(iv)
    values_sep = list([0]*nb_values)#Donne brute avec identification des étages
    paliers_find=1
    plage_len_find= list()
    count=1
    for i in range(nb_values):
        if iv[i]== paliers_mark:
            values_sep[i]= paliers_mark
            paliers_find = paliers_find +1
            plage_len_find.append(count)
            count=1
        else:
            values_sep[i]=iv[i]
            if i==(nb_values-1):
                plage_len_find.append(count)
            count = count +1
    return[paliers_find,plage_len_find,nb_values,values_sep]

#creation de la liste du nombre de paliers avec la taille
def make_paliers(paliers_find,plage_len_find):
    paliers = list([0]*paliers_find)
    for i in range(len(paliers)):
        paliers[i] = list([0]*plage_len_find[i])
    return paliers
#Passage de données separer, en liste des tableaux remplis
def paliers_values_sep(values_sep,nb_values,paliers):
    count=0
    nb=0
    values_paliers = paliers
    for i in range(nb_values):
        if values_sep[i]== paliers_mark:
            values_paliers[count][nb]=values_sep[i-1]
            count=count+1
            nb=0
        else:
            values_paliers[count][nb]=values_sep[i]
            nb=nb+1
    return values_paliers
#génération du tableau pour insertion dans le pdf
def myTable(tabledata):
    t = Table(tabledata,rowHeights=(10))
    GRID_STYLE = TableStyle([
    ('INNERGRID', (0,0), (-1,-1), 0.25, colors.darkgrey),
    ('BOX', (0,0), (-1,0), 0.25, colors.black),
    ('BACKGROUND',(0,0),(4,0),colors.lightgrey),
    ('ALIGN', (0, 1), (-1, -1), "CENTER"),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('TEXTFONT', (0, 0), (-1, -1), 'Times-Bold')
    ])
    t.setStyle(GRID_STYLE)
    t.hAlign=1
    return t
#tracer des graph dans le PDF, GROS bordel ^^....
def trace_graph(title, data, w, h, data2=[[(0,0)]], xtitle='Nombre de mesures',
                xtvisi=1, ytitle='Tension [V]', y2title='Capteur réf', ForceXzero= 1):
    graph = Drawing(w, h)
    # print(data)
    chart = LinePlot()
    chart.y                = 12
    chart.x                = 12
    chart.width            = w-6
    chart.height           = h-30
    #fontName = 'Helvetica'
    fontSize = 10
    graph.add(Label(),name='XLabel')
    graph.XLabel.fontName = 'Times-Roman'
    graph.XLabel.fontSize = fontSize-1
    graph.XLabel.x = w/2
    graph.XLabel.y = -7
    if xtvisi==1 :
        graph.XLabel._text = xtitle
    else:
        graph.XLabel._text = ''
    graph.add(Label(),name='YLabel')
    graph.YLabel.fontSize = fontSize-2
    graph.YLabel.x = -17
    graph.YLabel.y = h/2
    graph.YLabel.angle = 90
    graph.YLabel.textAnchor ='middle'
    graph.YLabel._text = ytitle
    #chart.lineLabels.fontSize           = fontSize
    chart.lineLabels.boxStrokeWidth     = 0.3
    #chart.lineLabels.visible            = 1
    chart.lineLabels.boxAnchor          = 'c'
    chart.lineLabels.angle              = 0
    chart.lineLabelNudge                = 10
    chart.joinedLines                   = 1
    chart.lines.strokeWidth             = 0.5
    # line styles
    chart.lines[0].strokeColor = colors.darkcyan
    chart.lines[0].symbol = makeMarker(None)
    chart.lines[0].symbol.size        = 2
    chart.lines[0].symbol.angle       = 15
    chart.lines[1].strokeColor = colors.darkorange
    chart.lines[1].symbol = makeMarker(None)
    chart.lines[1].symbol.size        = 2
    chart.lines[1].symbol.angle       = 15
    chart.lines[2].strokeColor = colors.blueviolet
    chart.lines[2].symbol = makeMarker(None)
    chart.lines[2].symbol.size        = 3
    chart.lines[2].symbol.angle       = 15
    chart.lines[3].strokeColor = colors.darkslategrey
    chart.lines[3].symbol = makeMarker(None)
    chart.lines[3].symbol.size        = 2
    chart.lines[3].symbol.angle       = 15
    chart.lines[4].strokeColor = colors.antiquewhite
    chart.lines[4].symbol = makeMarker(None)
    chart.lines[4].symbol.size        = 2
    chart.lines[4].symbol.angle       = 15
    chart.lines[5].strokeColor = colors.darkslategray
    chart.lines[5].symbol = makeMarker(None)
    chart.lines[5].symbol.size        = 2
    chart.lines[5].symbol.angle       = 15
    chart.lines[6].strokeColor = colors.darkolivegreen
    chart.lines[6].symbol = makeMarker(None)
    chart.lines[6].symbol.size        = 2
    chart.lines[6].symbol.angle       = 15
    chart.lines[7].strokeColor = colors.bisque
    chart.lines[7].symbol = makeMarker(None)
    chart.lines[7].symbol.size        = 2
    chart.lines[7].symbol.angle       = 15
    chart.lines[8].strokeColor = colors.aquamarine
    chart.lines[8].symbol = makeMarker(None)
    chart.lines[8].symbol.size        = 2
    chart.lines[8].symbol.angle       = 15
    chart.lines.strokeWidth     = 0.5
    chart.lines.symbol= makeMarker(None)
    # x axis
    chart.xValueAxis.visibleAxis           = 1
    chart.xValueAxis.visibleGrid           = 1
    chart.xValueAxis.gridStrokeWidth       = 0.15
    chart.xValueAxis.gridStrokeColor       = colors.darkgrey
    #chart.xValueAxis.labels.fontName       = fontName
    chart.xValueAxis.labels.fontSize       = fontSize-2
    chart.xValueAxis.labels.boxAnchor      ='autox'
    chart.xValueAxis.maximumTicks          = 10
    chart.xValueAxis.minimumTickSpacing    = 0.5
    chart.xValueAxis.tickDown              = 2.5
    chart.xValueAxis.visibleSubTicks       = 1
    chart.xValueAxis.subTickHi             = 0
    chart.xValueAxis.subTickLo             = 1
    chart.xValueAxis.subTickNum            = 1
    chart.xValueAxis.subTickNum            = 1
    chart.xValueAxis.strokeWidth           = 0.45
    chart.xValueAxis.avoidBoundFrac = 0.1
    chart.xValueAxis.forceZero             = ForceXzero
    # y axis
    chart.yValueAxis.visibleGrid           = 1
    chart.yValueAxis.gridStrokeWidth       = 0.15
    chart.yValueAxis.gridStrokeColor       = colors.darkgrey
    chart.yValueAxis.visibleAxis           = 1
    #chart.yValueAxis.labels.fontName       = fontName
    chart.yValueAxis.labels.fontSize       = fontSize -2
    #chart.yValueAxis.labelTextFormat       = '%0.1f'
    chart.yValueAxis.strokeWidth           = 0.45
    chart.yValueAxis.visible               = 1
    chart.yValueAxis.labels.rightPadding   = 2
    chart.yValueAxis.rangeRound            ='both'
    chart.yValueAxis.tickLeft              = 2.5
    chart.yValueAxis.minimumTickSpacing    = 8
    chart.yValueAxis.maximumTicks          = 10
    chart.yValueAxis.visibleSubTicks       = 1
    chart.yValueAxis.subTickHi             = 0
    chart.yValueAxis.subTickLo             = 1
    chart.yValueAxis.subTickNum            = 1
    chart.yValueAxis.forceZero             = ForceXzero
    chart.yValueAxis.avoidBoundFrac        = 0.1
    graph.add(String(((w/2)-len(title)*2),h-14,'text'),name='title')
    graph.title.text       = title
    graph.title.fontSize   = fontSize -2
    chart.data  = data
    graph.add(chart)
    # y2 axis
    # data2 = data
    if not data2 or data2 == [[(0,0)]]:
        return graph
    else:#pour un éventuel tracer avec deux courbes
        chart2 = LinePlot()
        chart.y                = 12
        chart.x                = 12
        chart.width            = w-6
        chart.height           = h-30        
        # x axis
        chart2.xValueAxis.visibleAxis           = 0
        chart2.xValueAxis.visibleGrid           = 0
        chart2.xValueAxis.gridStrokeWidth       = 0.15
        chart2.xValueAxis.gridStrokeColor       = colors.darkgrey
        #chart2.xValueAxis.labels.fontName       = fontName
        chart2.xValueAxis.labels.fontSize       = 0#fontSize-2
        chart2.xValueAxis.labels.boxAnchor      ='autox'
        chart2.xValueAxis.maximumTicks          = 10
        chart2.xValueAxis.minimumTickSpacing    = 0.5
        chart2.xValueAxis.tickDown              = 2.5
        chart2.xValueAxis.visibleSubTicks       = 1
        chart2.xValueAxis.subTickHi             = 0
        chart2.xValueAxis.subTickLo             = 1
        chart2.xValueAxis.subTickNum            = 1
        chart2.xValueAxis.subTickNum            = 1
        chart2.xValueAxis.strokeWidth           = 0.45
        chart2.xValueAxis.forceZero             = ForceXzero
        chart2.data = data2
        chart2.xValueAxis.visible           = 1
        #
        #chart2.yTitleText           = y2title
        chart2.yValueAxis.setPosition(50, 50, 125)
        chart2.yValueAxis.joinAxisMode = 'right'
        chart2.yValueAxis.visibleGrid           = 0
        chart2.yValueAxis.gridStrokeWidth       = 0.15
        chart2.yValueAxis.gridStrokeColor       = colors.darkgrey
        chart2.yValueAxis.visibleAxis           = 0
        chart2.yValueAxis.labels.fontSize       = fontSize -2
        chart2.yValueAxis.labels.textAnchor = 'start'
        chart2.yValueAxis.labels.boxAnchor = 'w'
        chart2.yValueAxis.labels.angle = 0
        chart2.yValueAxis.labels.dx = 5
        chart2.yValueAxis.labels.dy = 0
        chart2.yValueAxis.strokeWidth           = 0.45
        chart2.yValueAxis.labels.rightPadding   = 2
        chart2.yValueAxis.rangeRound            ='both'
        chart2.yValueAxis.tickLeft             = -2.5
        chart2.yValueAxis.minimumTickSpacing    = 8
        chart2.yValueAxis.maximumTicks          = 10
        chart2.yValueAxis.visibleSubTicks       = 1
        chart2.yValueAxis.subTickHi             = 0
        chart2.yValueAxis.subTickLo             = -1
        chart2.yValueAxis.subTickNum            = 1
        chart2.yValueAxis.forceZero             = ForceXzero
        chart2.yValueAxis.avoidBoundFrac        = 0.1
        graph.add(chart2)
        return graph
#Retour une liste des données des capteurs en sous list de données par capteurs
def isol_capteurs(values):
    del values [0:23]
    last_key = None
    values_capteurs = dict()
    for value in values:
        if value == 'Invalid':
            value = 0.01
        if isinstance(value, str):
            values_capteurs[value] = list()
            last_key = value
        elif last_key:
            values_capteurs[last_key].append(value)
        else:
            raise KeyError("error in the first item")
    return(values_capteurs)#retourne un dic des nom de capteur avec les valeurs
#génération des pdf par capteurs isolés
def trait_valuescapteurs(values_capteurs, nom_fichier, nom_utilisateur, values_capteurs2):
    for capteur, capteur2 in zip(values_capteurs.keys(), values_capteurs2.keys()):
        numcapteur = capteur
        numcapteur2 = capteur2
        values = values_capteurs.get(capteur)
        values2 = values_capteurs2.get(capteur2)
        pdf.gen_pdf(values,numcapteur,nom_fichier,nom_utilisateur, values2, numcapteur2)
#Initialisation du post traitement du fichier de données
def pre_traitement(nom_fichier,nom_utilisateur, colonne1, colonne2):
    #values = list()
    values = readColCSV1(nom_fichier,";",colonne1)
    values_capteurs = isol_capteurs(values)

    values2 = readColCSV1(nom_fichier,";",colonne2)
    values_capteurs2 = isol_capteurs(values2)
    #print (values_capteurs2)
    trait_valuescapteurs(values_capteurs,nom_fichier,nom_utilisateur,values_capteurs2)
    
class LineChartWithMarkers(_DrawingEditorMixin, Drawing):
    def __init__(self,
                 titre_graph='Un titre de graphique',
                 data=[[(0,0)]],
                 width=215,
                 height=115,
                 data2=[[(0,0)]],
                 xtvisi=0,
                 xtitle='Nombre de mesures',
                 ytitle='Tension [V]',
                 y2title='Capteur Réf',
                 nomCapteur1 = 'Capteur raccordé',
                 nomCapteur2 = 'Capteur référence',
                 *args, **kw):

        Drawing.__init__(self, width, height, *args, **kw)
        fontSize = 10
        self._add(self, LinePlot(), name='chart', validate=None, desc="The main chart")
        self.chart.data = data # [((0., 0.491), (1., 0.149), (2., 0.3498), (4., 0.2335))]
        # self.background = Rect(0, 0, self.width, self.height, strokeWidth=0, fillColor=PCMYKColor(0,0,10,0))
        self.chart.width = width - 80
        self.chart.height = height - 60
        self.chart.x = 40
        self.chart.y = 35

        self.chart.lines.strokeWidth = 0.5

        # premier graph
        self.chart.lines[0].strokeColor = color01
        self.chart.lines[1].strokeColor = color02
        self.chart.lines[2].strokeColor = color03
        self.chart.lines[3].strokeColor = color04
        self.chart.lines[4].strokeColor = color05
        self.chart.lines[5].strokeColor = color06
        self.chart.lines[6].strokeColor = color07
        self.chart.lines[7].strokeColor = color08
        self.chart.lines[8].strokeColor = color09
        self.chart.lines[9].strokeColor = color10
        # deuxieme graph

        """
        self.chart.lines[0].symbol = makeMarker('FilledSquare')
        self.chart.lines[1].symbol = makeMarker('FilledDiamond')
        self.chart.lines[2].symbol = makeMarker('FilledStarFive')
        self.chart.lines[3].symbol = makeMarker('FilledTriangle')
        self.chart.lines[4].symbol = makeMarker('FilledCircle')
        self.chart.lines[5].symbol = makeMarker('FilledPentagon')
        self.chart.lines[6].symbol = makeMarker('FilledStarSix')
        self.chart.lines[7].symbol = makeMarker('FilledHeptagon')
        self.chart.lines[8].symbol = makeMarker('FilledOctagon')
        self.chart.lines[9].symbol = makeMarker('FilledCross')
        """
        #self.chart.fillColor = colors.ivory
        # self.chart.lineLabels.fontName              = 'Helvetica'
        self.chart.yValueAxis.tickLeft = 3
        # self.chart.yValueAxis.labels.fontName       = 'Helvetica'
        self.chart.yValueAxis.labels.fontSize = fontSize - 2
        self._add(self, Label(), name='Title', validate=None, desc="The title at the top of the chart")
        # self.Title.fontName = 'Helvetica-Bold'
        self.Title.fontSize = fontSize - 1
        self.Title.x = (width / 2) - len(self.Title._text) / 2
        self.Title.y = height - 25
        self.Title._text = titre_graph
        self.Title.maxWidth = 180
        self.Title.height = 35
        self.Title.textAnchor = 'middle'

        # Axe des X
        self._add(self, Label(), name='XLabel', validate=None, desc="The label on the horizontal axis")
        # self.XLabel.fontName       = 'Helvetica'
        self.XLabel.fontSize = fontSize - 2
        self.XLabel.x = width / 2
        self.XLabel.y = 12
        self.XLabel.textAnchor = 'middle'
        # position x et y du titre des axes X
        self.XLabel.maxWidth = 100
        self.XLabel.height = 10
        if xtvisi == 1:
            self.XLabel._text = xtitle
        else:
            self.XLabel._text = ''
        # self.chart.xValueAxis.labels.fontName       = 'Helvetica'
        self.chart.xValueAxis.labels.fontSize = fontSize - 2

        self.chart.xValueAxis.gridStrokeWidth = 0.15
        self.chart.xValueAxis.gridStrokeColor = colors.darkgrey
        self.chart.xValueAxis.minimumTickSpacing = 8
        self.chart.xValueAxis.maximumTicks = 10
        self.chart.xValueAxis.visibleSubTicks = 1
        self.chart.xValueAxis.subTickHi = 0
        self.chart.xValueAxis.subTickLo = 2
        self.chart.xValueAxis.subTickNum = 1
        self.chart.xValueAxis.strokeWidth = 0.45
        self.chart.xValueAxis.forceZero = 1
        self.chart.xValueAxis.avoidBoundFrac = None
        # self.chart.xValueAxis.gridEnd = 175
        self.chart.xValueAxis.tickDown = 3
        self.chart.xValueAxis.visibleGrid = 1
        self.chart.xValueAxis.visible = 1
        # Axe des Y
        self._add(self, Label(), name='YLabel', validate=None, desc="The label on the vertical1 axis")
        # self.YLabel.fontName       = 'Helvetica'
        self.YLabel.fontSize = fontSize - 2
        self.YLabel.x = 22
        self.YLabel.y = height / 2
        self.YLabel.angle = 90
        self.YLabel.textAnchor = 'middle'
        self.YLabel.maxWidth = 100
        self.YLabel.height = 20
        self.YLabel._text = ytitle
        #
        self.chart.yValueAxis.visibleGrid = 1
        self.chart.yValueAxis.gridStrokeWidth = 0.15
        self.chart.yValueAxis.gridStrokeColor = colors.darkgrey
        self.chart.yValueAxis.visibleAxis = 1
        self.chart.yValueAxis.labels.textAnchor = 'start'
        self.chart.yValueAxis.labels.boxAnchor = 'e'
        self.chart.yValueAxis.labels.angle = 0
        self.chart.yValueAxis.labels.dx = -3
        self.chart.yValueAxis.labels.dy = 0

        self.chart.yValueAxis.strokeWidth = 0.45
        self.chart.yValueAxis.visible = 1
        self.chart.yValueAxis.labels.rightPadding = 2
        self.chart.yValueAxis.rangeRound = 'both'
        self.chart.yValueAxis.tickLeft = self.chart.yValueAxis.tickLeft
        self.chart.yValueAxis.minimumTickSpacing = 8
        self.chart.yValueAxis.maximumTicks = 10
        self.chart.yValueAxis.visibleSubTicks = 1
        self.chart.yValueAxis.subTickHi = 0
        self.chart.yValueAxis.subTickLo = 1
        self.chart.yValueAxis.subTickNum = 1
        self.chart.yValueAxis.forceZero = 1
        self.chart.yValueAxis.avoidBoundFrac = None

        #self.Legend.colorNamePairs = Auto(chart=self.plot)
        if not data2 or data2 == [[(0, 0)]]:
            self._add(self, 0, name='preview', validate=None, desc=None)
        else:  # pour un éventuel tracer avec deux courbes
            # self.chart2.data = [[(0,0)]]
            # self.chart2.yValueAxis.setPosition(50, 50, 125)
            self._add(self, LinePlot(), name='chart2', validate=None, desc="The main chart2")
            self.chart2.data = data2  # [((0., 0.491), (1., 0.249), (2., 0.3498), (4., 0.2335))]
            self.chart2.lines[0].strokeColor = color11 = colors.darkcyan
            self.chart2.lines[1].strokeColor = color12 = colors.darkorange
            self.chart2.lines[2].strokeColor = color13 = colors.blueviolet
            self.chart2.lines[3].strokeColor = color14 = colors.darkslategrey
            self.chart2.lines[4].strokeColor = color15 = colors.antiquewhite
            self.chart2.lines[5].strokeColor = color16 = colors.darkslategray
            self.chart2.lines[6].strokeColor = color17 = colors.darkolivegreen
            self.chart2.lines[7].strokeColor = color18 = colors.bisque
            self.chart2.lines[8].strokeColor = color19 = colors.aquamarine
            self.chart2.lines[9].strokeColor = color20 = colors.red

            self.chart2.lines.strokeWidth = 0.5
            self.chart2.yValueAxis.tickLeft = 3
            self.chart2.width = self.chart.width
            self.chart2.height = self.chart.height
            self.chart2.x = self.chart.x
            self.chart2.y = self.chart.y
            self.chart2.yValueAxis.joinAxisMode = 'right'
            # y2 axis
            self.chart2.yValueAxis.labels.fontSize = fontSize - 3
            self.chart2.yValueAxis.visibleGrid = 0
            self.chart2.yValueAxis.gridStrokeWidth = 0.15
            self.chart2.yValueAxis.gridStrokeColor = colors.darkgrey
            self.chart2.yValueAxis.visibleAxis = 1
            self.chart2.yValueAxis.labels.textAnchor = 'start'
            self.chart2.yValueAxis.labels.boxAnchor = 'w'
            self.chart2.yValueAxis.labels.angle = 0
            self.chart2.yValueAxis.labels.dx = 5
            self.chart2.yValueAxis.labels.dy = 0
            self.chart2.yValueAxis.labels.fontSize = fontSize - 2
            self.chart2.yValueAxis.strokeWidth = 0.45
            self.chart2.yValueAxis.visible = 1
            self.chart2.yValueAxis.labels.rightPadding = 2
            self.chart2.yValueAxis.rangeRound = 'both'
            # self.chart2.yValueAxis.tickLeft             = -self.chart.yValueAxis.tickLeft
            self.chart2.yValueAxis.minimumTickSpacing = 8
            self.chart2.yValueAxis.maximumTicks = 10
            self.chart2.yValueAxis.visibleSubTicks = 1
            self.chart2.yValueAxis.subTickHi = 0
            self.chart2.yValueAxis.subTickLo = 1
            self.chart2.yValueAxis.subTickNum = 1
            self.chart2.yValueAxis.forceZero = 1
            self.chart2.yValueAxis.avoidBoundFrac = None
            self._add(self, Label(), name='YLabel', validate=None, desc="The label on the vertical2 axis")
            # self.YLabel.fontName       = 'Helvetica'
            self.YLabel.fontSize = fontSize - 3
            self.chart.yValueAxis.labels.fontSize = fontSize - 3
            self.YLabel.x = width - 10
            self.YLabel.y = height / 2
            self.YLabel.angle = 90
            self.YLabel.textAnchor = 'middle'
            self.YLabel.maxWidth = 100
            self.YLabel.height = 20
            self.YLabel._text = y2title

            #
            self.chart2.xValueAxis.gridStrokeWidth = 0.15
            self.chart2.xValueAxis.gridStrokeColor = colors.darkgrey
            self.chart2.xValueAxis.minimumTickSpacing = 8
            self.chart2.xValueAxis.maximumTicks = 10
            self.chart2.xValueAxis.visibleSubTicks = 1
            self.chart2.xValueAxis.subTickHi = 1
            self.chart2.xValueAxis.subTickLo = 1
            self.chart2.xValueAxis.subTickNum = 1
            self.chart2.xValueAxis.strokeWidth = 0.45
            self.chart2.xValueAxis.forceZero = 1
            self.chart2.xValueAxis.avoidBoundFrac = None
            self.chart2.xValueAxis.gridEnd = 175
            self.chart2.xValueAxis.tickDown = 3
            self.chart2.xValueAxis.visibleGrid = 0
            self.chart2.xValueAxis.visible = 0
            # legende
            self._add(self, Legend(), name='Legend', validate=None, desc="The legend or key for the chart")
            # self.Legend.colorNamePairs = [(color01, 'Widgets')]
            # self.Legend.fontName       = 'Helvetica'
            self.Legend.fontSize = fontSize - 3
            self.Legend.x = 55
            self.Legend.y = 3
            self.Legend.dxTextSpace = 5
            self.Legend.dy = 5
            self.Legend.dx = 5
            self.Legend.deltay = 5
            self.Legend.alignment = 'right'
            self.Legend.columnMaximum = 1
            self.Legend.colorNamePairs = [(color01, nomCapteur1), (color11, nomCapteur2)]
        return self._add(self, 0, name='preview', validate=None, desc=None)

if __name__=="__main__":
    testmod()
