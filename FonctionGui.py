# !/usr/bin/python
# !python
# -*- coding: utf-8 -*-
"""
Created on Thus Aug  23 15:05:52 2022

@author : Aelurus

@contributor: Bruno
"""
# FonctionGui.py
try:
    import sys, os
    import codecs
    import glob
    # from tkinter import *
    from tkinter.scrolledtext import ScrolledText
    from tkinter import filedialog, END, Frame, Canvas, TOP, BOTH, NS, EW, INSERT, Tk, Label, \
        Entry, StringVar, Button, Scrollbar, Listbox, VERTICAL, W, E
    import FonctionsSignal as fs
    import FonctionPdf as pdf
    from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
    from statistics import mean, pstdev
    import matplotlib.pyplot as plt
    import FonctionCSV as fc
except Exception as e:
    print(e)
    input('***')

# zone de def des variables

dossier_actuel = ""
"""Définition de la variable du chemin du dossier"""
motif_fichiers = "*.csv"
varidxinfile1 = 2
"""Index de variable d'intérêt 1 dans les fichiers bruts. Joker :)"""
varidxinfile2 = 10
"""Index de variable d'intérêt 2 dans les fichiers bruts"""


# zone de définition des fonctions
def choisir_dossier():
    """Ouvre un dialogue de sélection de répertoire
        voir http://tkinter.unpythonic.net/wiki/tkFileDialog

    ### Variables
    ----------
    `dossier` : str
        Association automatique de l'adresse du chemin selectionner

    ### Returns
    ------

    lance `pdoc.remplir_liste(dossier)`
    """
    dossier = filedialog.askdirectory(
        title="Sélectionnez le dossier de fichier (s) de mesure (s)",
        mustexist=True,
        parent=fenetre,
    )
    # un dossier a vraiment été sélectionné ?
    if dossier:
        # on remplit la liste de fichiers
        remplir_liste(dossier)
    # end if
# end def

def remplir_liste(dossier):
    """Remplit la liste de fichiers à partir de l'emplacement
        @dossier fourni en paramètre de fonction
    """
    # init globales
    global dossier_actuel
    # on conserve le dossier en cours de traitement
    dossier_actuel = dossier
    # on récupère la liste des fichiers
    liste_fichiers = glob.glob(normaliser(dossier, motif_fichiers))
    liste_fichiers.sort()  # tri par ordre alphabetic
    # on met à jour la listbox à travers la variable de contrôle
    cvar_fichiers.set(" ".join(map(os.path.basename, liste_fichiers)))
# end def

def normaliser(chemin, *args):
    """Met un chemin de fichier en conformité avec l'OS utilisé, utile pour nunux"""
    return os.path.normpath(os.path.join(chemin, *args))
# end def

