# -*- coding: utf-8 -*-
"""
Fonctions permettant la production du PDF et sa mise en page.

Created on Thu Jun 11 19:21:41 2020
@author: Aelurus
"""

# FonctionPdf.py
import os
import sys
import traceback
from logging import exception
import sqlite3
import numpy as np
from datetime import date
from doctest import testmod
from pathlib import Path
from typing import List, Tuple
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics.samples.excelcolors import *
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Spacer, SimpleDocTemplate, Table, Image, TableStyle
from tkinter import messagebox
try:
    import FonctionsSignal as fs
    import FonctionsCSV as fc
    import FonctionsGui_V3 as fg
    import FonctionsDB as fdb

except Exception as e:
    print(f"Une exception s'est produite dans le module {__name__}: {e}")
    print(f"Fichier en cours d'exécution : {os.path.basename(__file__)}")
    input('Appuyez sur Entrée pour continuer...')
    sys.exit(1)
##

def test_get_info_unite_pdf():
    """
    Teste l'intégration de get_info_unite dans FonctionsPdf.py en utilisant fg.
    """
    try:
        # Récupération du gestionnaire de capteurs via l'état global
        capteurs_manager = fg.get_state("capteurs_manager")
        if not capteurs_manager:
            print("Erreur : CapteursManager non initialisé.")
            return

        # Récupération des informations des capteurs
        capteur_infos = capteurs_manager.get_info_unite()

        # Affichage des informations des capteurs
        print("Test des capteurs récupérés dans FonctionsPdf :")
        print("Capteurs :")
        for nom, unite in capteur_infos["capteurs"].items():
            print(f"Capteur : {nom}, Unité : {unite}")

        print("\nCapteur de référence :")
        print(f"Nom : {capteur_infos['capteur_ref']['nom']}, Unité : {capteur_infos['capteur_ref']['unite']}")

    except Exception as e:
        print(f"Erreur lors du test de get_info_unite dans FonctionsPdf : {str(e)}")



