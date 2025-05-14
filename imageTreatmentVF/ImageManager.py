import os
import subprocess
import numpy as np
import cv2

from Color import *
from Nature import *


class ImageManager:

    def __init__(self, width: int = 640, height: int = 480, autofocus: bool = True,
                 name: str = 'image', extension: str = '.jpg', path: str = './',
                 rgb_image: np.ndarray = None, hsv_image: np.ndarray = None,
                 binary_image: np.ndarray = None, filtered_image: np.ndarray = None,
                 segmented_image: list = None, objects: list = None):
        self.width = width
        self.height = height
        self.autofocus = autofocus
        self.name = name
        self.extension = extension
        self.path = path

        # Vérification si les images sont fournies, sinon initialisation à des valeurs par défaut (ex: tableau vide ou `None`)
        self.rgb_image = rgb_image if rgb_image is not None else np.array([])
        self.hsv_image = hsv_image if hsv_image is not None else np.array([])
        self.binary_image = binary_image if binary_image is not None else np.array([])
        self.filtered_image = filtered_image if filtered_image is not None else np.array([])
        self.segmented_image = segmented_image if segmented_image is not None else []
        self.objects = objects if objects is not None else []

    def start(self):
        """
            This method start the imageTreatment
        """

        # leave resources
        self.process_killer()

        # take image
        self.photographer()

        # Upload image
        self.uploader()

        # HSV
        self.hsv_converter()

        # detect object
        self.object_analyser()

        # leave resources
        self.process_killer()

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

        self.rgb_image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

    def hsv_converter(self):
        """
        Convertit une image RGB en image HSV.

        Params:
            rgb_image (np.ndarray): image en base RGB (3 canaux).

        Returns: NONE
            np.ndarray: image en base HSV (3 canaux).
        """
        rgb_image = self.rgb_image
        if rgb_image is None or rgb_image.ndim != 3 or rgb_image.shape[2] != 3:
            raise ValueError("L'image RGB doit être une matrice 3D avec 3 canaux.")

        self.hsv_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV)

    def binarizer(self, color: Color):
        """
        Applique un seuillage binaire sur une image HSV en fonction d'une couleur cible.

        Params:
            hsv_image (np.ndarray): image en base HSV (3 canaux).
            color (Color): couleur cible (BLUE, YELLOW, ORANGE).

        Returns: NONE
            np.ndarray: image binaire (1 canal), 0 pour pixels d'intérêt, 1 pour les autres.
        """
        hsv_image = self.hsv_image
        if hsv_image is None or hsv_image.ndim != 3 or hsv_image.shape[2] != 3:
            raise ValueError("L'image HSV doit être une matrice 3D avec 3 canaux.")

        # Définir les intervalles HSV pour chaque couleur
        if color == Color.BLUE:
            lower = np.array([90, 50, 20])  # Hue plus bas, saturation et valeur plus faibles
            upper = np.array([135, 255, 255])  # Hue un peu plus large vers les bleus profonds
        elif color == Color.YELLOW:
            lower = np.array([22, 150, 100])
            upper = np.array([32, 255, 255])
        elif color == Color.ORANGE:
            lower = np.array([10, 150, 100])
            upper = np.array([20, 255, 255])
        else:
            raise ValueError("Couleur non supportée")

        # Créer le masque binaire inversé (0 pour la couleur cible, 1 ailleurs)
        mask = cv2.inRange(hsv_image, lower, upper)

        self.binary_image = np.where(mask == 255, 0, 1).astype(np.uint8)

    def median_filter(self, mask_size: int = 7) :
        """
        Applique un filtre médian sur une image binaire.

        Params:
            binary_image (np.ndarray): matrice binaire 2D.
            maskSize (int): taille du masque du filtre. Par défaut, maskSize = 7.

        Returns: NONE
            np.ndarray: image filtrée par le filtre médian.
        """
        binary_image = self.binary_image
        if binary_image is None or binary_image.ndim != 2:
            raise ValueError("L'image binary_image doit être une matrice 2D.")

        # Calcul de la taille du masque du filtre médian
        kernel_size = 2 * mask_size + 1  # Taille du noyau du filtre

        # Appliquer le filtre médian avec la taille du noyau

        self.filtered_image = cv2.medianBlur(binary_image, kernel_size)

    def segmentation_manager(self):
        """
        Segmente une image binaire en régions distinctes à l'aide de l'algorithme Watershed.

        Parameters:
            binary_image (np.ndarray): image binaire 2D (fond = 1, objets = 0)

        Returns: NONE
            segmentedImage (List[np.ndarray]): liste de matrices binaires, chaque matrice représentant une zone segmentée
        """

        filtered_image = self.filtered_image
        # Inverser l'image car Watershed travaille avec fond=0, objets>0
        inverted = np.uint8(1 - filtered_image)

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

        self.segmented_image = []
        # Générer une image binaire pour chaque label > 1
        nbMin = (self.width * self.height) * 0.03
        # 3% of the total size of the image
        for label in range(2, markers.max() + 1):
            region = np.where(markers == label, 1, 0).astype(np.uint8)
            if np.count_nonzero(region) > 1:
                self.segmented_image.append(region)

    def object_analyser(self):
        """
        Identifie la forme principale dans self.filteredImage : carré, cercle ou forme inconnue.

        Returns:
            str: Type de la forme détectée ("carré", "cercle", "inconnue").
        """
        self.objects = []

        for color in Color:

            if color != Color.NONE:

                self.binarizer(color)
                self.median_filter()
                self.segmentation_manager()

                for binary_image in self.segmented_image :
                    ####### Orientation of the object
                    # +1 => object a the right
                    # -1 => object a the left
                    cx, cy = self.centroid_getter(binary_image)
                    if cx is None:
                        position = None
                    elif cx < self.width / 2:
                        position = +1
                    else:
                        position = -1

                    # relation entre angle et pixel

                    # Trois points (x, y)
                    x = [0, self.width/2, self.width]
                    y = [33, 0, -33]

                    # Ajustement polynômial de degré 2
                    coeffs = np.polyfit(x, y, deg=2)

                    # Création du polynôme à partir des coefficients
                    polynome = np.poly1d(coeffs)

                    if binary_image is None or binary_image.ndim != 2:
                        raise ValueError("filteredImage doit être une image binaire 2D.")

                    # Trouver les contours
                    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                    if not contours:
                        self.objects.append(
                            {
                                "color": color,
                                "nature": Nature.NONE,
                                "position": position,
                                "angle" : polynome(cx)
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
                                    "color" : color,
                                    "nature" : Nature.CUBE,
                                    "position" : position,
                                    "angle": polynome(cx)
                                }
                            )
                        elif len(approx) >= 7:
                            self.objects.append(
                                {
                                    "color": color,
                                    "nature": Nature.BALL,
                                    "position": position,
                                    "angle": polynome(cx)
                                }
                            )
                        else:
                            self.objects.append(
                                {
                                    "color": color,
                                    "nature": Nature.NONE,
                                    "position": position,
                                    "angle": polynome(cx)
                                }
                            )

    @staticmethod
    def centroid_getter(binary_image):
        moments = cv2.moments(binary_image)
        if moments["m00"] != 0:
            cx = int(moments["m10"] / moments["m00"])
            cy = int(moments["m01"] / moments["m00"])  # Calcul de cy
            return cx, cy
        else:
            return None, None

    @staticmethod
    def process_killer():
        try:
            # Récupérer les PIDs des processus qui utilisent /dev/video0
            result = subprocess.check_output(
                "lsof /dev/video0 | awk 'NR>1 {print $2}'",
                shell=True,
                text=True
            )
            pids = result.strip().split('\n')
            # Vérifier qu'il y a bien des PID à tuer
            if pids and pids != ['']:
                subprocess.run(['sudo', 'kill', '-9'] + pids, check=True)
        except subprocess.CalledProcessError:
            pass  # Silencieusement ignorer si aucun processus ne tient la caméra