def afficher_fichier(event):
    """Lecture et affichage du contenu du fichier sélectionné,
    tentative d'implémentation de l'ouverture avec codec pour passage en Ut8
    pour nunux.

    On récupère le nom du fichier
    """
    fichier = normaliser(
        dossier_actuel,
        liste_fichiers.get(liste_fichiers.curselection() or 0)
    )
    """est-ce réellement un fichier ?"""
    if os.path.isfile(fichier):
        affichage_texte.delete("1.0", END)
        affichage_texte1.delete("1.0", END)
        try:

            # oui, on peut l'ouvrir en forçant l'encodage UTF8
            with codecs.open(fichier, 'r', encoding='ANSI',
                             errors='ignore') as file_in:
                # on efface d'abord la zone de texte
                affichage_texte.delete("1.0", END)
                # on insère le nouveau contenu texte du fichier
                affichage_texte.insert("1.0", file_in.read())
                fig = plt.figure(1, figsize=(6, 3))
                # y = []
                plt.clf()
                #
                y = fc.read_col_CSV(fichier, ";", varidxinfile1)
                if y:
                    values_sep_paliers, values, values_sep1, paliers_find = fs.traitement_signal(y, fs.seuil_capteur1())
                    y = fc.supp_txt(y)
                    plt.plot(y, linewidth=0.5)
                else:
                    plt.clf()
                    # values_sep_paliers, values, values_sep1, paliers_find = fs.traitement_signal(y)
                    plt.plot([0], [0], 'r', linewidth=0.5)
                # traitement deuxieme capteur
                y2 = fc.read_col_CSV(fichier, ";", varidxinfile2)
                if y2:
                    values_sep_paliers_2, values_2, values_sep1_2, paliers_find_2 = fs.traitement_signal(y2,
                                                                                                         fs.seuil_capteur2())
                    y2 = fc.supp_txt(y2)
                    plt.plot(y2, 'r', linewidth=0.5)

                else:
                    # values_sep_paliers_2 , values_2 , values_sep1_2 , paliers_find_2 = fs.traitement_signal2(y2)
                    plt.plot([0], [0], 'r', linewidth=0.5)

                # va permettre de stocker les canvs à supprimer pour faire un refresh des graphes,
                # entre 2 ouvertures de fichier
                global remove_canvs

                if remove_canvs:
                    for icanv in remove_canvs:
                        icanv.destroy()
                    remove_canvs = []

                conteneur_canv = Frame(fenetre)
                remove_canvs.append(conteneur_canv)
                # dessin = Canvas(fenetre, bg='white', height=250, width=300)
                conteneur_canv1 = Frame(fenetre)
                remove_canvs.append(conteneur_canv1)
                # dessin1 = Canvas(fenetre, bg='white', height=250, width=300)

                canvas = FigureCanvasTkAgg(fig, master=conteneur_canv)
                canvas.draw()
                canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
                conteneur_canv.grid(row=2, column=0, sticky=NS + EW, padx=5, pady=5)

                # on efface d'abord la zone de texte
                affichage_texte1.delete("1.0", END)
                affichage_texte1.delete("1.0", END)

                ###
                #
                entete = ["--------------------------\nNom capteur\n[N° palier] \tMoyenne [V] \tÉcart-type [mV]"]

                # col = fs.readColCSV1(fichier, ";", varidxinfile1)

                values_capteurs = fs.isol_capteurs(fc.read_col_CSV(fichier, ";", varidxinfile1))
                values_capteurs2 = fs.isol_capteurs(fc.read_col_CSV(fichier, ";", varidxinfile2))

                # data1 et data2, dans la meme logique que dans FonctionPdf/traitement_pdf,
                # sont les variables de préparation des tableaux (une fois, sommant entete et donneestraitees
                datat1 = [entete[0]]
                datat2 = [entete[0]]

                # BGU 2022-08-10 : Codage rapproché de celui de la generation de pdf :
                # Le pre-traitement des données (calcul des variables dérivées)
                # est le même (utilisation de traitement_general_donnees),
                # mais la mise en forme est différente (preparation de datat1 et datat2)
                for capteur, capteur2 in zip(values_capteurs.keys(), values_capteurs2.keys()):
                    values_sep_paliers, values, values_sep, paliers_find = fs.traitement_signal(
                        values_capteurs.get(capteur), fs.seuil_capteur1())
                    values_sep_paliers2, values2, values_sep2, paliers_find2 = fs.traitement_signal(
                        values_capteurs2.get(capteur2), fs.seuil_capteur2())
                    #

                    donneestraitees2 = fs.traitement_general_donnees(paliers_find, paliers_find2, values_sep_paliers,
                                                                     values_sep_paliers2, entete)
                    #
                    datat1.append(str("\n----------\n") + str(capteur) + "\n")
                    datat2.append(str("\n----------\n") + str(capteur2) + "\n")
                    #
                    for i, d in enumerate(donneestraitees2):
                        datat1.append("[" + str(i) + "]\t" + str(d[0]) + "\t" + str(d[1]) + "\n")
                        datat2.append("[" + str(i) + "]\t" + str(d[2]) + "\t" + str(d[3]) + "\n")
                #
                affichage_texte1.insert("0.0", str(len(values_capteurs.keys()))
                                        + " capteur(s) trouvé(s) a raccorder !\n")
                for i, t in enumerate(datat1):
                    affichage_texte1.insert(INSERT, t)

                affichage_texte1.insert("0.0", str(len(values_capteurs2.keys()))
                                        + " mesure(s) de référence(s) trouvé(s) !\n")
                if len(values_capteurs) == len(values_capteurs2):
                    affichage_texte1.insert("0.0", " Ok  !\n")
                else:
                    affichage_texte1.insert("0.0", "Attention soucis ... !\n")
                for i, t in enumerate(datat2):
                    affichage_texte1.insert(INSERT, t)

                fig1 = plt.figure(2, figsize=(6, 3))
                plt.clf()
                if values_sep1:
                    plt.plot(values_sep1, linewidth=0.5)
                else:
                    plt.plot([0], [0], 'r', linewidth=0.5)
                if values_sep1_2:
                    plt.plot(values_sep1_2, 'r', linewidth=0.5)
                else:
                    plt.clf()
                    plt.plot([0], [0], 'r', linewidth=0.5)
                # plt.show()
                canvas = FigureCanvasTkAgg(fig1, master=conteneur_canv1)
                canvas.draw()
                canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
                conteneur_canv1.grid(row=2, column=1, sticky=NS + EW, padx=5, pady=5)
            # end with
            file_in.close()

        except Exception as e:
            affichage_texte1.insert(INSERT, "Y a Erreur : " + str(e))
            plt.close()

    # end if