def create_graph(title: str, data, chartcolors, x, y, w, shiftw, h, shifth, xYLabel, data2=[[(0., 0.)]], chartcolors2=[],
                 xtitle='Temps [s]', shiftFontXt=1, yXt=-7,
                 xtvisi=1, ytitle: str ='Tension [V]', y2title: str ='Capteur réf',
                 nomCapteur1: str = None, #Ajout des parametres nom capteur et unité
                 unite_capteur1: str = None,
                 nomCapteur2: str = None,
                 unite_capteur2: str = None,
                 ForceXzero=1, isSecondY=True, isLegend=True):
    '''
    Cette fonction crée un graphe à l'aide de la bibliothèque `drawing`. Elle prend plusieurs paramètres obligatoires
    et facultatifs permettant de configurer son apparence et ses données.

    Parameters:
        title (str): Titre du graphe.
        data (list<tuple>): Données à représenter sous forme de liste de couples (x, y).
        chartcolors (list<str>): Couleurs des lignes du premier jeu de données. Doit contenir autant d'éléments
                                que de séries dans `data`.
        x (int): Coordonnée abscisse en pixel de l'origine supérieure gauche du graphe par rapport au coin haut gauche
                de la zone de dessin.
        y (int): Coordonnée ordonne en pixel de l'origine supérieure gauche du graphe par rapport au coin haut gauche
                de la zone de dessin.
        w (int): Largeur en pixels du graphe.
        shiftw (int): Décallage horizontal appliqué aux données avant affichage. Utile si l'abscisse zéro doit être
                      centré sur le graphe.
        h (int): Hauteur en pixels du graphe.
        shifth (int): Décallage vertical appliqué aux données avant affichage. Utile si l'ordonné zéro doit être
                     centré sur le graphe.
        xYLabel (int): Abscisse en pixel de l'extrêmité inférieur gauche de l'étiquette associée à l'axe des ordonnées.
        data2 (list<tuple>, optional): Second ensemble de données à représenter sous forme de liste de couples (x, y).
                                      Par défaut [], pas de seconde série.
        chartcolors2 (list<str>, optional): Couleurs des lignes du second jeu de données. Doit contenir autant
                                           d'éléments que de séries dans `data2`. Par défaut [], pas de seconde
                                           série.
        xtitle (str, optional): Texte à afficher comme libellé de l'axe des abcisses. Par défaut 'Temps [s]'.
        shiftFontXt (int, optional): Valeur numérique positive ou négative indiquant la quantité à incrémenter
                                    (positive) ou diminuer (negative) de la taille du texte utilisé pour
                                    l'affichage du titre de l'axe des abcisses. Par défaut 1.
        yXt (int, optional): Ordonnée en pixel de l'extrêmité inférieur gauche de l'étiquette associée à l'axe des
                              ordonnées. Par défaut -7.
        xtvisi (int, optional): Choix entre 0 ou 1, indique si l'axe des abcisses doit être visible ou non. Par
                                défaut 1.
        ytitle (str, optional): Texte à afficher comme libellé de l'axe des ordonnées. Par défaut 'Tension [V]'.
        y2title (str, optional): Libellé de l'axe des ordonnées droit pour la deuxième série de données. Par
                                défaut 'Capteur réf'.
        nomCapteur1 (str, optional): Nom du premier capteur. Par défaut 'Capteur à raccorder (C_r)'.
        nomCapteur2 (str, optional): Nom du second capteur. Par défaut 'Capteur de référence (C_ref)'
        ForceXzero (int, optional): Indique si l'axe des abscisses doit forcer l'origine à zero. Par défaut 1.
        isSecondY (bool, optional): Active/Désactive l'affichage de l'axe des ordonnées droit. Par défaut True.
        isLegend (bool, optional): Affiche/Masque la légende. Par défaut True.

    Returns:
        drawing.Drawing: Objet instancié correspondant au graphe créé. Peut être exporté vers un fichier image
                          après personnalisation complémentaire.
    Raises:
        NameError: Si les variables `color01` et `color02` sont utilisées mais n'ont pas été correctement
                  définies.
    '''
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
        chart.lines[i].strokeColor = chartcolors[i + 1]

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
    # Axe des Y (Modification ici)
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

    # Correction pour le passage des noms de capteurs et unites
    if nomCapteur1 and unite_capteur1:  # Verification que les valeurs existent
        graph.YLabel._text = f"{nomCapteur1} [{unite_capteur1}]"  # Utilisation d'une f-string
    else:
        graph.YLabel._text = ytitle  # Valeur par défaut si les infos n'existent pas

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
        # Correction pour le passage des noms de capteurs et unites
        if nomCapteur2 and unite_capteur2:
            graph.YLabel._text = f"{nomCapteur2} [{unite_capteur2}]"
        else:
            graph.YLabel._text = y2title

    # legende
    if isLegend:
        graph.add(Legend(), name='Legend')
        graph.Legend.fontSize = fontSize - 2
        # position de la legende
        graph.Legend.x = 25
        graph.Legend.y = 3
        graph.Legend.dxTextSpace = 5
        # taille des cubes de couleur
        graph.Legend.dy = 6
        graph.Legend.dx = 6
        graph.Legend.deltay = 5
        #graph.legend.boxAnchor        = 'nw'
        graph.Legend.alignment = 'right' #Left placerait les marques de couleur à droite du texte.
        graph.Legend.columnMaximum = 1

        #Color2 avec Capteur1 car le premier capteur est tracé en deuxieme ou il y a une inversion
        graph.Legend.colorNamePairs = [(color02, nomCapteur1), (color01, nomCapteur2)]

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
            chart2.lines[i].strokeColor = chartcolors[i]

        chart2.lines.strokeWidth = 0.3
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
    try :
        return graph
    except ValueError:
        print("Oops!  Pas de PDF")



