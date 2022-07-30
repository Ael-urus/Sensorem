# !/usr/bin/python
# !python
# -*- coding: utf-8 -*-
"""
Created on Mon May  4 18:02:18 2020
@author: windows
"""
try:
    import os
    import codecs
    import glob
    # from tkinter import *
    from tkinter.scrolledtext import ScrolledText
    from tkinter import filedialog, END, Frame, Canvas, TOP, BOTH, NS, EW, INSERT, Tk, Label, \
        Entry, StringVar, Button, Scrollbar, Listbox, VERTICAL, W, E
    import FonctionsSignal as Fs
    from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
    from statistics import mean, pstdev
    import matplotlib.pyplot as plt
except Exception as e:
    print(e)
    input('***')


# zone de définition des fonctions


def choisir_dossier():
    # ouvre un dialogue de sélection de répertoire
    # voir http://tkinter.unpythonic.net/wiki/tkFileDialog
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
    """
        Remplit la liste de fichiers à partir de l'emplacement
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
    """ Met un chemin de fichier en conformité avec l'OS utilisé"""
    return os.path.normpath(os.path.join(chemin, *args))
# end def


def afficher_fichier(event):
    """ Affiche le contenu du fichier sélectionné"""
    # on récupère le nom du fichier
    fichier = normaliser(
        dossier_actuel,
        liste_fichiers.get(liste_fichiers.curselection() or 0)
    )
    # est-ce réellement un fichier ?
    if os.path.isfile(fichier):
        affichage_texte.delete("1.0", END)
        affichage_texte1.delete("1.0", END)
        affichage_texte1.insert(INSERT, "Y a Erreur")
        # oui, on peut l'ouvrir en forçant l'encodage UTF8
        with codecs.open(fichier, 'r', encoding='utf-8',
                         errors='ignore') as file_in:
            # on efface d'abord la zone de texte
            affichage_texte.delete("1.0", END)
            # on insère le nouveau contenu texte du fichier
            affichage_texte.insert("1.0", file_in.read())

            conteneur_canv = Frame(fenetre)
            dessin = Canvas(fenetre, bg='white', height=250, width=300)
            fig = plt.figure(1, figsize=(6, 3))
            # y = []
            plt.clf()
            y = Fs.readColCSV(fichier, ";", 2)
            if y:
                values_sep_paliers, values, values_sep1, paliers_find = Fs.traitement_signal(y)
                plt.plot(y, linewidth=0.5)
            else:
                plt.clf()
                #values_sep_paliers, values, values_sep1, paliers_find = Fs.traitement_signal(y)
                plt.plot([0],[0], 'r', linewidth=0.5)
            # traitement deuxieme capteur
            y2 = Fs.readColCSV(fichier, ";", 10)
            if y2:
                values_sep_paliers_2, values_2, values_sep1_2, paliers_find_2 = Fs.traitement_signal2(y2)
                plt.plot(y2, 'r', linewidth=0.5)
                
            else:
                values_sep_paliers_2 , values_2 , values_sep1_2 , paliers_find_2 = Fs.traitement_signal2(y2)
                plt.plot([0],[0], 'r', linewidth=0.5)

            canvas = FigureCanvasTkAgg(fig, master=conteneur_canv)
            canvas.draw()
            canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
            conteneur_canv.grid(row=2, column=0, sticky=NS + EW, padx=5, pady=5)
            # on efface d'abord la zone de texte
            affichage_texte1.delete("1.0", END)
            affichage_texte1.delete("1.0", END)
            ###
            er = Fs.isol_capteurs(Fs.readColCSV1(fichier, ";", 2))
            nc = []
            entete2 = ["--------------------------\nNom capteur\n[N° palier] \tMoyenne [V] \tÉcart-type [mV]"]
            for capteur in er.keys():
                nc.append(capteur)
                entete2.append(str("\n----------\n") + str(capteur) + "\n")
                values1 = er.get(capteur)
                values_sep_paliers, values, values_sep, paliers_find = Fs.traitement_signal(values1)
                donneestraitees2 = [["0"] * len(entete2)] * paliers_find
                moyenne = list([""] * paliers_find)
                ecartype = list([""] * paliers_find)
                #
                for i in range(paliers_find):
                    #
                    if values_sep_paliers[i][7: -7]:
                        moyenne[i] = mean(values_sep_paliers[i][7: -7])
                        ecartype[i] = pstdev(values_sep_paliers[i][7: -7]) * 1000
                    else:
                        moyenne[i] = 0
                        ecartype[i] = 0
                    donneestraitees2[i] = (str(round(moyenne[i], 4)), str(round(ecartype[i], 4)))
                for i, d in enumerate(donneestraitees2):
                    entete2.append("[" + str(i) + "]\t" + str(d[0]) + "\t" + str(d[1]) + "\n")
            affichage_texte1.insert("0.0", str(len(nc)) + " capteur(s) trouvé(s) a raccorder !\n")
            for i, t in enumerate(entete2):
                affichage_texte1.insert(INSERT, t)
            er2 = Fs.isol_capteurs(Fs.readColCSV1(fichier, ";", 10))
            nc = []
            entete2 = ["--------------------------\nNom capteur\n[N° palier] \tMoyenne [V] \tÉcart-type [mV]"]
            try:
                for capteur in er2.keys():
                    nc.append(capteur)
                    entete2.append(str("\n----------\n") + str(capteur) + "\n")
                    values1_2 = er2.get(capteur)
                    values_sep_paliers, values, values_sep, paliers_find = Fs.traitement_signal2(values1_2)
                    donneestraitees2 = [["0"] * len(entete2)] * paliers_find
                    moyenne = list([""] * paliers_find)
                    ecartype = list([""] * paliers_find)
                    #
                    for i in range(paliers_find):
                        moyenne[i] = mean(values_sep_paliers[i][7: -7])
                        ecartype[i] = pstdev(values_sep_paliers[i][7: -7])
                        donneestraitees2[i] = (str(round(moyenne[i], 4)), str(round(ecartype[i], 4)))
                    for i, d in enumerate(donneestraitees2):
                        entete2.append("[" + str(i) + "]\t" + str(d[0]) + "\t" + str(d[1]) + "\n")
                affichage_texte1.insert("0.0", str(len(nc)) + " capteur(s) de référence(s) trouvé(s) sont !\n")
                for i, t in enumerate(entete2):
                    affichage_texte1.insert(INSERT, t)
            except :
                print("erreur",donneestraitees2)
                for i, t in enumerate(entete2):
                    affichage_texte1.insert(INSERT, t)
                pass
            conteneur_canv1 = Frame(fenetre)
            dessin1 = Canvas(fenetre, bg='white', height=250, width=300)
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

    # end if
