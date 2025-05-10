import os
import subprocess
import numpy as np
import cv2

from Color import *
from StructuredElement import *


class ImageManager:

    def __init__(self, width: int = 640, height: int = 480, autofocus: bool = True,
                 name: str = 'image', extension: str = '.jpg', path: str = './',
                 rgbImage: np.ndarray = None, hsvImage: np.ndarray = None,
                 binaryImage: np.ndarray = None, medianFiltedImage: np.ndarray = None,
                 erosionFiltedImage: np.ndarray = None):
        self.width = width
        self.height = height
        self.autofocus = autofocus
        self.name = name
        self.extension = extension
        self.path = path
        ####cette fonction fera bien le taf 
        je te la donne comme cadeau :)
     def capTure(self):
        # Exécuter la commande libcamera-still
        subprocess.run([
            "libcamera-still", "-n", "-t", "0", "--immediate",
            "--width", "640", "--height", "480", "-o", "image.jpg"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        frame = cv2.imread("image.jpg")
        return frame


        # Vérification si les images sont fournies, sinon initialisation à des valeurs par défaut (ex: tableau vide ou `None`)
        self.rgbImage = rgbImage if rgbImage is not None else np.array([])
        self.hsvImage = hsvImage if hsvImage is not None else np.array([])
        self.binaryImage = binaryImage if binaryImage is not None else np.array([])
        self.medianFiltedImage = medianFiltedImage if medianFiltedImage is not None else np.array([])
        self.erosionFiltedImage = erosionFiltedImage if erosionFiltedImage is not None else np.array([])

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

        Returns:
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
            cmd.append('--autofocus-mode auto --autofocus-on-capture 1')
        cmd.append(f'-o {full_path}')

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

        Returns:
            np.ndarray: Une matrice de dimension 3 contenant l'image dans la base RGB.
        """
        path = self.path
        image_bgr = cv2.imread(path)
        if image_bgr is None:
            raise ValueError(f"Impossible de charger l'image depuis le chemin {path}")

        # Convertir l'image BGR en RGB
        rgbImage = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        self.rgbImage = rgbImage

    def hsvConverter(self):
        """
        Convertit une image RGB en image HSV.

        Params:
            rgbImage (np.ndarray): image en base RGB (3 canaux).

        Returns:
            np.ndarray: image en base HSV (3 canaux).
        """
        rgbImage = self.rgbImage
        if rgbImage is None or rgbImage.ndim != 3 or rgbImage.shape[2] != 3:
            raise ValueError("L'image RGB doit être une matrice 3D avec 3 canaux.")

        hsvImage = cv2.cvtColor(rgbImage, cv2.COLOR_RGB2HSV)

        self.hsvImage = hsvImage

    def binarizer(self, color: Color):
        """
        Applique un seuillage binaire sur une image HSV en fonction d'une couleur cible.

        Params:
            hsvImage (np.ndarray): image en base HSV (3 canaux).
            color (Color): couleur cible (BLUE, YELLOW, ORANGE).

        Returns:
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
        binaryImage = np.where(mask == 255, 0, 1).astype(np.uint8)

        self.binaryImage = binaryImage

    def medianFilter(self, maskSize: int = 1) :
        """
        Applique un filtre médian sur une image binaire.

        Params:
            binaryImage (np.ndarray): matrice binaire 2D.
            maskSize (int): taille du masque du filtre. Par défaut, maskSize = 1.

        Returns:
            np.ndarray: image filtrée par le filtre médian.
        """
        binaryImage = self.binaryImage
        if binaryImage is None or binaryImage.ndim != 2:
            raise ValueError("L'image binaryImage doit être une matrice 2D.")

        # Calcul de la taille du masque du filtre médian
        kernel_size = 2 * maskSize + 1  # Taille du noyau du filtre

        # Appliquer le filtre médian avec la taille du noyau
        filtedImage = cv2.medianBlur(binaryImage, kernel_size)

        self.medianFiltedImage = filtedImage

    def erosionFilter(self, elementType: StructuredElement, elementSize: int) :
        """
        Applique une érosion morphologique sur une image binaire ou en niveaux de gris.

        Params:
            image (np.ndarray): image 2D (binaire ou niveaux de gris). Les pixels d'intérêt sont à 0.
            elementType (StructuringElement): type de l'élément structurant (CERCLE, SQUARE, RECTANGLE).
            elementSize (int): taille de l'élément structurant.

        Returns:
            np.ndarray: image filtrée par érosion.
        """
        image = self.medianFiltedImage
        if image is None or image.ndim != 2:
            raise ValueError("L'image doit être une matrice 2D.")

        # Sélection de la forme de l'élément structurant
        if elementType == StructuredElement.CIRCLE:
            shape = cv2.MORPH_ELLIPSE
        elif elementType == StructuredElement.SQUARE:
            shape = cv2.MORPH_RECT
        elif elementType == StructuredElement.RECTANGLE:
            shape = cv2.MORPH_RECT  # même type que carré, mais géré par taille différente
        else:
            raise ValueError("Type d'élément structurant non supporté.")

        # Création de l'élément structurant
        if elementType == StructuredElement.RECTANGLE:
            kernel = cv2.getStructuringElement(shape, (elementSize * 2, elementSize))
        else:
            kernel = cv2.getStructuringElement(shape, (elementSize, elementSize))

        # Application de l'érosion
        filtedImage = cv2.erode(image, kernel, iterations=1)

        self.erosionFiltedImage = filtedImage