# génération du tableau pour insertion dans le pdf
def myTable(tabledata : list[float]):
    """
        Crée un tableau pour un document PDF en utilisant la bibliothèque ReportLab.

        :param tabledata: Liste de listes contenant les données du tableau.
        :type tabledata: list[list]

        :return: Objet de tableau prêt à être utilisé dans un document PDF.
        :rtype: reportlab.platypus.tables.Table
        """
    t = Table(tabledata, rowHeights=(10))
    # Styles pour la mise en forme du tableau
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


def prep_donnees1(len0: int, paliers_find: int, values_sep_paliers: list[list[float]]) -> list[tuple[int, str, str]]:
    """
    Prépare les données pour le tableau 1 du PDF en formatant les valeurs des paliers.

    Parameters:
    -----------
    len0 : int
        Nombre d'éléments par ligne dans le tableau.
    paliers_find : int
        Nombre de paliers à traiter.
    values_sep_paliers : List[List[float]]
        Liste des valeurs séparées par palier.

    Returns:
    --------
    List[Tuple[int, str, str]]
        Liste des données formatées pour le tableau 1 du PDF.
        Chaque élément de la liste est un tuple contenant :
        - Le numéro du palier
        - Le coefficient généré pour le palier
        - La longueur arrondie des valeurs du palier

    Examples:
    ---------
    >>> prep_donnees1(5, 3, [[1, 2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]])
    [(1, '0', '3'), (2, '1', '3'), (3, '0', '3')]
    """
    donneestraitees1 = [["0"] * len0] * paliers_find
    coeff_gen = fs.gen_nom_paliers(paliers_find)

    for i in range(paliers_find):
        donneestraitees1[i] = (i + 1, str(coeff_gen[i]), str(round(len(values_sep_paliers[i]), 3)))

    return donneestraitees1


