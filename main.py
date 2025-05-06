# main.py

"""Sensorem application entry point.

This script launches the main graphical interface of the
Sensorem application. It imports the necessary functions from the
modules `gui_V3` and `SignalFunctions`.

Attributes :
    title (str): Title of the GUI's main window.
    width (int) : Main window width.
    height (int): Main window height.
"""

from FonctionsSignal import version
from gui_V3 import mainGui



def main() -> None:
    """
    Launches the main graphical interface of the Sensorem application.

    This function configures the title, width and height of the main
    window. It uses the following values:

    - `APP_TITLE` (str): Window title (including version number).
    - APP_WIDTH` (int): The window width in pixels.
    - APP_HEIGHT` (int): The height of the window in pixels.

    These values are currently defined directly within the function, but
    it is planned to externalize them as global constants to facilitate
    modification and reuse.

    The function then launches the interface by calling the `mainGui` function
    function of module `gui_V3` with the configured parameters.

    Returns:
        None
    “"”
    # Builds the window title by concatenating the application name
    # with the version number (obtained via the 'version()' function)
    """
    app_title: str = "Sensorem - Traitement-Signal-capteur(s) " + version()
    # Application title (will be global constant).

    # Définit la largeur de la fenêtre à 500 pixels
    app_width: int = 500
    # Window width (will be a global constant).

    # Définit la hauteur de la fenêtre à 500 pixels
    app_height: int = 500
    # Window height (will be a global constant).

    # Lance l'interface graphique avec les paramètres configurés
    mainGui(title=app_title, width=app_width, height=app_height)
    # Launches the graphical interface.




if __name__ == "__main__":
    # Executes the application's main script.
    main()
