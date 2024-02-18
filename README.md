# Sensorem
## Traitement de raccordement de capteur.

Plusieurs modifications :

    _ En cours
    _Corrections de bugs
    _Ajout de la suppression de "#N/A" et de "Calibration" dans la récupération des données.
        Fait le 18/02.
    _Ajout de légend au graph dans le GUI. Fait le 18/02
    _Affichages des valeurs de capteurs dans la fenetre "Voici les données trouvées". Fait le 18/02

Bugs :

    _Reprendre la détection sur 10 points à plus, car certaines descente pose soucis, passé à 13 le 18/02.
    _Attention en cas de mavais traitement avec plusieurs capteurs,
        il y a un décalages dans le remplissage des tableaux de valeurs (moyenne et ecart..),
        les valeurs différentes dans les paliers des capteurs, crée une erreure.
        Corrigé le 15/02.
    _Inversion des couleurs dans la légende des mesures dans la PDF.
        Corrigé le 18/02.
    -Il n'y a qu'un seul capteur qui s'affiche dans la fenetre "Voici les données trouvées".