# Initialisation du post traitement du fichier de données pour la génération de pdf
def traitement_pdf(rundir: str, nom_fichier: str, nom_utilisateur: str, colonne1: int, colonne2: int, info_unites):
    """Pré-traitement et mise en forme des données, puis génération des PDF par couple de capteurs capteur-ref."""
    #print("Coté FonctionsPDF" ,info_unites)
    try:
        # Récupérer les coefficients de conversion
        coef_a = float(fg.get_state("champ_coef_a").get())
        coef_b = float(fg.get_state("champ_coef_b").get())

        # Vérifier que les coefficients sont valides
        if coef_a == 0:
            raise ValueError("Le coefficient 'a' ne peut pas être nul.")

        # Vérifier que les paramètres d'entrée sont valides
        if not all([rundir, nom_fichier, nom_utilisateur]):
            raise ValueError("Les paramètres rundir, nom_fichier et nom_utilisateur sont obligatoires")

        # Vérifier que le fichier existe
        chemin_complet = os.path.join(rundir, nom_fichier)
        if not os.path.isfile(chemin_complet):
            raise FileNotFoundError(f"Le fichier {chemin_complet} n'existe pas")

        # Pré-traitement des données
        entete1 = [("Nb paliers", "asc/desc", "Nb de valeurs/palier")]
        entete2 = [("Moyenne C_rac [V]", "Ecart-type C_rac [mV]", "Moyenne C_ref", "Ecart-type C_ref")]

        # Lecture des données avec vérification
        values = fc.read_col_csv(nom_fichier, ";", fg.num_colonne_lire("capteur1"))
        values2 = fc.read_col_csv(nom_fichier, ";", fg.num_colonne_lire("capteurRef"))

        if not values or not values2:
            raise ValueError("Impossible de lire les données des colonnes spécifiées")

        # Isolation des capteurs avec vérification
        values_capteurs = fs.isol_capteurs(fs.insert_nomscapteurs_gui(values, 0))
        values_capteurs2 = fs.isol_capteurs(fs.insert_nomscapteurs_gui(values2, 1))

        if not values_capteurs or not values_capteurs2:
            raise ValueError("Aucun capteur trouvé dans les données")

        if len(values_capteurs) != len(values_capteurs2):
            raise ValueError(f"Nombre de capteurs différent : {len(values_capteurs)} vs {len(values_capteurs2)}")

        # Traitement des données pour chaque paire de capteurs
        for capteur, capteur2 in zip(values_capteurs.keys(), values_capteurs2.keys()):
            # Traitement du signal avec vérification
            try:
                values_sep_paliers, values, values_sep, paliers_find, paliers_info = fs.traitement_signal(
                    values_capteurs.get(capteur), fs.seuil_capteur1()
                )
                values_sep_paliers2, values2, values_sep2, paliers_find2, paliers_info2 = fs.traitement_signal(
                    values_capteurs2.get(capteur2), fs.seuil_capteur2()
                )

                # Vérifier que nous avons des données valides
                if not all([values_sep_paliers, values, values_sep, values_sep_paliers2, values2, values_sep2]):
                    print(f"Données manquantes pour les capteurs {capteur} et {capteur2}")
                    continue

                # Préparation des données avec vérification
                donneestraitees1 = prep_donnees1(len(entete1), paliers_find, values_sep_paliers)
                if not donneestraitees1:
                    raise ValueError(f"Erreur lors de la préparation des données 1 pour {capteur}")

                donneestraitees2 = fs.traitement_general_donnees(
                    paliers_find, paliers_find2,
                    values_sep_paliers, values_sep_paliers2,
                    entete2
                )
                if not donneestraitees2:
                    raise ValueError(f"Erreur lors de la préparation des données 2 pour {capteur}")

                # Assemblage des tableaux
                datat1 = entete1 + donneestraitees1
                datat2 = entete2 + donneestraitees2
                #Suppression de l'information sur la stabilité du palier
                #print("Traitement des données:", donneestraitees2)
                #datat2 = []  # Initialisation de la liste contenue
                contenue = []  # Initialisation de la liste contenue
                if donneestraitees2:
                    for data_row in donneestraitees2:
                        nouveau_tuple = data_row[1:3] + data_row[4:]
                        #print (nouveau_tuple)
                        contenue.append(nouveau_tuple)
                datat2 = entete2 + contenue
                #print("Traitement des données:", contenue)

                # Génération des données pour les graphiques avec vérification
                data_by_capteur = []
                for n in range(len(values_sep_paliers)):
                    if values_sep_paliers[n]:  # Vérifier que nous avons des données
                        data_by_capteur.append([
                            [i, float(values_sep_paliers[n][i])]
                            for i in range(len(values_sep_paliers[n]))
                            if str(values_sep_paliers[n][i]).replace('.','',1).isdigit()  # Vérifier que c'est un nombre
                        ])
                        # Convertir les valeurs du capteur de référence
                        valeurs_reference_converties = convertir_valeurs_reference(values_capteurs2[capteur2], coef_a,
                                                                                   coef_b)

                        # Calculer les coefficients de régression
                        a_reg, b_reg = calculer_regression(values_capteurs[capteur], valeurs_reference_converties)

                # Génération du PDF
                #print(f"Mon premier capteur: {capteur}, Nom capteur de référence: {capteur2}")
                gen_pdf(
                    values, capteur, values2, capteur2,
                    datat1, datat2, values_sep, values_sep2,
                    data_by_capteur, rundir, nom_fichier, nom_utilisateur,info_unites
                )

            except Exception as e:
                print(f"Erreur lors du traitement des capteurs {capteur} et {capteur2}: {e}")
                print(traceback.format_exc())
                continue  # Passer à la paire de capteurs suivante

    except Exception as e:
        print(f"Erreur globale dans traitement_pdf: {e}")
        print(traceback.format_exc())
        raise  # Propager l'erreur pour la gestion en amont

def convertir_valeurs_reference(valeurs: List[float], coef_a: float, coef_b: float) -> List[float]:
    """
    Convertit les valeurs du capteur de référence en utilisant les coefficients de conversion.

    Args:
        valeurs: Liste des valeurs brutes du capteur de référence.
        coef_a: Coefficient de conversion 'a'.
        coef_b: Coefficient de conversion 'b'.

    Returns:
        Liste des valeurs converties.
    """
    return [coef_a * valeur + coef_b for valeur in valeurs]

