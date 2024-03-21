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
    from doctest import testmod
    # from tkinter import *
    from tkinter.scrolledtext import ScrolledText
    from tkinter import filedialog, END, Frame, Canvas, TOP, BOTH, NS, EW, INSERT, Tk, Label, \
        Entry, StringVar, Button, Scrollbar, Listbox, VERTICAL, W, E
    import FonctionsSignal as fs
    import FonctionPdf as pdf
    from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
    from statistics import mean, pstdev
    import matplotlib.pyplot as plt
    from itertools import zip_longest
    import FonctionCSV as fc

except ImportError as import_error:
    module_name = import_error.name if hasattr(import_error, 'name') else None
    print(f"Erreur d'importation dans le module {module_name}: {import_error}")
    print(f"Fichier en cours d'exécution : {os.path.basename(__file__)}")
    input('Appuyez sur Entrée pour continuer...')
    sys.exit(1)
except Exception as e:
    print(f"Une exception s'est produite dans le module {__name__}: {e}")
    print(f"Fichier en cours d'exécution : {os.path.basename(__file__)}")
    input('Appuyez sur Entrée pour continuer...')
    sys.exit(1)

# Zone de définition des constantes
DOSSIER_ACTUEL = ""
MOTIF_FICHIERS = "*.csv"
VAR_IDX_IN_FILE_1 = 2 #Numero de la colonne du premier capteur (Mon capteur)
VAR_IDX_IN_FILE_2 = 10

# Zone de définition des fonctions
def choisir_dossier():
    """Ouvre un dialogue de sélection de répertoire
        voir http://tkinter.unpythonic.net/wiki/tkFileDialog

    ### Variables
    ----------
    `dossier` : str
        Association automatique de l'adresse du chemin selectionner

    ### Returns

    """
    dossier = filedialog.askdirectory(
        title="Sélectionnez le dossier de fichier (s) de mesure (s)",
        mustexist=True,
        parent=fenetre,
    )

    # Si un dossier a été sélectionné, on remplit la liste de fichiers
    if dossier:
        remplir_liste(dossier)

def remplir_liste(dossier):
    """Remplit la liste de fichiers à partir de l'emplacement spécifié.

    Args:
        dossier (str): Le chemin du dossier contenant les fichiers de mesure.

    Returns:
        None
    """
    # Initialisation de la variable globale
    global dossier_actuel
    # Conservation du dossier en cours de traitement
    dossier_actuel = dossier
    # Récupération de la liste des fichiers
    liste_fichiers = glob.glob(normaliser(dossier, MOTIF_FICHIERS))
    liste_fichiers.sort()  # Tri par ordre alphabétique
    # Mise à jour de la listbox à travers la variable de contrôle
    cvar_fichiers.set(" ".join(map(os.path.basename, liste_fichiers)))

def normaliser(chemin, *args):
    """Normalise un chemin de fichier pour le rendre compatible avec l'OS utilisé.

    Args:
        chemin (str): Le chemin initial.
        *args: Une séquence d'arguments supplémentaires pour rejoindre le chemin.

    Returns :
        str : Le chemin normalisé.

    Example :
        #>>> print(normaliser("/dossier", "sous-dossier", "fichier.txt"))
        \dossier\sous-dossier\fichier.txt
    """
    return os.path.normpath(os.path.join(chemin, *args))

def afficher_fichier(event):
    """Lecture et affichage du contenu du fichier sélectionné,
    tentative d'implémentation de l'ouverture avec codec pour passage en Ut8
    pour Linux.

    On récupère le nom du fichier

    Args:
        event: Événement déclencheur (non utilisé dans la fonction).
        ligne_debut_affichage : int =21, affiche à partir de la 21 e ligne
    Returns:
        None
    """
    ligne_debut_affichage : int =21
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
            with open(fichier, 'r') as file_in:
                # on efface d'abord la zone de texte
                affichage_texte.delete("1.0", END)
                # on insère le nouveau contenu texte du fichier
                y = fc.read_col_CSV(fichier, ";", VAR_IDX_IN_FILE_1)
                y2 = fc.read_col_CSV(fichier, ";", VAR_IDX_IN_FILE_2)
                # Utilisation de zip_longest pour fusionner les deux listes
                liste_valeurs = list(zip_longest(y, y2))

                # Afficher les éléments côte à côte après le 21ème élément
                for i, element in enumerate(liste_valeurs):
                    if i > ligne_debut_affichage:
                        Y = f"{element[0]}\t\t{element[1]}"
                        affichage_texte.insert(INSERT, Y + "\n")
                fig = plt.figure(1, figsize=(6, 3))
                # y = []
                plt.clf()
                #
                #y = fc.read_col_CSV(fichier, ";", VAR_IDX_IN_FILE_1)
                if y:
                    values_sep_paliers, values, values_sep1, paliers_find = fs.traitement_signal(y, fs.seuil_capteur1())
                    y = fc.supp_txt(y)
                    plt.plot(y, linewidth=0.5, color='red')
                else:
                    plt.clf()
                    # values_sep_paliers, values, values_sep1, paliers_find = fs.traitement_signal(y)
                    plt.plot([0], [0], 'r', linewidth=0.5)
                # traitement deuxieme capteur
                #y2 = fc.read_col_CSV(fichier, ";", VAR_IDX_IN_FILE_2)
                if y2:
                    values_sep_paliers_2, values_2, values_sep1_2, paliers_find_2 = fs.traitement_signal(y2, fs.seuil_capteur2())
                    y2 = fc.supp_txt(y2)
                    plt.plot(y2, 'r', linewidth=0.5, color='purple')
                    plt.legend(['Mon capteur', 'Capteur_ref'])
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

                values_capteurs = fs.isol_capteurs(fc.read_col_CSV(fichier, ";", VAR_IDX_IN_FILE_1))
                values_capteurs2 = fs.isol_capteurs(fc.read_col_CSV(fichier, ";", VAR_IDX_IN_FILE_2))

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
                                        + " capteur(s) trouvé(s) à raccorder !\n")
                for i, t in enumerate(datat1):
                    affichage_texte1.insert(INSERT, t)

                affichage_texte1.insert("0.0", str(len(values_capteurs2.keys()))
                                        + " mesure(s) de référence(s) trouvée(s) !\n")
                if len(values_capteurs) == len(values_capteurs2):
                    affichage_texte1.insert("0.0", " Ok  !\n")
                else:
                    affichage_texte1.insert("0.0", "Attention, il y a un problème... !\n")
                for i, t in enumerate(datat2):
                    affichage_texte1.insert(INSERT, t)

                fig1 = plt.figure(2, figsize=(6, 3))
                plt.clf()
                if values_sep1:
                    plt.plot(values_sep1, linewidth=0.5, color='red')
                else:
                    plt.plot([0], [0], 'r', linewidth=0.5)
                if values_sep1_2:
                    plt.plot(values_sep1_2, 'r', linewidth=0.5, color='purple')
                    plt.legend(['Mon capteur', 'Capteur_ref'])
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
            affichage_texte1.insert(INSERT, "Erreur. Probablement une différence de taille de paliers : " + str(e))
            plt.close()

    # end if
