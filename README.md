# Sensorem
## Traitement de raccordement de capteur.

Plusieurs modifications :

    _ En cours
    _Corrections de bugs
    _Ajout de la suppression de "#N/A" et de "Calibration" dans la récupération des données.
        Fait le 18/02.
    _Ajout de légend au graph dans le GUI. Fait le 18/02
    _Affichages des valeurs de capteurs dans la fenetre "Voici les données trouvées". Fait le 18/02
    _Ajout d'une moyenne mobile au pas de 2 avant la détection des paliers, il faudrait rajourter la possibilitée 
        de la manipuler dans le GUI. Fait le 24/03/2024
Bugs :

    _Reprendre la détection sur 10 points à plus, car certaines descente pose soucis, passé à 13 le 18/02.
    _Attention en cas de mavais traitement avec plusieurs capteurs,
        il y a un décalages dans le remplissage des tableaux de valeurs (moyenne et ecart..),
        les valeurs différentes dans les paliers des capteurs, crée une erreure.
        Corrigé le 15/02.
    _Inversion des couleurs dans la légende des mesures dans la PDF.
        Corrigé le 18/02.
    -Il n'y a qu'un seul capteur qui s'affiche dans la fenetre "Voici les données trouvées". OK 25/02
    _Metre un néttoyage des valeurs #DIV/!. OK 25/02
    _Perte du fichier selectionné lors de la validation du nom de l'utilisateur. Le fichier traité sera le premier de la liste des fichiers et non celui selectionné avant.



