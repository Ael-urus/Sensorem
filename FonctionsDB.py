#FonctionsDB.py

import tkinter as tk
from tkinter import ttk, messagebox, font
import sqlite3
from openpyxl import Workbook
from datetime import datetime
from typing import List, Tuple, Optional, Any, Dict
import FonctionsSignal as fs

class DBManager:
    """
    Gestionnaire de base de données pour les capteurs.

    Cette classe permet de gérer les données de calibration des capteurs dans une base de données SQLite.
    Elle fournit des méthodes pour ajouter, supprimer, récupérer et exporter les données de calibration.
    """

    def __init__(self, db_path='capteurs.db'):
        """
        Initialisation du gestionnaire de base de données.

        :param db_path: Chemin de la base de données SQLite (par défaut : 'capteurs.db').
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        """
        Établit la connexion à la base de données.

        :return: True si la connexion réussit, False sinon.
        """
        try:
            # Établir la connexion à la base de données
            self.conn = sqlite3.connect(self.db_path)
            # Créer un curseur pour exécuter les requêtes
            self.cursor = self.conn.cursor()
            return True
        except sqlite3.Error as e:
            # Gérer les erreurs de connexion
            print(f"Erreur de connexion : {e}")
            return False

    def disconnect(self):
        """
        Ferme la connexion à la base de données.
        """
        # Fermer la connexion si elle est établie
        if self.conn:
            self.conn.close()

    def execute_query(self, query, params=None):
        """
        Exécute une requête SQL avec gestion des erreurs et commit.

        :param query: La requête SQL à exécuter.
        :param params: Les paramètres à passer à la requête (optionnel).
        :return: Un tuple contenant un booléen indiquant le succès de la requête
                 et le résultat de la requête (None si pas de résultat).
        """
        try:
            # Exécuter la requête avec les paramètres
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            # Valider les modifications
            self.conn.commit()
            # Récupérer le résultat de la requête si elle est une requête de sélection
            result = self.cursor.fetchall() if "SELECT" in query.upper() else None
            return True, result
        except sqlite3.Error as e:
            # Gérer les erreurs de requête
            self.conn.rollback()
            return False, str(e)

    def ajouter_calibration(self, date_test: str, numcapteur: int, nom_utilisateur: str, fichier: str,
                            coef_a: float, coef_b: float, a_reg: float, b_reg: float, datat1: list, datat2: list) -> tuple:
        """
        Ajoute une calibration avec les paliers associés.

        :param date_test: Date du test.
        :param numcapteur: Numéro du capteur.
        :param nom_utilisateur: Nom de l'utilisateur.
        :param fichier: Nom du fichier source.
        :param coef_a: Coefficient de conversion a.
        :param coef_b: Coefficient de conversion b.
        :param a_reg: Coefficient capteur a.
        :param b_reg: Coefficient capteur b.
        :param datat1: Liste des données t1 pour les paliers.
        :param datat2: Liste des données t2 pour les paliers.
        :return: Un tuple contenant un booléen indiquant le succès de l'ajout
                 et un message de résultat.
        """
        try:
            # Insertion de la calibration
            query = """
                INSERT INTO calibrations (
                    date_test, version_logiciel, nom_capteur, operateur,
                    fichier_source, coef_conversion_a, coef_conversion_b,
                    coef_capteur_a, coef_capteur_b
                ) VALUES (?,?,?,?,?,?,?,?,?)
            """
            params = (date_test, fs.version(), numcapteur, nom_utilisateur,
                      fichier, coef_a, coef_b, a_reg, b_reg)

            success, _ = self.execute_query(query, params)
            if not success:
                return False, "Erreur lors de l'insertion de la calibration"

            calibration_id = self.cursor.lastrowid

            # Insertion des paliers
            for i in range(1, len(datat1)):
                success = self._ajouter_palier(calibration_id, datat1[i], datat2[i])
                if not success:
                    return False, f"Erreur lors de l'insertion du palier {i}"

            return True, "Calibration ajoutée avec succès"

        except Exception as e:
            return False, str(e)

    def _ajouter_palier(self, calibration_id: int, data_t1: list, data_t2: list) -> bool:
        """
        Méthode privée pour ajouter un palier.

        :param calibration_id: ID de la calibration.
        :param data_t1: Données t1 du palier.
        :param data_t2: Données t2 du palier.
        :return: Un booléen indiquant le succès de l'ajout.
        """
        try:
            # Récupérer les informations du palier
            num_palier = int(data_t1[1])
            nb_valeurs = int(data_t1[2])
            query = """
                INSERT INTO paliers (
                    calibration_id, numero_palier, type, nb_valeurs,
                    moyenne_c_rac, ecart_type_c_rac, moyenne_c_ref, ecart_type_c_ref
                ) VALUES (?,?,?,?,?,?,?,?)
            """
            params = (
                calibration_id, num_palier, "asc/desc", nb_valeurs,
                float(data_t2[0]), float(data_t2[1]),
                float(data_t2[2]), float(data_t2[3])
            )
            success, _ = self.execute_query(query, params)
            return success
        except (ValueError, IndexError):
            return False

    def get_calibrations(self, filters: dict = None, sort_by: str = None) -> list:
        """
        Récupère les calibrations avec filtres et tri.

        :param filters: Un dictionnaire de filtres (optionnel).
        :param sort_by: Le critère de tri (optionnel).
        :return: Une liste de calibrations.
        """
        query = "SELECT * FROM calibrations"
        params = []

        if filters:
            conditions = []
            for key, value in filters.items():
                if value:
                    conditions.append(f"{key} =?")
                    params.append(value)
            if conditions:
                query += " WHERE " + " AND ".join(conditions)

        if sort_by:
            query += f" ORDER BY {sort_by}"

        success, result = self.execute_query(query, params if params else None)
        return result if success else []

    def supprimer_calibration(self, calibration_id: int) -> tuple:
        """
        Supprime une calibration et ses paliers associés.

        :param calibration_id: L'ID de la calibration à supprimer.
        :return: Un tuple contenant un booléen indiquant le succès de la suppression
                 et un message de résultat.
        """
        try:
            # Supprimer d'abord les paliers (contrainte de clé étrangère)
            self.execute_query("""
                DELETE FROM paliers 
                WHERE calibration_id =?
            """, (calibration_id,))

            # Puis supprimer la calibration
            self.execute_query("""
                DELETE FROM calibrations 
                WHERE id =?
            """, (calibration_id,))

            return True, "Calibration supprimée avec succès"
        except sqlite3.Error as e:
            return False, f"Erreur lors de la suppression : {str(e)}"

    def exporter_excel(self, filtres: dict = None) -> tuple:
        """
        Exporte les données avec filtres vers Excel.

        :param filtres: Dictionnaire des filtres à appliquer (optionnel).
        :return: Un tuple contenant un booléen indiquant le succès de l'export
                 et un message de résultat.
        """
        try:
            wb = Workbook()
            ws_calibrations = wb.active
            ws_calibrations.title = "Calibrations"

            # En-têtes
            calibrations = self.get_calibrations(filtres)
            if calibrations:
                headers = [
                    "ID", "Date Test", "Version", "Capteur", "Opérateur",
                    "Fichier", "Coef Conv A", "Coef Conv B", "Coef Capt A", "Coef Capt B"
                ]
                ws_calibrations.append(headers)

                # Données
                for cal in calibrations:
                    ws_calibrations.append(cal)

                # Formatage
                for col in ws_calibrations.columns:
                    max_length = 0
                    for cell in col:
                        max_length = max(max_length, len(str(cell.value)))
                    ws_calibrations.column_dimensions[col[0].column_letter].width = max_length + 2

            # Nom de fichier avec date
            date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"export_capteurs_{date_str}.xlsx"
            wb.save(filename)
            return True, f"Export réussi: {filename}"
        except Exception as e:
            return False, f"Erreur lors de l'export: {str(e)}"

    def get_dernieres_calibrations(self) -> tuple:
        """
        Récupère la dernière calibration pour chaque capteur.

        :return: Un tuple contenant un booléen indiquant le succès de la requête
                 et soit la liste des calibrations, soit un message d'erreur.
        """
        query = """
            WITH DernieresCalibs AS (
                SELECT 
                    c.*,
                    ROW_NUMBER() OVER (
                        PARTITION BY nom_capteur 
                        ORDER BY date_test DESC, id DESC
                    ) as rn
                FROM calibrations c
            )
            SELECT * FROM DernieresCalibs
            WHERE rn = 1
            ORDER BY nom_capteur
        """

        success, result = self.execute_query(query)
        if not success:
            return False, "Erreur lors de la récupération des dernières calibrations"
        if not result:
            return False, "Aucune calibration trouvée"
        return True, result

    def get_dernieres_calibrations(self) -> tuple:
        """
        Récupère la dernière calibration pour chaque capteur.

        :return: Un tuple contenant un booléen indiquant le succès de la requête
                 et soit la liste des calibrations, soit un message d'erreur.
        """
        query = """
            WITH DernieresCalibs AS (
                SELECT 
                    c.*,
                    ROW_NUMBER() OVER (
                        PARTITION BY nom_capteur 
                        ORDER BY date_test DESC, id DESC
                    ) as rn
                FROM calibrations c
            )
            SELECT * FROM DernieresCalibs
            WHERE rn = 1
            ORDER BY nom_capteur
        """

        return self.execute_query(query)

    def exporter_dernieres_calibrations(self) -> tuple:
        """
        Exporte les dernières calibrations pour chaque capteur dans un fichier Excel.

        :return: Un tuple contenant un booléen indiquant le succès de l'export
                 et un message de résultat.
        """
        try:
            success, result = self.get_dernieres_calibrations()
            if not success:
                return False, "Erreur lors de la récupération des dernières calibrations"

            wb = Workbook()
            ws = wb.active
            ws.title = "Dernières Calibrations"

            # Ajouter les en-têtes
            headers = ["ID", "Date Test", "Version", "Capteur", "Opérateur",
                       "Fichier", "Coef Conv A", "Coef Conv B", "Coef Capt A", "Coef Capt B"]
            ws.append(headers)

            # Ajouter les données
            for cal in result:
                ws.append(cal)

            # Sauvegarde du fichier avec un horodatage unique
            filename = f"dernieres_calibrations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            wb.save(filename)

            return True, f"Les dernières calibrations ont été exportées dans {filename}"
        except Exception as e:
            return False, f"Erreur lors de l'export: {str(e)}"

class GestionnaireFenetreDB:
    def __init__(self):
        self.fenetre_db = None

    def ouvrir_fenetre_db(self, parent):
        """Ouvre la fenêtre de gestion de base de données si elle n'existe pas déjà."""
        if self.fenetre_db is None or not self.fenetre_db.winfo_exists():
            # Créer une nouvelle fenêtre
            self.fenetre_db = tk.Toplevel(parent)
            self.fenetre_db.title("Gestion de la Base de Données")

            # Définir les dimensions
            window_width = int(parent.winfo_screenwidth() * 0.8)
            window_height = int(parent.winfo_screenheight() * 0.8)
            self.fenetre_db.geometry(f"{window_width}x{window_height}")

            # Créer le notebook et les onglets
            notebook = ttk.Notebook(self.fenetre_db)
            notebook.pack(fill=tk.BOTH, expand=True)

            # Créer les onglets avec les fonctions existantes
            creer_onglet_base_de_donnees(notebook)
            creer_onglet_deux(notebook)

            # Assurer que la fenêtre reste au premier plan jusqu'à sa fermeture
            self.fenetre_db.transient(parent)
            self.fenetre_db.grab_set()

            # Gérer la fermeture propre
            def on_closing():
                self.fenetre_db.grab_release()
                self.fenetre_db.destroy()
                self.fenetre_db = None

            self.fenetre_db.protocol("WM_DELETE_WINDOW", on_closing)
        else:
            # Si la fenêtre existe déjà, la mettre au premier plan
            self.fenetre_db.lift()
            self.fenetre_db.focus_force()

