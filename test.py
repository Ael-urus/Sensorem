y = [1, 2, 3]
y2 = [4, 5, 6]

# Assurez-vous que les deux listes ont la même longueur
if len(y) == len(y2):
    for i in range(len(y)):
        print(f"{y[i]}\t{y2[i]}")
else:
    print("Les listes n'ont pas la même longueur.")