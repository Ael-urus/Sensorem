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

class LineChartWithMarkers(_DrawingEditorMixin, Drawing):
    """Classe de conteneur graphique. Elle trace les graphiques des mesures brutes et corrigées.
    Pourrait faire doublon avec la fonction trace_graph (qui trace les paliers).
    Mais deux mises en forme diff, plus simple à gérer avec deux générateurs
    """

    def __init__(self,
                 titre_graph='Un titre de graphique',
                 data=[[(0, 0)]],
                 width=215,
                 height=115,
                 data2=[[(0, 0)]],
                 xtvisi=0,
                 xtitle='Nombre de mesures',
                 ytitle='Tension [V]',
                 y2title='Capteur Réf',
                 nomCapteur1='Capteur raccordé',
                 nomCapteur2='Capteur référence',
                 *args, **kw):

        Drawing.__init__(self, width, height, *args, **kw)
        fontSize = 10
        self._add(self, LinePlot(), name='chart', validate=None, desc="The main chart")
        self.chart.data = data  # [((0., 0.491), (1., 0.149), (2., 0.3498), (4., 0.2335))]
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
        # self.chart.fillColor = colors.ivory
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

        # self.Legend.colorNamePairs = Auto(chart=self.plot)
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

# tracer des graph dans le PDF, GROS bordel ^^....
def trace_graph(title, data, w, h, data2=[[(0, 0)]], xtitle='Nombre de mesures',
                xtvisi=1, ytitle='Tension [V]', y2title='Capteur réf', ForceXzero=1):
    """Fonction qui génère les graphiques des paliers dans le pdf, petite usine à gaz à ne pas toucher
    ou alors on à du temps devant sois :), même bordel que la class de graph
    """
    graph = Drawing(w, h)
    # print(data)
    chart = LinePlot()
    chart.y = 12
    chart.x = 12
    chart.width = w - 6
    chart.height = h - 30
    # fontName = 'Helvetica'
    fontSize = 10
    graph.add(Label(), name='XLabel')
    graph.XLabel.fontName = 'Times-Roman'
    graph.XLabel.fontSize = fontSize - 1
    graph.XLabel.x = w / 2
    graph.XLabel.y = -7
    if xtvisi == 1:
        graph.XLabel._text = xtitle
    else:
        graph.XLabel._text = ''
    graph.add(Label(), name='YLabel')
    graph.YLabel.fontSize = fontSize - 2
    graph.YLabel.x = -17
    graph.YLabel.y = h / 2
    graph.YLabel.angle = 90
    graph.YLabel.textAnchor = 'middle'
    graph.YLabel._text = ytitle
    # chart.lineLabels.fontSize           = fontSize
    chart.lineLabels.boxStrokeWidth = 0.3
    # chart.lineLabels.visible            = 1
    chart.lineLabels.boxAnchor = 'c'
    chart.lineLabels.angle = 0
    chart.lineLabelNudge = 10
    chart.joinedLines = 1
    chart.lines.strokeWidth = 0.5
    # line styles
    chart.lines[0].strokeColor = colors.darkcyan
    chart.lines[0].symbol = makeMarker(None)
    chart.lines[0].symbol.size = 2
    chart.lines[0].symbol.angle = 15
    chart.lines[1].strokeColor = colors.darkorange
    chart.lines[1].symbol = makeMarker(None)
    chart.lines[1].symbol.size = 2
    chart.lines[1].symbol.angle = 15
    chart.lines[2].strokeColor = colors.blueviolet
    chart.lines[2].symbol = makeMarker(None)
    chart.lines[2].symbol.size = 3
    chart.lines[2].symbol.angle = 15
    chart.lines[3].strokeColor = colors.darkslategrey
    chart.lines[3].symbol = makeMarker(None)
    chart.lines[3].symbol.size = 2
    chart.lines[3].symbol.angle = 15
    chart.lines[4].strokeColor = colors.antiquewhite
    chart.lines[4].symbol = makeMarker(None)
    chart.lines[4].symbol.size = 2
    chart.lines[4].symbol.angle = 15
    chart.lines[5].strokeColor = colors.darkslategray
    chart.lines[5].symbol = makeMarker(None)
    chart.lines[5].symbol.size = 2
    chart.lines[5].symbol.angle = 15
    chart.lines[6].strokeColor = colors.darkolivegreen
    chart.lines[6].symbol = makeMarker(None)
    chart.lines[6].symbol.size = 2
    chart.lines[6].symbol.angle = 15
    chart.lines[7].strokeColor = colors.bisque
    chart.lines[7].symbol = makeMarker(None)
    chart.lines[7].symbol.size = 2
    chart.lines[7].symbol.angle = 15
    chart.lines[8].strokeColor = colors.aquamarine
    chart.lines[8].symbol = makeMarker(None)
    chart.lines[8].symbol.size = 2
    chart.lines[8].symbol.angle = 15
    chart.lines.strokeWidth = 0.5
    chart.lines.symbol = makeMarker(None)
    # x axis
    chart.xValueAxis.visibleAxis = 1
    chart.xValueAxis.visibleGrid = 1
    chart.xValueAxis.gridStrokeWidth = 0.15
    chart.xValueAxis.gridStrokeColor = colors.darkgrey
    # chart.xValueAxis.labels.fontName       = fontName
    chart.xValueAxis.labels.fontSize = fontSize - 2
    chart.xValueAxis.labels.boxAnchor = 'autox'
    chart.xValueAxis.maximumTicks = 10
    chart.xValueAxis.minimumTickSpacing = 0.5
    chart.xValueAxis.tickDown = 2.5
    chart.xValueAxis.visibleSubTicks = 1
    chart.xValueAxis.subTickHi = 0
    chart.xValueAxis.subTickLo = 1
    chart.xValueAxis.subTickNum = 1
    chart.xValueAxis.subTickNum = 1
    chart.xValueAxis.strokeWidth = 0.45
    chart.xValueAxis.avoidBoundFrac = 0.1
    chart.xValueAxis.forceZero = ForceXzero
    # y axis
    chart.yValueAxis.visibleGrid = 1
    chart.yValueAxis.gridStrokeWidth = 0.15
    chart.yValueAxis.gridStrokeColor = colors.darkgrey
    chart.yValueAxis.visibleAxis = 1
    # chart.yValueAxis.labels.fontName       = fontName
    chart.yValueAxis.labels.fontSize = fontSize - 2
    # chart.yValueAxis.labelTextFormat       = '%0.1f'
    chart.yValueAxis.strokeWidth = 0.45
    chart.yValueAxis.visible = 1
    chart.yValueAxis.labels.rightPadding = 2
    chart.yValueAxis.rangeRound = 'both'
    chart.yValueAxis.tickLeft = 2.5
    chart.yValueAxis.minimumTickSpacing = 8
    chart.yValueAxis.maximumTicks = 10
    chart.yValueAxis.visibleSubTicks = 1
    chart.yValueAxis.subTickHi = 0
    chart.yValueAxis.subTickLo = 1
    chart.yValueAxis.subTickNum = 1
    chart.yValueAxis.forceZero = ForceXzero
    chart.yValueAxis.avoidBoundFrac = 0.1
    graph.add(String(((w / 2) - len(title) * 2), h - 14, 'text'), name='title')
    graph.title.text = title
    graph.title.fontSize = fontSize - 2
    chart.data = data
    graph.add(chart)
    # y2 axis
    # data2 = data
    if not data2 or data2 == [[(0, 0)]]:
        return graph
    else:  # pour un éventuel tracer avec deux courbes
        chart2 = LinePlot()
        chart.y = 12
        chart.x = 12
        chart.width = w - 6
        chart.height = h - 30
        # x axis
        chart2.xValueAxis.visibleAxis = 0
        chart2.xValueAxis.visibleGrid = 0
        chart2.xValueAxis.gridStrokeWidth = 0.15
        chart2.xValueAxis.gridStrokeColor = colors.darkgrey
        # chart2.xValueAxis.labels.fontName       = fontName
        chart2.xValueAxis.labels.fontSize = 0  # fontSize-2
        chart2.xValueAxis.labels.boxAnchor = 'autox'
        chart2.xValueAxis.maximumTicks = 10
        chart2.xValueAxis.minimumTickSpacing = 0.5
        chart2.xValueAxis.tickDown = 2.5
        chart2.xValueAxis.visibleSubTicks = 1
        chart2.xValueAxis.subTickHi = 0
        chart2.xValueAxis.subTickLo = 1
        chart2.xValueAxis.subTickNum = 1
        chart2.xValueAxis.subTickNum = 1
        chart2.xValueAxis.strokeWidth = 0.45
        chart2.xValueAxis.forceZero = ForceXzero
        chart2.data = data2
        chart2.xValueAxis.visible = 1
        #
        # chart2.yTitleText           = y2title
        chart2.yValueAxis.setPosition(50, 50, 125)
        chart2.yValueAxis.joinAxisMode = 'right'
        chart2.yValueAxis.visibleGrid = 0
        chart2.yValueAxis.gridStrokeWidth = 0.15
        chart2.yValueAxis.gridStrokeColor = colors.darkgrey
        chart2.yValueAxis.visibleAxis = 0
        chart2.yValueAxis.labels.fontSize = fontSize - 2
        chart2.yValueAxis.labels.textAnchor = 'start'
        chart2.yValueAxis.labels.boxAnchor = 'w'
        chart2.yValueAxis.labels.angle = 0
        chart2.yValueAxis.labels.dx = 5
        chart2.yValueAxis.labels.dy = 0
        chart2.yValueAxis.strokeWidth = 0.45
        chart2.yValueAxis.labels.rightPadding = 2
        chart2.yValueAxis.rangeRound = 'both'
        chart2.yValueAxis.tickLeft = -2.5
        chart2.yValueAxis.minimumTickSpacing = 8
        chart2.yValueAxis.maximumTicks = 10
        chart2.yValueAxis.visibleSubTicks = 1
        chart2.yValueAxis.subTickHi = 0
        chart2.yValueAxis.subTickLo = -1
        chart2.yValueAxis.subTickNum = 1
        chart2.yValueAxis.forceZero = ForceXzero
        chart2.yValueAxis.avoidBoundFrac = 0.1
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
    entete2 = [("Moyenne C_r [V]", "Ecart-type C_r [mV]", "Moyenne C_ref", "Ecart-type C_ref")]

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
    mesure_brute = LineChartWithMarkers('Mesures brutes', [fs.prep_donnees_graph(data1)], w, h,
                                        [fs.prep_donnees_graph(data2)], 1,
                                        'Nombre de mesures', 'Tension [V]', numcapteur2)

    # tracé de la mesure
    mesure_sep = LineChartWithMarkers('Mesures corrigées avec identification des paliers',
                                      [fs.prep_donnees_graph(values_sep)],
                                      w, h, [fs.prep_donnees_graph(values_sep2)], 1, 'Nombre de mesures', 'Tension [V]',
                                      numcapteur2)

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
    # print (data2[0])
    for i in range(int(len(data3) / 2)):
        gdata = [data3[i]] + [data3[int(len(data3) - i - 1)]]
        graph = trace_graph('Paliers ' + str(i), gdata, w, h, xtvisi=0, ForceXzero=0)
        # graph = fs.LineChartWithMarkers('Paliers ' + str(i), gdata, w, h)
        contenue.append(graph)
        if i + 1 == int(len(data3) / 2):
            gdata = [data3[int(len(data3) / 2)]]
            graph = trace_graph('Paliers ' + str(i + 1), gdata, w, h, 0, ForceXzero=0)
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