def creer_onglet_base_de_donnees(notebook):
    """Crée l'onglet Base de données avec filtres et tri."""
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Base de données")

    # Frame pour les filtres
    frame_filtres = ttk.LabelFrame(frame, text="Filtres")
    frame_filtres.pack(fill=tk.X, padx=5, pady=5)

    # Frame pour les TreeViews
    frame_data = ttk.Frame(frame)
    frame_data.pack(fill=tk.BOTH, expand=True)

    # Création du PanedWindow pour les TreeViews
    paned = ttk.PanedWindow(frame_data, orient=tk.HORIZONTAL)
    paned.pack(fill=tk.BOTH, expand=True)

    # Création des TreeViews
    tree_calibrations = creer_treeview_calibrations(paned)
    tree_paliers = creer_treeview_paliers(paned)

    paned.add(tree_calibrations.frame)
    paned.add(tree_paliers.frame)

    # Variables pour les filtres
    filtres = {
        'capteur': tk.StringVar(),
        'annee': tk.StringVar(),
        'operateur': tk.StringVar()
    }

    # Création des widgets de filtres
    row = 0
    ttk.Label(frame_filtres, text="Capteur:").grid(row=row, column=0, padx=5, pady=5)
    ttk.Entry(frame_filtres, textvariable=filtres['capteur']).grid(row=row, column=1, padx=5, pady=5)

    ttk.Label(frame_filtres, text="Année:").grid(row=row, column=2, padx=5, pady=5)
    ttk.Entry(frame_filtres, textvariable=filtres['annee']).grid(row=row, column=3, padx=5, pady=5)

    ttk.Label(frame_filtres, text="Opérateur:").grid(row=row, column=4, padx=5, pady=5)
    ttk.Entry(frame_filtres, textvariable=filtres['operateur']).grid(row=row, column=5, padx=5, pady=5)

    def mettre_a_jour_affichage(calibrations=None):
        """Met à jour l'affichage des TreeViews avec les données filtrées."""
        # Effacer les données existantes
        for item in tree_calibrations.get_children():
            tree_calibrations.delete(item)
        for item in tree_paliers.get_children():
            tree_paliers.delete(item)

        # Si aucune donnée n'est fournie, récupérer toutes les calibrations
        if calibrations is None:
            db = DBManager()
            calibrations = db.get_calibrations()
            db.disconnect()

        # Insérer les nouvelles données
        for cal in calibrations:
            tree_calibrations.insert("", tk.END, values=cal)

    def appliquer_filtres():
        """Applique les filtres sélectionnés."""
        db = DBManager()
        filters = {}

        if filtres['capteur'].get():
            filters['nom_capteur'] = filtres['capteur'].get()
        if filtres['annee'].get():
            filters['strftime("%Y", date_test)'] = filtres['annee'].get()
        if filtres['operateur'].get():
            filters['operateur'] = filtres['operateur'].get()

        calibrations = db.get_calibrations(filters=filters)
        mettre_a_jour_affichage(calibrations)
        db.disconnect()

    def on_calibration_select(event):
        """Gère la sélection d'une ou plusieurs calibrations."""
        # Effacer les paliers existants
        for item in tree_paliers.get_children():
            tree_paliers.delete(item)

        selection = tree_calibrations.selection()
        if len(selection) == 1:  # Si une seule calibration est sélectionnée
            item = tree_calibrations.item(selection[0])
            calibration_id = item['values'][0]

            # Charger les paliers pour cette calibration
            db = DBManager()
            success, paliers = db.execute_query(
                "SELECT * FROM paliers WHERE calibration_id = ? ORDER BY numero_palier",
                (calibration_id,)
            )
            if success:
                for palier in paliers:
                    tree_paliers.insert("", tk.END, values=palier)
            db.disconnect()

    def afficher_dernieres_calibrations():
        """Affiche uniquement la dernière calibration de chaque capteur."""
        db = DBManager()
        success, result = db.get_dernieres_calibrations()
        db.disconnect()

        if success:
            mettre_a_jour_affichage(result)
        else:
            messagebox.showerror("Erreur", "Impossible de récupérer les dernières calibrations")

    # Liaison des événements
    tree_calibrations.bind("<<TreeviewSelect>>", on_calibration_select)

    # Boutons d'action
    frame_boutons = ttk.Frame(frame_filtres)
    frame_boutons.grid(row=1, column=0, columnspan=6, pady=5)

    def supprimer_calibrations_selectionnees():
        """Supprime toutes les calibrations sélectionnées après confirmation."""
        selection = tree_calibrations.selection()
        if not selection:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner au moins une calibration à supprimer.")
            return

        nb_selections = len(selection)
        if not messagebox.askyesno("Confirmation",
                                   f"Êtes-vous sûr de vouloir supprimer ces {nb_selections} calibration(s) et tous leurs paliers associés ?"):
            return

        db = DBManager()
        #db.afficher_liste_capteurs_uniques(notebook)
        erreurs = []
        supprimees = 0

        for item_id in selection:
            item = tree_calibrations.item(item_id)
            try:
                calibration_id = item['values'][0]
                success, message = db.supprimer_calibration(calibration_id)

                if success:
                    tree_calibrations.delete(item_id)
                    supprimees += 1
                else:
                    erreurs.append(f"Calibration {calibration_id}: {message}")

            except (IndexError, TypeError) as e:
                erreurs.append(f"Erreur avec l'item {item_id}: {str(e)}")

        db.disconnect()

        # Effacer les paliers affichés
        for item in tree_paliers.get_children():
            tree_paliers.delete(item)

        # Afficher le résultat
        if supprimees > 0:
            message = f"{supprimees} calibration(s) supprimée(s) avec succès."
            if erreurs:
                message += f"\n\nErreurs rencontrées :\n" + "\n".join(erreurs)

            if erreurs:
                messagebox.showwarning("Résultat", message)
            else:
                messagebox.showinfo("Succès", message)
        else:
            messagebox.showerror("Erreur", "Aucune suppression effectuée.\n\n" + "\n".join(erreurs))

    # Ajouter le bouton de suppression
    ttk.Button(frame_boutons,
               text="Supprimer sélection",
               command=supprimer_calibrations_selectionnees
               ).pack(side=tk.LEFT, padx=5)

    ttk.Button(frame_boutons, text="Appliquer filtres",
               command=appliquer_filtres).pack(side=tk.LEFT, padx=5)

    ttk.Button(frame_boutons, text="Réinitialiser filtres",
               command=lambda: [var.set('') for var in filtres.values()] + [mettre_a_jour_affichage()]).pack(
        side=tk.LEFT, padx=5)

    ttk.Button(frame_boutons, text="Exporter filtrés ou liste complete",
               command=lambda: exporter_donnees_filtrees(filtres)).pack(side=tk.LEFT, padx=5)

    # Ajout du bouton afficher_dernieres_calibrations dans l'interface
    ttk.Button(frame_boutons,
               text="Dernières calibrations",
               command=afficher_dernieres_calibrations
               ).pack(side=tk.LEFT, padx=5)
    # Ajout du bouton exporter_dernieres_calibrations dans l'interface
    ttk.Button(frame_boutons,
               text="Exporter dernières calibrations",
               command=lambda: exporter_dernieres_calibrations_db()
               ).pack(side=tk.LEFT, padx=5)

    # Chargement initial des données
    mettre_a_jour_affichage()

    return frame