# end def

def destroy_fenetre():
    """Fermeture de la fenêtre, pourquoi je ferme le tracer içi ?

    Cette fonction ferme la fenêtre principale et le tracé (graphique).

    Returns:
        None
    """
    plt.close()
    fenetre.destroy()

def lance_traitement_pdf():
    """Lance l'exécution de la génération du PDF après quelques vérifications.

    ### Variables
    ----------
    `numero_col_1` : `int`
        Numéro de colonne des premières données à lire (capteur raccordé).

    `numero_col_2` : `int`
        Numéro de colonne des deuxièmes données à lire (capteur de référence).

    `nom_utilisateur` : `str`
        Trigramme de l'utilisateur récupéré.
    """
    fichier = normaliser(
        dossier_actuel,
        liste_fichiers.get(liste_fichiers.curselection() or 0)
    )

    if os.path.isfile(fichier):
        nom_utilisateur = recup_nomutilisateur()
        numero_col_1 = VAR_IDX_IN_FILE_1
        numero_col_2 = VAR_IDX_IN_FILE_2
        try:
            pdf.traitement_pdf(dossier_actuel, fichier, nom_utilisateur, numero_col_1, numero_col_2)
            affichage_texte.delete(1.0, END)
            affichage_texte.insert(INSERT, f"{maZone.get()}, le traitement est terminé.\n")
        except Exception  as custom_exception1:
            handle_custom_exception1(custom_exception1)
        except Exception  as custom_exception2:
            handle_custom_exception2(custom_exception2)
        except Exception as e:
            handle_generic_exception(e)

def handle_custom_exception1(exception):
    # Gérer CustomException1
    affichage_texte.insert(INSERT, f"{maZone.get()},\n Oups Pas de PDF.\n")
    pass

def handle_custom_exception2(exception):
    # Gérer CustomException2
    affichage_texte.insert(INSERT, f"{maZone.get()}, Oups 2.\n")
    pass

def handle_generic_exception(exception):
    # Gérer une exception générique
    affichage_texte.delete(1.0, END)
    affichage_texte.insert(INSERT, f"{maZone.get()}, !!!!! \n \n---LE TRAITEMENT A ÉCHOUÉ--- !!!!!.\n \n")
    affichage_texte.insert(INSERT, str(exception))
    affichage_texte.insert(INSERT, "\n \nMerci de sélectionner un fichier")
    affichage_texte.tag_add("---LE TRAITEMENT A ÉCHOUÉ---", "2.0", "5.0")
    affichage_texte.tag_config("---LE TRAITEMENT A ÉCHOUÉ---", background="red", foreground="blue")

# On définit la fonction appelée par le info
def recup_nomutilisateur():
    """Récupère le trigramme de l'utilisateur."""
    trigramme = maZone.get().strip()  # Supprime les espaces au début et à la fin
    if trigramme :
        affichage_texte.delete("1.0", END)
        affichage_texte.insert("1.0", f"Trigramme {trigramme} récupéré.")
        return trigramme
    else:
        affichage_texte.delete("1.0", END)
        affichage_texte.insert("1.0", "Veuillez entrer un trigramme valide.")
        raise ValueError("Trigramme invalide")

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
maZone.insert(0, "Test")
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
    text="  Voici les données trouvées :                       "
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

def run_main_loop():
    """On lance la boucle événementielle principale"""
    remplir_liste(".//")
    fenetre.mainloop()

if __name__ == "__main__":
    testmod()  # Exécute les tests doctest lorsqu'il est exécuté en tant que script principal