# end def

def destroy_fenetre():
    """Fermeture de la fenêtre, pourquoi je ferme le tracer içi ?

        ok ***Bruno*** tu as rajouté le `plt.close`.

    """
    plt.close()
    fenetre.destroy()

def lance_traitement_pdf():
    """Lance execution de la génération du pdf aprés quelques vérifications

    ### Variables
    ----------
    `numero_col_1` : `int`

    numero de colonne des premieres données à lire (capteur raccorder)

    `numero_col_2` : `int`

    numero de colonne des deuxime données à lire (capteur de référence)

    `nom_utilisateur` : `str`

    trigrame info récupérer
    """
    fichier = normaliser(
        dossier_actuel,
        liste_fichiers.get(liste_fichiers.curselection() or 0)
    )

    # est-ce réellement un fichier ?
    if os.path.isfile(fichier):
        nom_utilisateur = recup_nomutilisateur()
        # passage des numeros de colonne a lire
        numero_col_1 = varidxinfile1  # numero de colonne des premieres données à lire
        numero_col_2 = varidxinfile2
        try:
            pdf.traitement_pdf(dossier_actuel, fichier, nom_utilisateur, numero_col_1, numero_col_2)
            affichage_texte.delete("1.0", END)
            affichage_texte.insert(INSERT, maZone.get() + ", le traitement est terminé.\n")
            affichage_texte.insert(INSERT, "Merci de sélectionner un fichier")
        except Exception as e:
            affichage_texte.delete("1.0", END)
            affichage_texte.insert(INSERT, maZone.get() + ",!!!!! \n \n---LE TRAITEMENT A ECHOUE--- !!!!!.\n \n")
            affichage_texte.insert(INSERT, str(e))
            affichage_texte.insert(INSERT, "\n \nMerci de sélectionner un fichier")
            affichage_texte.tag_add("---LE TRAITEMENT A ECHOUE---", "2.0", "5.0")
            affichage_texte.tag_config("---LE TRAITEMENT A ECHOUE---", background="red", foreground="blue")

# On définit la fonction appelée par le info
def recup_nomutilisateur():
    """Recupere le trigramme"""
    affichage_texte.delete("1.0", END)
    affichage_texte.insert("1.0", maZone.get() + ", merci de sélectionner un fichier")
    return maZone.get()


def on_closing():
    """Fermeture de la fenetre, pas utilisé ou doublon de 'destroy_fenetre'
    pas utilisé, Bruno a supp sauf si tu voulais en faire quelque chose."""
    destroy_fenetre()


def Initialize():
    """Initialization de la zone graphique GUI"""


# ------------------------------------------------------------------------------------
# on commence par établir l'interface graphique (GUI)
# on crée la fenêtre principale
fenetre = Tk()

# stockage des 2 canvas des graphes plt, pour suppression dans afficher_dossier avant recréation
remove_canvs = []
"""va permettre de stocker les canvs à supprimer pour faire un refresh des graphes,
entre 2 ouvertures de fichier"""

fenetre.title("Traitement-Signal-capteur(s)" + fs.version())
# SVP, NE FORCEZ PAS LA GÉOMÉTRIE de la fenêtre /!\
# elle va s'adapter toute seule...
# ~ fenetre.geometry("1000x800") --> c'est NON !
# d'autant plus qu'elle sera REDIMENSIONNABLE ensuite
# on ajoute des composants graphiques à la fenêtre principale
# on crée un conteneur pour la gestion des fichiers
#####
conteneur_info = Frame(fenetre)
# On crée un Label
champLabel_nom = Label(conteneur_info, text="Nom (Trigramme): ")
# champLabel_nom.grid(row=0, column=0)
champLabel_nom.pack(side="left")
# On crée un Entry (zone de saisie)
maZone = Entry(conteneur_info, width=5)
# On affiche le Entry dans la fenêtre
maZone.insert(0, "XXX")
maZone.pack(side="left")