def calculer_regression(valeurs_capteur: List[float], valeurs_reference_converties: List[float]) -> Tuple[float, float]:
    """
    Calcule les coefficients de régression linéaire entre les valeurs du capteur passé et les valeurs converties du capteur de référence.

    Args:
        valeurs_capteur: Liste des valeurs du capteur passé.
        valeurs_reference_converties: Liste des valeurs converties du capteur de référence.

    Returns:
        Tuple (a_reg, b_reg) : Coefficients de régression linéaire.
    """
    if len(valeurs_capteur) != len(valeurs_reference_converties):
        raise ValueError("Les listes de valeurs doivent avoir la même longueur.")

    # Calcul des coefficients de régression
    a_reg, b_reg = np.polyfit(valeurs_capteur,valeurs_reference_converties,  1)
    return a_reg, b_reg

def gen_pdf(data1, numcapteur, data2, numcapteur2, datat1, datat2,
            values_sep, values_sep2, data3, rundir, fichier,
            nom_utilisateur,info_unites):
    """Génération du PDF final comprenant les données pré-calculées et les graphiques.

        Cette fonction génère un PDF final contenant toutes les informations et traitements nécessaires pour chaque paire
        de capteurs capteur-ref. Elle inclut des graphiques et des tableaux résumant les données pré-calculées et les résultats
        du traitement.
    Parameters:
    ----------
    data1 : list
        Données brutes du premier capteur.
    numcapteur : str
        Numéro du premier capteur.
    data2 : list
        Données brutes du deuxième capteur.
    numcapteur2 : str
        Numéro du deuxième capteur.
    datat1 : list
        Données formatées pour le tableau 1.
    datat2 : list
        Données formatées pour le tableau 2.
    values_sep : list
        Valeurs séparées des paliers du premier capteur.
    values_sep2 : list
        Valeurs séparées des paliers du deuxième capteur.
    data3 : list
        Données pour les graphiques par paires de paliers.
    rundir : str
        Répertoire de sortie pour le PDF généré.
    fichier : str
        Nom du fichier CSV contenant les données.
    nom_utilisateur : str
        Nom de l'utilisateur pour lequel le PDF est généré.

    Returns:
    ----------
    None le PDF
    """
    # Connexion à la base de données
    conn = sqlite3.connect('capteurs.db')
    cursor = conn.cursor()

    # Initialisation des couleurs pour les graphiques
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
    try:
        # Récupérer les coefficients de conversion
        coef_a = float(fg.get_state("champ_coef_a").get())
        coef_b = float(fg.get_state("champ_coef_b").get())

        # Convertir les valeurs du capteur de référence
        valeurs_reference_converties = convertir_valeurs_reference(data2, coef_a, coef_b)

        # Calculer les coefficients de régression
        a_reg, b_reg = calculer_regression(data1, valeurs_reference_converties)

        # Ajouter les coefficients dans le PDF
        texte_coefficients = f"Coefficient de conversion utilisé [a = {coef_a} | b = {coef_b}]<br/><br/>"
        texte_coefficients += f"  Coefficient du capteur {numcapteur} :  a = <b>{a_reg:.4f}</b>, b = <b>{b_reg:.4f}</b>"

    except Exception as e:
        pass

    #Verife recpetion
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
    text = "Traitement pour le raccordement <br/>du capteur <u>" + str(numcapteur) + "</u>"
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
                              + ", pour le raccordement par comparaison du capteur " + str(numcapteur)
                              + ".<u> Merci de ne pas les utiliser sans une vérification minimale</u>.",
                              styleN))