def creer_onglet_deux(notebook):
    """Crée le 2e onglet  dans le notebook."""
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="EnCours")
    # Ajout de contenu dans frame_2 (exemple)
    label = ttk.Label(frame, text="Contenu de l'onglet 'EnCours' options pour plus tard")
    label.pack(pady=10)
    bouton = ttk.Button(frame, text="Cliquez-moi", command=Nan)
    bouton.pack(pady=5)

def creer_treeview_calibrations(parent):
    """Crée et configure le TreeView des calibrations avec sélection multiple."""
    frame = ttk.Frame(parent)

    columns = ("id", "date_test", "version_logiciel", "nom_capteur", "operateur",
               "fichier_source", "coef_conversion_a", "coef_conversion_b",
               "coef_capteur_a", "coef_capteur_b")

    # Ajouter le paramètre selectmode='extended' pour permettre la sélection multiple
    tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode='extended')

    headers = {
        "id": "ID",
        "date_test": "Date Test",
        "version_logiciel": "Version",
        "nom_capteur": "Capteur",
        "operateur": "Opérateur",
        "fichier_source": "Fichier",
        "coef_conversion_a": "Coef Conv A",
        "coef_conversion_b": "Coef Conv B",
        "coef_capteur_a": "Coef Capt A",
        "coef_capteur_b": "Coef Capt B"
    }

    for col in columns:
        tree.heading(col, text=headers[col])
        tree.column(col, width=100)

    # Scrollbars
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    tree.grid(column=0, row=0, sticky='nsew')
    vsb.grid(column=1, row=0, sticky='ns')
    hsb.grid(column=0, row=1, sticky='ew')

    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)

    tree.frame = frame
    return tree

