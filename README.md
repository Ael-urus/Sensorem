# Sensorem
## Traitement de raccordement de capteur.

Plusieurs modifications :

    _ Rangement du code
    _ Séparation des fonctions dans des fichiers distincts
    _ Recherche des doublons de fonction et suppression
    _ Compléter les Docstring
    _ Mise en place d'une doc html (pdoc)
    _ Reprise de la trame PDF

Bugs :

    _Reprendre la détection sur 10 points à plus, car certaines descente pose soucis
    _Attention en cas de mavais traitement avec plusieurs capteurs,
        il y a un décalages dans le remplissage des tableaux de valeurs (moyenne et ecart..),
        les valeurs différentes dans les paliers des capteurs, crée une erreure. Corriger 13/02/24.