#    contenue.append(Spacer(1, .1 * cm))
    contenue.append(Spacer(1, .12 * cm))
    contenue.append(Paragraph("<u>Valeurs des paliers</u>", styleN))

    # recup des données brutes perduent dans le traitement???
    # et passage en liste des valeurs
    w = 270
    h = 150
    x=40;y=35;shiftw=80;shifth=60
    xYLabel=22

    # Extraction des informations
    nomCapteur1 = numcapteur + " (C_rac)"
    nomCapteur2 = info_unites[2] + " (C_ref)"
    unite_capteur1 = info_unites[0]
    unite_capteur2 = info_unites[1]

    # Création des graphiques
    mesure_brute = create_graph(
        title='Mesures brutes',
        data=[fs.prep_donnees_graph(data1)],
        chartcolors=chartcolors,
        x=x, y=y, w=w, shiftw=shiftw, h=h, shifth=shifth, xYLabel=xYLabel,
        data2=[fs.prep_donnees_graph(data2)],
        chartcolors2=chartcolors2,
        xtitle='Durée [s]',
        shiftFontXt=2, yXt=12, xtvisi=1,
        ytitle=f'{nomCapteur1} {unite_capteur1} ',
        y2title=f'{nomCapteur2} {unite_capteur2} ',
        nomCapteur1=f'{nomCapteur1}',
        nomCapteur2=f'{nomCapteur2}',
        ForceXzero=1, isSecondY=True, isLegend=True
    )

    mesure_sep = create_graph(
        title='Mesures corrigées avec identification des paliers',
        data=[fs.prep_donnees_graph(values_sep)],
        chartcolors=chartcolors,
        x=x, y=y, w=w, shiftw=shiftw, h=h, shifth=shifth, xYLabel=xYLabel,
        data2=[fs.prep_donnees_graph(values_sep2)],
        chartcolors2=chartcolors2,
        xtitle='Durée [s]',
        shiftFontXt=2, yXt=12, xtvisi=1,
        ytitle=f'{nomCapteur1} {unite_capteur1} ',
        y2title=f'{nomCapteur2} {unite_capteur2} ',
        nomCapteur1=f'{nomCapteur1}',
        nomCapteur2=f'{nomCapteur2}',
        ForceXzero=1, isSecondY=True, isLegend=True
    )

    # affichage de deux tableaux cote à cote pour simplifier le copier-coller des données utile
    contenue.append(Table([[myTable(datat1), myTable(datat2)]]))

    # Ajouter ce texte au contenu du PDF
    contenue.append(Paragraph(texte_coefficients, styles['Normal']))
    contenue.append(Spacer(1, 0.1 * cm))

    #############
    contenue.append(Paragraph("Contrôle de la mesure", styleH4))
    contenue.append(
        Paragraph(
            "Représentations graphiques des données brutes, isolées et corrigées du traitement des moyennes des paliers identifiés.",
            styleN))
    contenue.append(Spacer(1, .12 * cm))
    contenue.append(Paragraph("<u>Identification des paliers</u>", styleN))

    # affichage de deux graphiques cote cote
    contenue.append(Table([[mesure_brute, mesure_sep]], colWidths=None, rowHeights=None, style=None, splitByRow=0,
                          repeatRows=0, repeatCols=0, rowSplitRange=None, spaceBefore=None,
                          spaceAfter=None))
    #
    contenue.append(Paragraph("<br/><u>Valeurs des paliers ascendants et descendants isolés du capteur raccordé :</u>", styleN))

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

    doc = SimpleDocTemplate(os.path.join(rundir, 'Donnees_Raccordement_Capteur-' + str(
        numcapteur) + '_' + d1 + '_' + nom_utilisateur + '.pdf'),
                            pagesize=A4,
                            title='Premier test',
                            leftMargin=1.5 * cm,
                            rightMargin=1.5 * cm,
                            author='Moi',
                            topMargin=3.5,
                            bottomMargin=1.5,
                            showBoundary=0)

    # Enregistrement des données du traitement dans la base de données
    db = fdb.DBManager()
    success, message = db.ajouter_calibration(d1, numcapteur, nom_utilisateur,
                                              fichier, coef_a, coef_b, a_reg, b_reg,
                                              datat1, datat2)
    if not success:
        messagebox.showerror("Erreur", message)
    db.disconnect()

    doc.build(contenue)


def main() ->None:
    testmod()
if __name__ == "__main__":
    main()