def creer_treeview_paliers(parent):
    """Crée et configure le TreeView des paliers."""
    frame = ttk.Frame(parent)

    # Définition des colonnes
    columns = ("id", "calibration_id", "numero_palier", "type", "nb_valeurs",
               "moyenne_c_rac", "ecart_type_c_rac", "moyenne_c_ref", "ecart_type_c_ref")

    tree = ttk.Treeview(frame, columns=columns, show="headings")

    # Configuration des en-têtes
    headers = {
        "id": "ID",
        "calibration_id": "Cal ID",
        "numero_palier": "N° Palier",
        "type": "Type",
        "nb_valeurs": "Nb Valeurs",
        "moyenne_c_rac": "Moy C_rac",
        "ecart_type_c_rac": "ET C_rac",
        "moyenne_c_ref": "Moy C_ref",
        "ecart_type_c_ref": "ET C_ref"
    }

    for col in columns:
        tree.heading(col, text=headers[col])
        tree.column(col, width=100)

    # Scrollbars
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    # Placement des widgets
    tree.grid(column=0, row=0, sticky='nsew')
    vsb.grid(column=1, row=0, sticky='ns')
    hsb.grid(column=0, row=1, sticky='ew')

    # Configuration du redimensionnement
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)

    tree.frame = frame  # Permet d'accéder au frame depuis l'extérieur
    return tree

