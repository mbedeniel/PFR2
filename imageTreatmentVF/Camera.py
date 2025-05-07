import os
import subprocess
import numpy as np
import cv2
from typing import Optional, Dict, Any
from enum import Enum

class ImageManager:
    def __init__(self, width: int = 640, height: int = 480, autofocus: bool = True, 
                 name: str = 'image', extension: str = '.jpg', path: str = './'):
        """
        Initialise la caméra avec les paramètres spécifiés.
        
        Params:
            width (int): largeur de l'image en pixels (par défaut 640)
            height (int): hauteur de l'image en pixels (par défaut 480)
            autofocus (bool): activer l'autofocus (par défaut True)
            name (str): nom de fichier sans extension (par défaut 'image')
            extension (str): extension du fichier (par défaut '.jpg')
            path (str): chemin de sauvegarde (par défaut './')
        """
        self.width = width
        self.height = height
        self.autofocus = autofocus
        self.name = name
        self.extension = extension
        self.path = path

    def photographer(self, config: Optional[Dict[str, Any]] = None) -> str:
        """
        Capture une image à l'aide de la commande libcamera-still.

        Params:
            config (dict, optional): Configuration de la capture:
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
        if config:
            cfg.update(config)

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
            '-o', full_path
        ]
        # Gérer l'autofocus
        if cfg['autofocus']:
            cmd.append('--autofocus-mode auto --autofocus-on-capture 1')

        # Exécuter la commande
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Erreur lors de la capture de l'image: {e}")

        return full_path

    def image_to_frame(self, image_path: str) -> np.ndarray:
        """Lit une image depuis le disque et la convertit en frame OpenCV."""
        try:
            image_bgr = cv2.imread(image_path)
            if image_bgr is None:
                raise ValueError(f"Impossible de charger l'image depuis {image_path}")
            rgbImage = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
            return rgbImage
        except Exception as e:
            print("Erreur lecture image :", e)
            return None

    def uploader(self, path: str) -> np.ndarray:
        """
        Charge une image depuis un chemin donné et la retourne sous forme de matrice RGB.

        Params:
            path (str): Le chemin vers le fichier image, par exemple "chemin/vers/nomImage.extension".

        Returns:
            np.ndarray: Une matrice de dimension 3 contenant l'image dans la base RGB.
        """
        image_bgr = cv2.imread(path)
        if image_bgr is None:
            raise ValueError(f"Impossible de charger l'image depuis le chemin {path}")

        # Convertir l'image BGR en RGB
        rgbImage = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        return rgbImage

    def hsvConverter(self, rgbImage: np.ndarray) -> np.ndarray:
        """
        Convertit une image RGB en image HSV.

        Params:
            rgbImage (np.ndarray): image en base RGB (3 canaux).

        Returns:
            np.ndarray: image en base HSV (3 canaux).
        """
        if rgbImage is None or rgbImage.ndim != 3 or rgbImage.shape[2] != 3:
            raise ValueError("L'image RGB doit être une matrice 3D avec 3 canaux.")

        hsvImage = cv2.cvtColor(rgbImage, cv2.COLOR_RGB2HSV)
        return hsvImage

class Color(Enum):
    BLUE = 1
    YELLOW = 2
    ORANGE = 3

    def binarizer(self, hsvImage: np.ndarray, color: Color) -> np.ndarray:
        """
        Applique un seuillage binaire sur une image HSV en fonction d'une couleur cible.

        Params:
            hsvImage (np.ndarray): image en base HSV (3 canaux).
            color (Color): couleur cible (BLUE, YELLOW, ORANGE).

        Returns:
            np.ndarray: image binaire (1 canal), 0 pour pixels d'intérêt, 1 pour les autres.
        """
        if hsvImage is None or hsvImage.ndim != 3 or hsvImage.shape[2] != 3:
            raise ValueError("L'image HSV doit être une matrice 3D avec 3 canaux.")

        # Définir les intervalles HSV pour chaque couleur
        if color == Color.BLUE:
            lower = np.array([100, 100, 50])
            upper = np.array([130, 255, 255])
        elif color == Color.YELLOW:
            lower = np.array([20, 100, 100])
            upper = np.array([35, 255, 255])
        elif color == Color.ORANGE:
            lower = np.array([10, 100, 100])
            upper = np.array([20, 255, 255])
        else:
            raise ValueError("Couleur non supportée")

        # Créer le masque binaire inversé (0 pour la couleur cible, 1 ailleurs)
        mask = cv2.inRange(hsvImage, lower, upper)
        binaryImage = np.where(mask == 255, 0, 1).astype(np.uint8)

        return binaryImage

    def medianFilter(self, binaryImage: np.ndarray, maskSize: int = 1) -> np.ndarray:
        """
        Applique un filtre médian sur une image binaire.

        Params:
            binaryImage (np.ndarray): matrice binaire 2D.
            maskSize (int): taille du masque du filtre. Par défaut, maskSize = 1.

        Returns:
            np.ndarray: image filtrée par le filtre médian.
        """
        if binaryImage is None or binaryImage.ndim != 2:
            raise ValueError("L'image binaryImage doit être une matrice 2D.")

        # Calcul de la taille du masque du filtre médian
        kernel_size = 2 * maskSize + 1  # Taille du noyau du filtre

        # Appliquer le filtre médian avec la taille du noyau
        filtedImage = cv2.medianBlur(binaryImage, kernel_size)

        return filtedImage
