# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 19:21:41 2020
@author: Aelurus

Toutes les fonctions permettant la production du PDF et a sa mise en page
"""
try:
    # import numpy as np
    import os, sys
    from statistics import mean, pstdev
    import FonctionsSignal as fs
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, Spacer, SimpleDocTemplate, Table, Image, TableStyle
    # from reportlab.graphics.charts.legends import Legend
    # from reportlab.graphics.charts.lineplots import LinePlot
    # from reportlab.graphics.shapes import Drawing, _DrawingEditorMixin, String, Rect
    # from reportlab.graphics.widgets.markers import makeMarker
    # from reportlab.graphics.charts.textlabels import Label
    # from reportlab.graphics.samples.excelcolors import *
    # from reportlab.lib import colors

    from reportlab.graphics.charts.lineplots import LinePlot
    from reportlab.graphics.shapes import Drawing, String
    from reportlab.graphics.widgets.markers import makeMarker
    from reportlab.lib import colors
    from reportlab.graphics.charts.textlabels import Label
    from reportlab.graphics.charts.legends import Legend
    from reportlab.graphics.shapes import _DrawingEditorMixin
    from reportlab.graphics.samples.excelcolors import *

    from reportlab.lib.pagesizes import A4
    from datetime import date
    from reportlab.lib.units import cm
    from pathlib import Path
    # import matplotlib.pyplot as plt
except Exception as e:
    print(e)
    input('***')


##





def create_graph(title, data,chartcolors, x,y, w, shiftw,h,shifth,xYLabel,data2=[[(0, 0)]],chartcolors2=[], xtitle='Nombre de mesures',shiftFontXt=1,yXt=-7, 
                xtvisi=1, ytitle='Tension [V]', y2title='Capteur réf', nomCapteur1='Capteur raccordé',
                nomCapteur2='Capteur référence', ForceXzero=1, isSecondY=True, isLegend=True):

    graph = Drawing(w, h)


    fontSize = 10

    chart = LinePlot()

    chart.data = data  # [((0., 0.491), (1., 0.149), (2., 0.3498), (4., 0.2335))]
    # background = Rect(0, 0, width, height, strokeWidth=0, fillColor=PCMYKColor(0,0,10,0))
    chart.width = w - shiftw
    chart.height = h - shifth
    chart.x = x
    chart.y = y

    chart.lines.strokeWidth = 0.5

    # premier graph
    for i in range(len(chart.lines)):
        chart.lines[i].strokeColor = chartcolors[i]

    # deuxieme graph

    """
    chart.lines[0].symbol = makeMarker('FilledSquare')
    chart.lines[1].symbol = makeMarker('FilledDiamond')
    chart.lines[2].symbol = makeMarker('FilledStarFive')
    chart.lines[3].symbol = makeMarker('FilledTriangle')
    chart.lines[4].symbol = makeMarker('FilledCircle')
    chart.lines[5].symbol = makeMarker('FilledPentagon')
    chart.lines[6].symbol = makeMarker('FilledStarSix')
    chart.lines[7].symbol = makeMarker('FilledHeptagon')
    chart.lines[8].symbol = makeMarker('FilledOctagon')
    chart.lines[9].symbol = makeMarker('FilledCross')
    """

    graph.add(Label(), name='Title')
    # Title.fontName = 'Helvetica-Bold'
    graph.Title.fontSize = fontSize - 1
    graph.Title.x = (w / 2) - len(graph.Title._text) / 2
    graph.Title.y = h - 25
    graph.Title._text = title
    graph.Title.maxWidth = 180
    graph.Title.height = 35
    graph.Title.textAnchor = 'middle'
    #
    # Axe des X
    graph.add(Label(), name='XLabel')
    # XLabel.fontName       = 'Helvetica'
    graph.XLabel.fontSize = fontSize - shiftFontXt
    graph.XLabel.x = w / 2
    graph.XLabel.y = yXt
    graph.XLabel.textAnchor = 'middle'
    # position x et y du titre des axes X
    graph.XLabel.maxWidth = 100
    graph.XLabel.height = 10
    
    if xtvisi == 1:
        graph.XLabel._text = xtitle
    else:
        graph.XLabel._text = ''
    
    
    
    
    #
    # Axe des Y
    graph.add(Label(), name='YLabel')
    # YLabel.fontName       = 'Helvetica'
    graph.YLabel.fontSize = fontSize - 2
    graph.YLabel.x = xYLabel
    graph.YLabel.y = h / 2
    graph.YLabel.angle = 90
    graph.YLabel.textAnchor = 'middle'
    graph.YLabel.maxWidth = 100
    graph.YLabel.height = 20
    graph.YLabel._text = ytitle
    #

    
    # 2eme axe des Y
    if isSecondY:
        graph.add(Label(), name='YLabel')
        graph.YLabel.fontSize = fontSize - 3
        graph.YLabel.x = w - 10
        graph.YLabel.y = h / 2
        graph.YLabel.angle = 90
        graph.YLabel.textAnchor = 'middle'
        graph.YLabel.maxWidth = 100
        graph.YLabel.height = 20
        graph.YLabel._text = y2title

    # legende
    if isLegend:
        graph.add(Legend(), name='Legend')
        graph.Legend.fontSize = fontSize - 3
        graph.Legend.x = 55
        graph.Legend.y = 3
        graph.Legend.dxTextSpace = 5
        graph.Legend.dy = 5
        graph.Legend.dx = 5
        graph.Legend.deltay = 5
        graph.Legend.alignment = 'right'
        graph.Legend.columnMaximum = 1
        graph.Legend.colorNamePairs = [(color01, nomCapteur1), (colors.darkcyan, nomCapteur2)]



    # chart.xValueAxis.labels.fontName       = 'Helvetica'
    chart.xValueAxis.labels.fontSize = fontSize - 2

    chart.xValueAxis.gridStrokeWidth = 0.15
    chart.xValueAxis.gridStrokeColor = colors.darkgrey
    chart.xValueAxis.minimumTickSpacing = 8
    chart.xValueAxis.maximumTicks = 10
    chart.xValueAxis.visibleSubTicks = 1
    chart.xValueAxis.subTickHi = 0
    chart.xValueAxis.subTickLo = 2
    chart.xValueAxis.subTickNum = 1
    chart.xValueAxis.strokeWidth = 0.45
    chart.xValueAxis.forceZero = ForceXzero
    chart.xValueAxis.avoidBoundFrac = None
    # chart.xValueAxis.gridEnd = 175
    chart.xValueAxis.tickDown = 3
    chart.xValueAxis.visibleGrid = 1
    chart.xValueAxis.visible = 1


    chart.yValueAxis.tickLeft = 3
    chart.yValueAxis.labels.fontSize = fontSize - 3
    #
    chart.yValueAxis.visibleGrid = 1
    chart.yValueAxis.gridStrokeWidth = 0.15
    chart.yValueAxis.gridStrokeColor = colors.darkgrey
    chart.yValueAxis.visibleAxis = 1
    chart.yValueAxis.labels.textAnchor = 'start'
    chart.yValueAxis.labels.boxAnchor = 'e'
    chart.yValueAxis.labels.angle = 0
    chart.yValueAxis.labels.dx = -3
    chart.yValueAxis.labels.dy = 0

    chart.yValueAxis.strokeWidth = 0.45
    chart.yValueAxis.visible = 1
    chart.yValueAxis.labels.rightPadding = 2
    chart.yValueAxis.rangeRound = 'both'
    chart.yValueAxis.tickLeft = chart.yValueAxis.tickLeft
    chart.yValueAxis.minimumTickSpacing = 8
    chart.yValueAxis.maximumTicks = 10
    chart.yValueAxis.visibleSubTicks = 1
    chart.yValueAxis.subTickHi = 0
    chart.yValueAxis.subTickLo = 1
    chart.yValueAxis.subTickNum = 1
    chart.yValueAxis.forceZero = ForceXzero
    chart.yValueAxis.avoidBoundFrac = None
    graph.add(chart)

    if not data2 or data2 == [[(0, 0)]]:
        return graph
    else:  # pour un éventuel tracer avec deux courbes
        chart2 = LinePlot()
        chart2.data = data2  # [((0., 0.491), (1., 0.249), (2., 0.3498), (4., 0.2335))]

        for i in range(len(chart2.lines)):
            chart2.lines[i].strokeColor = chartcolors2[i]



        chart2.lines.strokeWidth = 0.5
        chart2.yValueAxis.tickLeft = 3
        chart2.width = chart.width
        chart2.height = chart.height
        chart2.x = chart.x
        chart2.y = chart.y
        chart2.yValueAxis.joinAxisMode = 'right'
        # y2 axis
        chart2.yValueAxis.labels.fontSize = fontSize - 3
        chart2.yValueAxis.visibleGrid = 0
        chart2.yValueAxis.gridStrokeWidth = 0.15
        chart2.yValueAxis.gridStrokeColor = colors.darkgrey
        chart2.yValueAxis.visibleAxis = 1
        chart2.yValueAxis.labels.textAnchor = 'start'
        chart2.yValueAxis.labels.boxAnchor = 'w'
        chart2.yValueAxis.labels.angle = 0
        chart2.yValueAxis.labels.dx = 5
        chart2.yValueAxis.labels.dy = 0
        chart2.yValueAxis.labels.fontSize = fontSize - 2
        chart2.yValueAxis.strokeWidth = 0.45
        chart2.yValueAxis.visible = 1
        chart2.yValueAxis.labels.rightPadding = 2
        chart2.yValueAxis.rangeRound = 'both'
        # chart2.yValueAxis.tickLeft             = -chart.yValueAxis.tickLeft
        chart2.yValueAxis.minimumTickSpacing = 8
        chart2.yValueAxis.maximumTicks = 10
        chart2.yValueAxis.visibleSubTicks = 1
        chart2.yValueAxis.subTickHi = 0
        chart2.yValueAxis.subTickLo = 1
        chart2.yValueAxis.subTickNum = 1
        chart2.yValueAxis.forceZero = ForceXzero
        chart2.yValueAxis.avoidBoundFrac = None

        #
        chart2.xValueAxis.gridStrokeWidth = 0.15
        chart2.xValueAxis.gridStrokeColor = colors.darkgrey
        chart2.xValueAxis.minimumTickSpacing = 8
        chart2.xValueAxis.maximumTicks = 10
        chart2.xValueAxis.visibleSubTicks = 1
        chart2.xValueAxis.subTickHi = 1
        chart2.xValueAxis.subTickLo = 1
        chart2.xValueAxis.subTickNum = 1
        chart2.xValueAxis.strokeWidth = 0.45
        chart2.xValueAxis.forceZero = ForceXzero
        chart2.xValueAxis.avoidBoundFrac = None
        chart2.xValueAxis.gridEnd = 175
        chart2.xValueAxis.tickDown = 3
        chart2.xValueAxis.visibleGrid = 0
        chart2.xValueAxis.visible = 0
        graph.add(chart2)
    return graph


# génération du tableau pour insertion dans le pdf
def myTable(tabledata):
    """Création de tableau pour le pdf, fonction de mise en page
    des données.
    TBC
    """
    t = Table(tabledata, rowHeights=(10))
    GRID_STYLE = TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.darkgrey),
        ('BOX', (0, 0), (-1, 0), 0.25, colors.black),
        ('BACKGROUND', (0, 0), (4, 0), colors.lightgrey),
        ('ALIGN', (0, 1), (-1, -1), "CENTER"),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TEXTFONT', (0, 0), (-1, -1), 'Times-Bold')
    ])
    t.setStyle(GRID_STYLE)
    t.hAlign = 1
    return t


def prep_donnees1(len0, paliers_find, values_sep_paliers):
    """mise en forme des données pour le tab1 du pdf
    """
    # tab 1
    donneestraitees1 = [["0"] * len0] * paliers_find
    #
    coeff_gen = fs.gen_nom_paliers(paliers_find)

    for i in range(paliers_find):
        donneestraitees1[i] = (i + 1, str(coeff_gen[i]), str(round(len(values_sep_paliers[i]), 3)))

    return donneestraitees1


# Initialisation du post traitement du fichier de données pour la génération de pdf
def traitement_pdf(rundir, nom_fichier, nom_utilisateur, colonne1, colonne2):
    """Pré-traitement (calcul de toutes les données dérivées) et mise en forme de toutes les données,
    puis traitement (gen_pdf) pour couple de capteurs capteur-ref
    Yes gros morceau
    """

    # PRe-traitement
    # Entetes de tabs
    # entete1 = [("Nb paliers","asc/desc","Nb de valeurs/palier","Incertitude ± [%]")]
    entete1 = [("Nb paliers", "asc/desc", "Nb de valeurs/palier")]
    entete2 = [("Moyenne C_rac [V]", "Ecart-type C_rac [mV]", "Moyenne C_ref", "Ecart-type C_ref")]

    # values = list()
    values = fs.readColCSV1(nom_fichier, ";", colonne1)
    values_capteurs = fs.isol_capteurs(values)

    values2 = fs.readColCSV1(nom_fichier, ";", colonne2)
    values_capteurs2 = fs.isol_capteurs(values2)
    # print (values_capteurs2)

    # par couple capteur-ref, finlisation du pre-traitement et génération des pdf par capteurs isolés
    for capteur, capteur2 in zip(values_capteurs.keys(), values_capteurs2.keys()):
        #
        values_sep_paliers, values, values_sep, paliers_find = fs.traitement_signal(values_capteurs.get(capteur),fs.seuil_capteur1())
        values_sep_paliers2, values2, values_sep2, paliers_find2 = fs.traitement_signal(values_capteurs2.get(capteur2),fs.seuil_capteur2())
        #
        # print("values_sep_paliers2=",values_sep_paliers2)
        # print(len(values_sep_paliers2))
        # [print(len(values_sep_paliers2[i])) for i in range(len(values_sep_paliers2))]

        # prep des donnees pour Tab1 - uniquement pour le pdf, pas pour le GUI
        donneestraitees1 = prep_donnees1(len(entete1), paliers_find, values_sep_paliers)
        #
        # prep des donnees pour Tab2 - commun au pdf et au GUI
        donneestraitees2 = fs.traitement_general_donnees(paliers_find, paliers_find2, values_sep_paliers,
                                                         values_sep_paliers2, entete2)

        # prep des 2 tableaux
        datat1 = entete1 + donneestraitees1
        datat2 = entete2 + donneestraitees2

        # prep des graphes capteur par capteur
        data_by_capteur = [""] * len(values_sep_paliers)
        # print(values_sep_paliers)
        for n in range(len(values_sep_paliers)):
            data_by_capteur[n] = []
            # print(values_sep_paliers[n])
            for i in range(len(values_sep_paliers[n])):
                data_by_capteur[n].append([i, float(values_sep_paliers[n][i])])
                # print(i,int(values_sep_paliers[n][i]))

        # Uniquement le tracé des pdf, toutes les données ayant été pré-calculées et mises en forme en amont
        gen_pdf(values, capteur, values2, capteur2, datat1, datat2, values_sep, values_sep2, data_by_capteur, rundir,
                nom_fichier, nom_utilisateur)


def gen_pdf(data1, numcapteur, data2, numcapteur2, datat1, datat2, values_sep, values_sep2, data3, rundir, fichier,
            nom_utilisateur):
    """Uniquement le tracé des pdf, toutes les données ayant été pré-calculées
    et mises en forme en amont.
    Génération finale du PDF, on réunit toutes les infos et traitement,
    les graphiques sont générés et incluent directement içi
    """

    color11 = colors.darkcyan
    color12 = colors.darkorange
    color13 = colors.blueviolet
    color14 = colors.darkslategrey
    color15 = colors.antiquewhite
    color16 = colors.darkslategray
    color17 = colors.darkolivegreen
    color18 = colors.bisque
    color19 = colors.aquamarine
    color20 = colors.red

    chartcolors=[color01,color02,color03,color04,color05,color06,color07,color08,color09,color10]
    chartcolors2=[color11,color12,color13,color14,color15,color16,color17,color18,color19,color20]
    chartcolors_palier=[colors.darkcyan,colors.darkorange,colors.blueviolet,colors.darkslategrey,colors.antiquewhite,colors.darkslategray,
                       colors.darkolivegreen,colors.bisque,colors.aquamarine]


    # dat = data1
    fichier = Path(fichier).stem + ".csv"  # nettoyage du chemin du nom de fichier et rajout de l'extension
    #
    ###
    styles = getSampleStyleSheet()
    # styleT = styles['Title']
    # styleH1 = styles['Heading1']
    # styleH2 = styles['Heading2']
    styleH3 = styles['Heading3']
    styleH4 = styles['Heading4']
    styleN = styles['Normal']
    ###
    contenue = []
    today = date.today()
    d1 = today.strftime("%d/%m/%Y")
    logo = "Logo.jpg"
    im = Image(logo, 3.5 * cm, 2 * cm)
    text = "Prétraitement pour le raccordement <br/>du capteur <u>" + str(numcapteur) + "</u>"
    titre = Paragraph(text, styleH3)
    c_droite = "&nbsp; &nbsp; &nbsp; " + d1 + "<br/>&nbsp; &nbsp; &nbsp; " + fs.version()
    c_droite = Paragraph(c_droite, styleN)
    t = Table([[im, titre, '', '', c_droite]])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (4, 0), 'MIDDLE'),
        ('SPAN', (1, 0), (3, 0)),
        ('ALIGN', (0, 0), (-1, 0), 'RIGHT')
    ]))
    ###
    contenue.append(t)

    ################################
    # Quelques calcules sur les paliers
    #################################
    contenue.append(Paragraph("Traitement des mesures", styleH4))
    contenue.append(Paragraph("Fichier de données : (" + fichier
                              + "), traité par " + nom_utilisateur
                              + ", pour le raccordement du capteur " + str(numcapteur)
                              + ".<br/><u>Merci de ne pas les utiliser sans une vérification minimale</u>.<br/>",
                              styleN))
    contenue.append(Spacer(1, .1 * cm))

    # recup des données brutes perduent dans le traitement???
    # et passage en liste des valeurs
    w = 270
    h = 150
    x=40;y=35;shiftw=80;shifth=60
    xYLabel=22
#     mesure_brute = LineChartWithMarkers('Mesures brutes', [fs.prep_donnees_graph(data1)], w, h,
#                                         [fs.prep_donnees_graph(data2)], 1,
#                                         'Nombre de mesures', 'Tension [V]', numcapteur2)
#
#     # tracé de la mesure
#     mesure_sep = LineChartWithMarkers('Mesures corrigées avec identification des paliers',
#                                       [fs.prep_donnees_graph(values_sep)],
#                                       w, h, [fs.prep_donnees_graph(values_sep2)], 1, 'Nombre de mesures', 'Tension [V]',
#                                       numcapteur2)


#     mesure_brute=trace_mesures('Mesures brutes', [fs.prep_donnees_graph(data1)], w, h,
#                                          [fs.prep_donnees_graph(data2)],'Nombre de mesures',1,
#                                          'Tension [V]',numcapteur2,'Capteur raccordé','Capteur référence', 1)
#
#     mesure_sep=trace_mesures('Mesures corrigées avec identification des paliers',
#                                        [fs.prep_donnees_graph(values_sep)],
#                                        w, h, [fs.prep_donnees_graph(values_sep2)],'Nombre de mesures',1,
#                                        'Tension [V]',numcapteur2,'Capteur raccordé','Capteur référence',1)


    
    mesure_brute=create_graph('Mesures brutes', [fs.prep_donnees_graph(data1)], chartcolors, x,y, w, shiftw,h,shifth,xYLabel,
                                         [fs.prep_donnees_graph(data2)],chartcolors2,'Nombre de mesures',2,12, 1,
                                         'Tension [V]',numcapteur2,'Capteur raccordé','Capteur référence', 1,True,True)
    
    mesure_sep=create_graph('Mesures corrigées avec identification des paliers',
                                       [fs.prep_donnees_graph(values_sep)],chartcolors,
                                       x,y, w, shiftw,h,shifth,xYLabel, [fs.prep_donnees_graph(values_sep2)],chartcolors2,'Nombre de mesures',2,12,1,
                                       'Tension [V]',numcapteur2,'Capteur raccordé','Capteur référence',1,True,True)






    # affichage de deux tableaux cote à cote pour simplifier le copier-coller des données utile
    contenue.append(Table([[myTable(datat1), myTable(datat2)]]))
    #############
    contenue.append(Paragraph("Contrôle de la mesure", styleH4))
    contenue.append(
        Paragraph("Représentations graphiques des données brutes, puis isolées et corrigées du pré-traitement.",
                  styleN))
    contenue.append(Spacer(1, .1 * cm))
    contenue.append(Paragraph("<u>Identification des paliers</u>", styleN))

    # affichage de deux graphiques cote cote
    contenue.append(Table([[mesure_brute, mesure_sep]], colWidths=None, rowHeights=None, style=None, splitByRow=0,
                          repeatRows=0, repeatCols=0, rowSplitRange=None, spaceBefore=None,
                          spaceAfter=None))
    #
    contenue.append(Paragraph("<br/><u>Paliers ascendants et descendants isolés du capteur raccordé :</u>", styleN))

    # tracé des graphiques par paires de paliers
    w = 470
    h = 55
    x=12;y=12;shiftw=6;shifth=30
    xYLabel=-17
    # print (data2[0])
    for i in range(int(len(data3) / 2)):
        gdata = [data3[i]] + [data3[int(len(data3) - i - 1)]]
        # graph = fs.LineChartWithMarkers('Paliers ' + str(i), gdata, w, h) 
        #graph = trace_mono_palier('Paliers ' + str(i), gdata, w, h, xtvisi=0, ForceXzero=0)

        graph=create_graph('Paliers ' + str(i), gdata,chartcolors_palier, x,y, w, shiftw,h,shifth,xYLabel, xtvisi=0, ForceXzero=0,isSecondY=False,isLegend=False)


        contenue.append(graph)
        if i + 1 == int(len(data3) / 2):
            gdata = [data3[int(len(data3) / 2)]]

            graph = create_graph('Paliers ' + str(i + 1), gdata, chartcolors_palier,x,y, w, shiftw,h,shifth,xYLabel,xtvisi=1, ForceXzero=0,isSecondY=False,isLegend=False)

            #graph = trace_mono_palier('Paliers ' + str(i + 1), gdata, w, h, 0, ForceXzero=0)
            contenue.append(graph)
    ############################
    d1 = today.strftime("%Y-%m-%d")
    doc = SimpleDocTemplate(os.path.join(rundir, 'Traitement_Mesure_Capteur-' + str(
        numcapteur) + '_' + d1 + '-' + nom_utilisateur + '.pdf'),
                            pagesize=A4,
                            title='Premier test',
                            leftMargin=1.5 * cm,
                            rightMargin=1.5 * cm,
                            author='Moi',
                            topMargin=3.5,
                            showBoundary=0)
    doc.build(contenue)
