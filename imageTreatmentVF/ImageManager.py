import os
import subprocess
import numpy as np
import cv2

from Color import *
from ObjectNature import *


class ImageManager:

    def __init__(self, width: int = 640, height: int = 480, autofocus: bool = True,
                 name: str = 'image', extension: str = '.jpg', path: str = './',
                 rgbImage: np.ndarray = None, hsvImage: np.ndarray = None,
                 binaryImage: np.ndarray = None, filteredImage: np.ndarray = None,
                 segmentedImage: list = None, objects: list = None):
        self.width = width
        self.height = height
        self.autofocus = autofocus
        self.name = name
        self.extension = extension
        self.path = path

        # Vérification si les images sont fournies, sinon initialisation à des valeurs par défaut (ex: tableau vide ou `None`)
        self.rgbImage = rgbImage if rgbImage is not None else np.array([])
        self.hsvImage = hsvImage if hsvImage is not None else np.array([])
        self.binaryImage = binaryImage if binaryImage is not None else np.array([])
        self.filteredImage = filteredImage if filteredImage is not None else np.array([])
        self.segmentedImage = segmentedImage if segmentedImage is not None else []
        self.objects = objects if objects is not None else []

    def photographer(self) :
        """
        Capture une image à l'aide de la commande libcamera-still.

        Params:
            self : Configuration de la capture:
                - width (int): largeur de l'image en pixels (par défaut 640)
                - height (int): hauteur de l'image en pixels (par défaut 480)
                - autofocus (bool): activer l'autofocus (par défaut True)
                - name (str): nom de fichier sans extension (par défaut 'image')
                - extension (str): extension du fichier (par défaut '.jpg')

        Returns: NONE
            str: Chemin absolu complet vers l'image capturée.
        """
        # Fusionner la config utilisateur
        cfg = {
            'width': self.width,
            'height': self.height,
            'autofocus': self.autofocus,
            'name': self.name,
            'extension': self.extension
        }
        # Préparer le dossier de sortie
        os.makedirs(self.path, exist_ok=True)

        # Construire le nom de fichier complet
        filename = f"{cfg['name']}{cfg['extension']}"
        full_path = os.path.abspath(os.path.join(self.path, filename))

        # Construire la commande libcamera-still
        cmd = [
            'libcamera-still',
            '--width', str(cfg['width']),
            '--height', str(cfg['height']),
        ]
        # Gérer l'autofocus
        if cfg['autofocus']:
            cmd += ['--autofocus-mode', 'auto', '--autofocus-on-capture', '1']
        cmd += ['-o', full_path]

        # Exécuter la commande
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Erreur lors de la capture de l'image: {e}")

        self.path = full_path

    def uploader(self) :
        """
        Charge une image depuis un chemin donné et la retourne sous forme de matrice RGB.

        Params:
            path (str): Le chemin vers le fichier image, par exemple "chemin/vers/nomImage.extension".

        Returns: NONE
            np.ndarray: Une matrice de dimension 3 contenant l'image dans la base RGB.
        """
        path = self.path
        image_bgr = cv2.imread(path)
        if image_bgr is None:
            raise ValueError(f"Impossible de charger l'image depuis le chemin {path}")

        # Convertir l'image BGR en RGB

        self.rgbImage = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

    def hsvConverter(self):
        """
        Convertit une image RGB en image HSV.

        Params:
            rgbImage (np.ndarray): image en base RGB (3 canaux).

        Returns: NONE
            np.ndarray: image en base HSV (3 canaux).
        """
        rgbImage = self.rgbImage
        if rgbImage is None or rgbImage.ndim != 3 or rgbImage.shape[2] != 3:
            raise ValueError("L'image RGB doit être une matrice 3D avec 3 canaux.")

        self.hsvImage = cv2.cvtColor(rgbImage, cv2.COLOR_RGB2HSV)

    def binarizer(self, color: Color):
        """
        Applique un seuillage binaire sur une image HSV en fonction d'une couleur cible.

        Params:
            hsvImage (np.ndarray): image en base HSV (3 canaux).
            color (Color): couleur cible (BLUE, YELLOW, ORANGE).

        Returns: NONE
            np.ndarray: image binaire (1 canal), 0 pour pixels d'intérêt, 1 pour les autres.
        """
        hsvImage = self.hsvImage
        if hsvImage is None or hsvImage.ndim != 3 or hsvImage.shape[2] != 3:
            raise ValueError("L'image HSV doit être une matrice 3D avec 3 canaux.")

        # Définir les intervalles HSV pour chaque couleur
        if color == Color.BLUE:
            lower = np.array([90, 100, 50])
            upper = np.array([150, 255, 255])
        elif color == Color.YELLOW:
            lower = np.array([15, 100, 100])
            upper = np.array([45, 255, 255])
        elif color == Color.ORANGE:
            lower = np.array([5, 100, 100])
            upper = np.array([25, 255, 255])
        else:
            raise ValueError("Couleur non supportée")

        # Créer le masque binaire inversé (0 pour la couleur cible, 1 ailleurs)
        mask = cv2.inRange(hsvImage, lower, upper)

        self.binaryImage = np.where(mask == 255, 0, 1).astype(np.uint8)

    def medianFilter(self, maskSize: int = 7) :
        """
        Applique un filtre médian sur une image binaire.

        Params:
            binaryImage (np.ndarray): matrice binaire 2D.
            maskSize (int): taille du masque du filtre. Par défaut, maskSize = 1.

        Returns: NONE
            np.ndarray: image filtrée par le filtre médian.
        """
        binaryImage = self.binaryImage
        if binaryImage is None or binaryImage.ndim != 2:
            raise ValueError("L'image binaryImage doit être une matrice 2D.")

        # Calcul de la taille du masque du filtre médian
        kernel_size = 2 * maskSize + 1  # Taille du noyau du filtre

        # Appliquer le filtre médian avec la taille du noyau

        self.filteredImage = cv2.medianBlur(binaryImage, kernel_size)

    def segmentationManager(self):
        """
        Segmente une image binaire en régions distinctes à l'aide de l'algorithme Watershed.

        Parameters:
            binaryImage (np.ndarray): image binaire 2D (fond = 1, objets = 0)

        Returns: NONE
            segmentedImage (List[np.ndarray]): liste de matrices binaires, chaque matrice représentant une zone segmentée
        """

        filteredImage = self.filteredImage
        # Inverser l'image car Watershed travaille avec fond=0, objets>0
        inverted = np.uint8(1 - filteredImage)

        # Calcul de la distance transformée
        distance = cv2.distanceTransform(inverted, distanceType=cv2.DIST_L2, maskSize=3)

        # Seuil sur la distance pour obtenir les centres des objets
        _, sure_fg = cv2.threshold(distance, 0.4 * distance.max(), 255, 0)
        sure_fg = np.uint8(sure_fg)

        # Déterminer les zones inconnues
        sure_bg = cv2.dilate(inverted, np.ones((3, 3), np.uint8), iterations=1)
        unknown = cv2.subtract(sure_bg, sure_fg)

        # Étiquetage des composantes connectées
        _, markers = cv2.connectedComponents(sure_fg)

        # Incrémenter tous les marqueurs de sorte que le fond soit 1 au lieu de 0
        markers = markers + 1

        # Marquer les zones inconnues avec zéro
        markers[unknown == 255] = 0

        # Convertir l'image binaire en image couleur pour Watershed
        image_color = cv2.cvtColor(inverted * 255, cv2.COLOR_GRAY2BGR)

        # Appliquer l’algorithme Watershed
        markers = cv2.watershed(image_color, markers)

        self.segmentedImage = []
        # Générer une image binaire pour chaque label > 1
        nbMin = (self.width * self.height) * 0.03
        # 3% of the total size of the image
        for label in range(2, markers.max() + 1):
            region = np.where(markers == label, 1, 0).astype(np.uint8)
            if np.count_nonzero(region) > 1:
                self.segmentedImage.append(region)

    def objectAnalyser(self):
        """
        Identifie la forme principale dans self.filteredImage : carré, cercle ou forme inconnue.

        Returns:
            str: Type de la forme détectée ("carré", "cercle", "inconnue").
        """
        self.objects = []

        for color in Color:

            if color != Color.NONE:

                self.binarizer(color)
                self.medianFilter()
                self.segmentationManager()

                for binaryImage in self.segmentedImage :

                    if binaryImage is None or binaryImage.ndim != 2:
                        raise ValueError("filteredImage doit être une image binaire 2D.")

                    # Trouver les contours
                    contours, _ = cv2.findContours(binaryImage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                    if not contours:
                        self.objects.append(
                            {
                                Color: color,
                                ObjectNature: ObjectNature.NONE
                            }
                        )
                    else :
                        # Prendre le plus grand contour (en cas de bruit résiduel)
                        largest_contour = max(contours, key=cv2.contourArea)

                        # Approximation du contour
                        epsilon = 0.02 * cv2.arcLength(largest_contour, True)
                        approx = cv2.approxPolyDP(largest_contour, epsilon, True)

                        # Identifier la forme
                        if len(approx) == 4:
                            self.objects.append(
                                {
                                    Color : color,
                                    ObjectNature : ObjectNature.CUBE
                                }
                            )
                        elif len(approx) >= 7:
                            self.objects.append(
                                {
                                    Color: color,
                                    ObjectNature: ObjectNature.BALL
                                }
                            )
                        else:
                            self.objects.append(
                                {
                                    Color: color,
                                    ObjectNature: ObjectNature.NONE
                                }
                            )
        print(self.objects)