# end def


def lance_traitement():
    fichier = normaliser(
        dossier_actuel,
        liste_fichiers.get(liste_fichiers.curselection() or 0)
    )
    # est-ce réellement un fichier ?
    if os.path.isfile(fichier):
        nom_utilisateur = recup_nomutilisateur()

        try:
            Fs.pre_traitement(fichier, nom_utilisateur, 2, 10)  # passage des numero de colonne a lire
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
    affichage_texte.delete("1.0", END)
    affichage_texte.insert("1.0", maZone.get() + ", merci de sélectionner un fichier")
    return maZone.get()


# début de la fenêtre de selection
# init variables globales


dossier_actuel = ""
motif_fichiers = "*.csv"
# on commence par établir l'interface graphique (GUI)
# on crée la fenêtre principale
fenetre = Tk()

fenetre.title("Traitement-Signal-capteur(s)" + Fs.version())
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
    command=choisir_dossier,
).grid(row=2, column=0)
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
    command=lance_traitement
).grid(row=2, column=0, sticky=E)
# on ajoute un bouton 'quitter'
Button(
    conteneur_affichage,
    text="Quitter",
    command=fenetre.destroy
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
#fenetre.columnconfigure(1, weight=1)
fenetre.rowconfigure(1, weight=1)


##############################################################################

# pour finir
# on lance la boucle événementielle principale
remplir_liste(".//")
fenetre.mainloop()
