import os
import subprocess
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