def exporter_donnees_filtrees(filtres):
    """Exporte les données filtrées vers Excel."""
    db = DBManager()
    filters = {}

    if filtres['capteur'].get():
        filters['nom_capteur'] = filtres['capteur'].get()
    if filtres['annee'].get():
        filters['strftime("%Y", date_test)'] = filtres['annee'].get()
    if filtres['operateur'].get():
        filters['operateur'] = filtres['operateur'].get()

    success, message = db.exporter_excel(filters)
    if success:
        messagebox.showinfo("Export réussi", message)
    else:
        messagebox.showerror("Erreur", message)
    db.disconnect()

def exporter_dernieres_calibrations_db():
    """Appelle directement la méthode de DBManager pour exporter les dernières calibrations."""
    db = DBManager()
    success, message = db.exporter_dernieres_calibrations()
    db.disconnect()

    if success:
        messagebox.showinfo("Export réussi", message)
    else:
        messagebox.showerror("Erreur", message)

def Nan():
    message = "Le gars il a dit non :p, mais mais mais"
    messagebox.showerror("Erreur", message)

def creer_affichage(root: tk.Tk):
    """Crée l'interface graphique principale et gère la taille de la fenêtre."""

    root.update_idletasks() # Important pour obtenir les dimensions correctes
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Définir une taille maximale pour la fenêtre (par exemple, 80% de l'écran)
    max_width = int(screen_width * 0.8)
    max_height = int(screen_height * 0.8)

    root.geometry(f"{max_width}x{max_height}")  # Définir la taille maximale

    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)

    creer_onglet_base_de_donnees(notebook)
    creer_onglet_deux(notebook)

if __name__ == "__main__":
    root = tk.Tk()
    creer_affichage(root)

    # Appeler ajouter_exemple_donnees APRÈS root.mainloop() avec root.after
    #root.after(100, ajouter_exemple_donnees)  # Délai de 100ms
    #root.after(100, ajouter_exemple_donnees)  # Délai de 100ms
    #root.after(100, ajouter_exemple_donnees)  # Délai de 100ms

    root.mainloop()
