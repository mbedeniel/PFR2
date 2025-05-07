import os
import subprocess
from typing import Optional, Dict, Any
import os
import subprocess
import numpy as np
import cv2
from typing import Optional, Dict, Any

def photographer(config: Optional[Dict[str, Any]] = None, path: Optional[str] = None) -> str:
    """
    Capture une image à l'aide de la commande libcamera-still.

    Params:
        config (dict, optional): Configuration de la capture:
            - width (int): largeur de l'image en pixels (par défaut 640)
            - height (int): hauteur de l'image en pixels (par défaut 480)
            - autofocus (bool): activer l'autofocus (par défaut True)
            - name (str): nom de fichier sans extension (par défaut 'image')
            - extension (str): extension du fichier (par défaut '.jpg')
        path (str, optional): chemin absolu ou relatif du dossier de sortie
            (par défaut dossier courant).

    Returns:
        str: Chemin absolu complet vers l'image capturée.
    """
    # Valeurs par défaut
    default_cfg = {
        'width': 640,
        'height': 480,
        'autofocus': True,
        'name': 'image',
        'extension': '.jpg'
    }
    # Fusionner la config utilisateur
    cfg = default_cfg.copy()
    if config:
        cfg.update(config)

    # Préparer le dossier de sortie
    output_dir = path or os.getcwd()
    os.makedirs(output_dir, exist_ok=True)

    # Construire le nom de fichier complet
    filename = f"{cfg['name']}{cfg['extension']}"
    full_path = os.path.abspath(os.path.join(output_dir, filename))

    # Construire la commande libcamera-still
    cmd = [
        'libcamera-still',
        '-t', '0',
        '-w', str(cfg['width']),
        '-h', str(cfg['height']),
        '-o', full_path
    ]
    # Gérer l'autofocus
    if cfg['autofocus']:
        cmd.append('--autofocus-on-capture')
    # Si autofocus est False, on n'ajoute pas le flag et on utilise le focus fixe

    # Exécuter la commande
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Erreur lors de la capture de l'image: {e}")

    return full_path

def uploader(nameImage: str, path: Optional[str] = None) -> np.ndarray:
    """
    Charge une image RGB à partir du disque à l'aide d'OpenCV.

    Params:
        nameImage (str): nom du fichier image avec extension (ex: 'photo.jpg')
        path (str, optional): chemin vers le dossier contenant l'image (par défaut dossier courant)

    Returns:
        np.ndarray: matrice 3D représentant l'image en RGB
    """
    # Déterminer le chemin absolu du fichier image
    image_dir = path or os.getcwd()
    image_path = os.path.join(image_dir, nameImage)

    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image introuvable à l'emplacement spécifié : {image_path}")

    # Lire l'image avec OpenCV (en BGR par défaut)
    bgr_image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if bgr_image is None:
        raise RuntimeError(f"Échec du chargement de l'image avec OpenCV : {image_path}")

    # Convertir BGR -> RGB
    rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)

    return rgb_image

def hsvConverter(rgbImage: np.ndarray) -> np.ndarray:
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

