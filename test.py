import FonctionCSV as fc

# Utilisez la fonction read_col_CSV avec les paramètres nécessaires
fichier = "DebudFindeFichier.csv"
sep = ";"
n = 2
result = fc.read_col_CSV(fichier, sep, n)

print(result)