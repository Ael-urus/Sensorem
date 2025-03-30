# main.py

"""Point d'entrée de l'application Sensorem.

Ce script lance l'interface graphique principale de l'application
Sensorem. Il importe les fonctions nécessaires depuis les modules
`gui_V3` et `FonctionsSignal`.

Attributs :
    title (str) : Titre de la fenêtre principale de l'interface graphique.
    width (int) : Largeur de la fenêtre principale.
    height (int) : Hauteur de la fenêtre principale.
"""

from FonctionsSignal import version
from gui_V3 import mainGui
from FonctionsDB import GestionnaireFenetreDB


def main() -> None:
    """Lance l'interface graphique principale de l'application Sensorem.

    Cette fonction configure le titre, la largeur et la hauteur de la fenêtre
    principale de l'interface graphique. Elle utilise les valeurs suivantes :

    - `APP_TITLE` (str) : Le titre de la fenêtre (incluant le numéro de version).
    - `APP_WIDTH` (int) : La largeur de la fenêtre en pixels.
    - `APP_HEIGHT` (int) : La hauteur de la fenêtre en pixels.

    Ces valeurs sont actuellement définies directement dans la fonction, mais
    il est prévu de les externaliser sous forme de constantes globales pour
    faciliter leur modification et leur réutilisation.

    La fonction lance ensuite l'interface en appelant la fonction `mainGui`
    du module `gui_V3` avec les paramètres configurés.

    Returns:
        None
    """
    # Construit le titre de la fenêtre en concaténant le nom de l'application
    # avec le numéro de version (obtenu via la fonction 'version()')
    app_title: str = "Sensorem - Traitement-Signal-capteur(s) " + version()
    """Titre de l'application (sera une constante globale)."""

    # Définit la largeur de la fenêtre à 500 pixels
    app_width: int = 500
    """Largeur de la fenêtre (sera une constante globale)."""

    # Définit la hauteur de la fenêtre à 500 pixels
    app_height: int = 500
    """Hauteur de la fenêtre (sera une constante globale)."""

    # Lance l'interface graphique avec les paramètres configurés
    mainGui(title=app_title, width=app_width, height=app_height)
    """Lance l'interface graphique."""




if __name__ == "__main__":
    """Exécute le script principal de l'application."""
    main()
