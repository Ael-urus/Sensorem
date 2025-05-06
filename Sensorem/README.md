# Sensorem - Traitement de Signaux Capteurs

**Sensorem** est une application de bureau conçue pour charger, traiter et analyser des données de signaux capteurs à partir de fichiers CSV. Elle offre une interface graphique conviviale, prend en charge l’internationalisation (français/anglais), et permet de valider des paramètres comme les trigrammes, capteurs, unités et coefficients. L’application est en cours de développement pour inclure la génération de rapports PDF.

## Table des Matières

- [Fonctionnalités](#fonctionnalités)
- [Aperçu](#aperçu)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Configuration](#configuration)
- [Compilation en Exécutable](#compilation-en-exécutable)
- [Structure du Projet](#structure-du-projet)
- [Tests](#tests)
- [Internationalisation](#internationalisation)
- [Licence](#licence)
- [Auteur](#auteur)

## Fonctionnalités ✨

- Chargement et affichage de fichiers `.csv` contenant des données de capteurs.
- Interface graphique basée sur `customtkinter` avec onglets pour le traitement, la base de données et les logs.
- Validation des paramètres :
  - Trigramme (code de 3 lettres).
  - Capteurs (nom et ligne de début).
  - Unités (capteur et référence).
  - Coefficients de conversion.
- Support de l’internationalisation (français et anglais) via `gettext`.
- Journalisation des événements dans `sensorem.log`.
- (À venir) Génération de rapports PDF personnalisés.

## Aperçu 📸

*Ajoutez des captures d’écran pour illustrer l’interface principale et les fonctionnalités.*

```markdown
![Interface principale](screenshots/main_window.png)
![Onglet Processing](screenshots/processing_tab.png)