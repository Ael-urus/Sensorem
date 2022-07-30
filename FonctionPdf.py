# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 19:21:41 2020
@author: windows
"""
try:
    #import numpy as np
    from statistics import mean, pstdev
    import FonctionsSignal as fs
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, Spacer, SimpleDocTemplate, Table, Image,TableStyle
    #from reportlab.graphics.charts.legends import Legend
    #from reportlab.graphics.charts.lineplots import LinePlot
    #from reportlab.graphics.shapes import Drawing, _DrawingEditorMixin, String, Rect
    #from reportlab.graphics.widgets.markers import makeMarker
    #from reportlab.graphics.charts.textlabels import Label
    #from reportlab.graphics.samples.excelcolors import *
    #from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from datetime import date
    from reportlab.lib.units import cm
    from pathlib import Path
    #import matplotlib.pyplot as plt
except Exception as e:
    print(e)
    input('***')

##
def gen_pdf(data1,numcapteur,fichier,nom_utilisateur, data2, numcapteur2):
    #dat = data1
    fichier = Path(fichier).stem+".csv" #netoyage du chemin du nom de fichier et rajout de l'extension
#
###
    styles = getSampleStyleSheet()
    #styleT = styles['Title']
    #styleH1 = styles['Heading1']
    #styleH2 = styles['Heading2']
    styleH3 = styles['Heading3']
    styleH4 = styles['Heading4']
    styleN = styles['Normal']
###
    contenue    = []
    today = date.today()
    d1 = today.strftime("%d/%m/%Y")
    logo = "Logo.jpg"
    im = Image(logo, 3.5*cm, 2*cm)
    text="Prétraitement pour le raccordement <br/>du capteur <u>"+str(numcapteur)+"</u>"
    titre = Paragraph(text, styleH3)
    c_droite = "&nbsp; &nbsp; &nbsp; "+d1+"<br/>&nbsp; &nbsp; &nbsp; "+fs.version()
    c_droite = Paragraph(c_droite, styleN)
    t=Table([[im,titre,'','',c_droite]])
    t.setStyle(TableStyle([
        ('VALIGN',(0,0),(4,0),'MIDDLE'),
        ('SPAN',(1,0),(3,0)),
        ('ALIGN',(0,0),(-1,0),'RIGHT')
        ]))
 ###
    contenue.append(t)
    #recup des données brute perdu dans le traitement???
    # et passage en liste des valeurs
    w = 270
    h = 150
    mesure_brute = fs.LineChartWithMarkers('Mesures brutes', [fs.prep_donnees_graph(data1)], w, h, [fs.prep_donnees_graph(data2)], 1,
                                           'Nombre de mesures' ,  'Tension [V]', numcapteur2)
    #mais ici sinon ecrasement de dat???? Soucis à corriger##################################################################
    values_sep_paliers,values, values_sep,paliers_find = fs.traitement_signal(data1)
    values_sep_paliers2, values2, values_sep2, paliers_find2 = fs.traitement_signal2(data2)
    ################################
    #Quelques calcules sur les paliers
    #################################
    contenue.append(Paragraph("Traitement des mesures", styleH4))
    contenue.append(Paragraph("Fichier de données : ("+fichier
                              +"), traité par "+nom_utilisateur
                              +", pour le raccordement du capteur "+str(numcapteur)
                              +".<br/><u>Merci de ne pas les utiliser sans une vérification minimale</u>.<br/>",
                              styleN))
    contenue.append(Spacer(1, .1*cm))
    ###################
    ##Le tableau du traitement
    moyenne = list([""]*paliers_find)
    moyenne2 = list([""] * paliers_find2)
    ecartype = list([""]*paliers_find)
    ecartype2 = list([""] * paliers_find2)
    #tab 1
    # entete1 = [("Nb paliers","asc/desc","Nb de valeurs/palier","Incertitude ± [%]")]
    entete1 = [("Nb paliers", "asc/desc", "Nb de valeurs/palier")]
    donneestraitees1 = [["0"]*len(entete1)]*paliers_find
    #
    coeff_gen = fs.gen_nom_paliers(paliers_find)

    for i in range(paliers_find):
        moyenne[i]= mean(values_sep_paliers[i][7 : -7])
        ecartype[i] = pstdev(values_sep_paliers[i][7 : -7])*1000
        # donneestraitees1[i] = (i+1,str(coeff_gen[i]), str(round(len(values_sep_paliers[i]),3)),str(round(ecartype[i]/moyenne[i]/10,2)) )
        donneestraitees1[i] = (i + 1, str(coeff_gen[i]), str(round(len(values_sep_paliers[i]), 3)))

    #donneestraitees1 = fs.make_stat(values_sep_paliers,paliers_find)
    #Tab2
    entete2 = [("Moyenne C_r [V]","Ecart-type C_r [mV]","Moyenne C_ref","Ecart-type C_ref" )]
    donneestraitees2 = [["0"]*len(entete2)]*paliers_find
    #

    if len(range(paliers_find)) == len(range(paliers_find2)) :
        for i,j in zip(range(paliers_find),range(paliers_find2)):
            values = values_sep_paliers[i][7 : -7]#Correction, supression des valeurs de début et de fin pour les traitements.
            moyenne[i] = mean(values)
            ecartype[i] = pstdev(values) * 1000

            if values_sep_paliers2[i][7: -7]:
                values2 = values_sep_paliers2[i][7: -7]
                moyenne2[j] = mean(values2)
                ecartype2[j] = pstdev(values2)
            else:
                moyenne2[j] = 0
                ecartype2[j] = 0
            donneestraitees2[i] = (str(round(moyenne[j],4)),str(round(ecartype2[i],4)), str(round(moyenne2[i],4)),str(round(ecartype[j],4)))
            #Attention il y a une inversion, un mauvais attribuation des valeurs ecartype 2 correspond au premier capteur ?
    else :
        for i in range(paliers_find):
            values = values_sep_paliers[i][7 : -7]#Correction, supression des valeurs de début et de fin pour les traitements.
            moyenne[i] = mean(values)
            #values2 = values_sep_paliers2[i][7: -7]
            #moyenne2[j] = mean(values2)
            ecartype[i] = pstdev(values)*1000
            #ecartype2[j] = pstdev(values)
            donneestraitees2[i] = ('Oups', str(round(moyenne[i],4)),str(round(ecartype[i],4)),"Oups")

    #le tableau
    datat1 = entete1+donneestraitees1
    datat2 = entete2+donneestraitees2
    #affichage de deux tableaux cote cote pour simplifier le copier coller des données utile
    contenue.append(Table([[fs.myTable(datat1), fs.myTable(datat2)]]))
#############
    contenue.append(Paragraph("Contrôle de la mesure", styleH4))
    contenue.append(Paragraph("Représentations graphiques des données brutes, puis isolées et corrigées du pré-traitement.", styleN))
    contenue.append(Spacer(1, .1*cm))
    contenue.append(Paragraph("<u>Identification des paliers</u>", styleN))
    #tracé de la mesure
    mesure_sep = fs.LineChartWithMarkers('Mesures corrigées avec identification des paliers', [fs.prep_donnees_graph(values_sep)],
                                w, h,[fs.prep_donnees_graph(values_sep2)], 1,'Nombre de mesures' ,  'Tension [V]', numcapteur2)
    #affichage de deux graphiques cote cote
    contenue.append(Table([[mesure_brute, mesure_sep]], colWidths=None, rowHeights=None, style=None, splitByRow=0,
                          repeatRows=0, repeatCols=0, rowSplitRange=None, spaceBefore=None,
                          spaceAfter=None))
    #
    contenue.append(Paragraph("<br/><u>Paliers ascendants et descendants isolés du capteur raccordé :</u>", styleN))
    data2=[""]*len(values_sep_paliers)
    #print(values_sep_paliers)
    for n in range(len(values_sep_paliers)):
        data2[n]=[]
        #print(values_sep_paliers[n])
        for i in range (len(values_sep_paliers[n])):
            data2[n].append([i,float(values_sep_paliers[n][i])])
            #print(i,int(values_sep_paliers[n][i]))
    #tracé des graphiques par paires de paliers
    w = 470
    h = 55
    #print (data2[0])
    for i in range(int(len(data2)/2)):
        gdata = [data2[i]]+[data2[int(len(data2)-i-1)]]
        graph=fs.trace_graph('Paliers '+str(i),gdata, w, h, xtvisi=0, ForceXzero=0)
        # graph = fs.LineChartWithMarkers('Paliers ' + str(i), gdata, w, h)
        contenue.append(graph)
        if i+1 == int(len(data2)/2):
            gdata = [data2[int(len(data2)/2)]]
            graph = fs.trace_graph('Paliers '+str(i+1),gdata, w, h, 0, ForceXzero=0)
            contenue.append(graph)
    ############################
    d1 = today.strftime("%Y-%m-%d")
    doc = SimpleDocTemplate('Traitement_Mesure_Capteur-'+str(numcapteur)+'_'+d1+'-'+nom_utilisateur+'.pdf',
                            pagesize = A4,
                            title = 'Premier test',
                            leftMargin= 1.5*cm,
                            rightMargin= 1.5*cm,
                            author = 'Moi',
                            topMargin=3.5,
                            showBoundary = 0)
    doc.build(contenue)