# On crée un Boutton
monBouton = Button(conteneur_info, text="Valide nom", command=recup_nomutilisateur)
# On affiche le Button dans la fenêtre
monBouton.pack()
# on place le conteneur dans la fenêtre principale
# avec des marges padx et pady
conteneur_info.grid(row=0, column=0, sticky=NS + EW, padx=5, pady=5)

##############################################################################
conteneur_fichiers = Frame(fenetre)
# on rend le conteneur redimensionnable
conteneur_fichiers.columnconfigure(0, weight=1)
conteneur_fichiers.rowconfigure(0, weight=1)
# on crée une étiquette texte dans ce conteneur
Label(
    conteneur_fichiers,
    text="Veuillez sélectionner un fichier :"
).grid(row=0, column=0, sticky=EW)
# on crée la liste des fichiers
cvar_fichiers = StringVar()
liste_fichiers = Listbox(conteneur_fichiers, listvariable=cvar_fichiers)
liste_fichiers.grid(row=1, column=0, sticky=NS + EW)
# avec sa scrollbar
vbar_fichiers = Scrollbar(conteneur_fichiers, orient=VERTICAL)
vbar_fichiers.grid(row=1, column=1, sticky=NS + W)
# on connecte la scrollbar à la liste des fichiers
liste_fichiers.configure(yscrollcommand=vbar_fichiers.set)
vbar_fichiers.configure(command=liste_fichiers.yview)

# on va gérer l'affichage du fichier sur simple clic
# sur un fichier de la liste
liste_fichiers.bind("<ButtonRelease-1>", afficher_fichier)

# on crée un bouton de type 'Parcourir'
Button(
    conteneur_fichiers,
    text="          Sélectionner un dossier                         ",
    command=choisir_dossier, ).grid(row=2, column=0)
# on place le conteneur dans la fenêtre principale
# avec des marges padx et pady
conteneur_fichiers.grid(row=1, column=0, sticky=NS + EW, padx=5, pady=5)
##############################################################################
# on crée un conteneur pour l'affichage
conteneur_affichage = Frame(fenetre)
# on rend le conteneur redimensionnable
conteneur_affichage.columnconfigure(0, weight=1)
conteneur_affichage.rowconfigure(0, weight=1)
# on crée une étiquette texte dans ce conteneur
Label(
    conteneur_affichage,
    text="  Voici le contenu du fichier :                       "
).grid(row=0, column=0, sticky=EW)
Label(
    conteneur_affichage,
    text=" Informations trouvées :                              "
).grid(row=0, column=1, sticky=EW)
# on crée la zone d'affichage de texte
affichage_texte = ScrolledText(
    conteneur_affichage,
    bg="white",
    fg="blue",
    font="sans 9 ",
    height=10,
    width=20,
)
user = recup_nomutilisateur()
# affichage_texte.insert("1.0",user+", merci de sélectionner un fichier")
affichage_texte.grid(row=1, column=0, sticky=NS + EW)

# on ajoute un bouton 'valide'
Button(
    conteneur_affichage,
    text="Génère le PDF du traitement",
    command=lance_traitement_pdf
).grid(row=2, column=0, sticky=E)
# on ajoute un bouton 'quitter'
Button(
    conteneur_affichage,
    text="Quitter",
    command=destroy_fenetre
).grid(row=2, column=1, sticky=E)
# on place le conteneur dans la fenêtre principale
# avec des marges padx et pady
conteneur_affichage.grid(row=1, column=1, sticky=NS + EW, padx=5, pady=5)
# on crée la zone d'affichage de texte
affichage_texte1 = ScrolledText(
    conteneur_affichage,
    bg="white",
    fg="blue",
    font="sans 9 ",
    height=10,
    width=20,
)
affichage_texte1.grid(row=1, column=1, sticky=NS + EW)
# on rend la fenêtre redimensionnable
# fenetre.columnconfigure(1, weight=1)
fenetre.rowconfigure(1, weight=1)


##############################################################################

def MainLoop():
    """On lance la boucle événementielle principale"""

    remplir_liste(".//")
    fenetre.mainloop()


if __name__ == "__main__":
    print("Il n'y a pas d'autotest ....")
