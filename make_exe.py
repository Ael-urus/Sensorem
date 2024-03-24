from cx_Freeze import setup, Executable
from FonctionsSignal import version
base = None
#Remplacer "monprogramme.py" par le nom du script qui lance votre programme
executables = [Executable("main.py", base=base)]
#Renseignez ici la liste complète des packages utilisés par votre application
packages = ["sys"]
packages = ["os"]
packages = ["codecs"]
packages = ["glob"]
packages = ["statistics"]
packages = ["reportlab"]
packages = ["datetime"]
packages = ["pathlib"]
packages = ["csv"]
packages = ["tkinter"]
packages = ["matplotlib"]
packages = ["itertools"]
packages = ["idna"]
options = {
    'build_exe': {
        'packages':packages,
    },
}
#Adaptez les valeurs des variables "name", "version", "description" à votre programme.
setup(
    name = "Sensorem",
    options = options,
    version = version(),
    description = "Ebauche d'un traitement de raccordement de capteur par comparaison, vous fournissez un signal enregistré d'un ou deux capteur, puis le code fait les moyenne par paliers detectés... ",
    executables = executables
)