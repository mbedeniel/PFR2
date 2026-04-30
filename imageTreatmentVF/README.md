# Module de Traitement d'Image - PFR2

## Description
Ce dépôt contient le code source du module de traitement d'image développé dans le cadre du projet PFR2. Son objectif principal est d'effectuer la reconnaissance et la localisation d'objets (balles, cubes) afin d'apporter une plus grande précision au scan LiDAR d'un robot ou d'une plateforme mobile. 

Ce module est optimisé pour tourner de manière fluide sur une plateforme mobile embarquée équipée d'une **Raspberry Pi 3 Modèle A+**.

## Fonctionnalités
*   **Gestion de la caméra** : Libération sécurisée des ressources (`/dev/video0`) et capture d'images automatisée via `libcamera-still` avec gestion de l'autofocus.
*   **Filtrage Colorimétrique (HSV)** : Conversion des images RGB en HSV et application de masques de seuillage précis pour détecter les couleurs cibles : Bleu, Jaune et Orange.
*   **Traitement et Segmentation** : Application de filtres médians pour la réduction du bruit et utilisation de l'algorithme de Watershed (Ligne de partage des eaux) couplé à une transformée de distance pour segmenter et séparer efficacement les objets proches ou superposés.
*   **Reconnaissance de Formes** : Analyse avancée des contours (via `cv2.approxPolyDP`) pour classifier la nature des objets détectés (Balle / Cube).
*   **Localisation et Calcul d'Angle** : Calcul du centroïde (moments de l'image) de chaque objet et estimation de leur angle d'orientation relatif à la caméra grâce à une interpolation polynomiale de degré 2, facilitant ainsi la fusion de données avec le LiDAR.

## Matériel Requis
*   **Microcontrôleur / SBC** : Raspberry Pi 3 Modèle A+ (ou version ultérieure).
*   **Caméra** : Module caméra compatible Raspberry Pi (ex: Pi Camera Module 2 ou 3).
*   **Capteur** : LiDAR (les données de vision viennent compléter le scan de ce capteur).

## Dépendances Logicielles
Le projet est développé en Python 3. Les bibliothèques et outils système suivants sont requis :
*   `numpy`
*   `opencv-python` (cv2)
*   `matplotlib` (utilisé pour visualiser la courbe polynomiale dans `detection.py`)

**Outils système requis sur la Raspberry Pi :**
*   `libcamera-apps` (pour la commande `libcamera-still`)
*   `lsof` (pour la gestion des processus utilisant la caméra)

Pour installer les dépendances Python :
`pip install numpy opencv-python matplotlib`

## Architecture des Fichiers
*   `ImageManager.py` : Cœur du système. Contient la classe gérant tout le pipeline de traitement (capture, upload, conversion, binarisation, filtrage, segmentation et analyse).
*   `Color.py` : Énumération des couleurs détectables (`BLUE`, `YELLOW`, `ORANGE`).
*   `Nature.py` : Énumération des types de formes gérés (`CUBE`, `BALL`).
*   `test.py` : Script de démonstration exécutant le pipeline complet. Il capture une image, applique le traitement pour chaque couleur, enregistre les images intermédiaires et affiche la liste des objets détectés.
*   `detection.py` : Script utilitaire calculant les coefficients du polynôme de degré 2 utilisé pour la conversion des coordonnées pixels (x) en angle d'orientation.

## Utilisation
Pour exécuter le pipeline de démonstration et générer les images de test :
`python3 test.py`

Lors de son exécution, le script va générer plusieurs fichiers dans le répertoire courant (ex : `filteredImageBLUE.jpg`, `segmentImageORANGE1.jpg`...) permettant de visualiser les résultats de la binarisation et de la segmentation pour chaque couleur et chaque objet.

---
### Développeur
Ce module a été conçu et développé par **MBEDE Niel** dans le cadre du projet PFR2.
