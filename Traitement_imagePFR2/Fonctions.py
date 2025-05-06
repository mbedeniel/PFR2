import os
import cv2

def photographer(config=None, path=None):
    # Valeurs par défaut
    default_config = {
        "width": 640,
        "height": 480,
        "autofocus": True,
        "name": "image",
        "extension": ".jpg"
    }
    
    # Mise à jour des valeurs par défaut avec les valeurs fournies
    if config:
        default_config.update(config)
    
    # Récupération des paramètres
    width = default_config["width"]
    height = default_config["height"]
    name = default_config["name"]
    extension = default_config["extension"]
    
    # Définition du chemin d'enregistrement
    save_path = path if path else os.getcwd()
    image_path = os.path.join(save_path, f"{name}{extension}")
    
    # Ouverture de la caméra (indice 0 pour la caméra par défaut)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Erreur lors de l'ouverture de la caméra")
        return None
    
    # Configuration de la résolution de l'image
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    
    # Capture de l'image
    ret, frame = cap.read()
    
    if ret:
        cv2.imwrite(image_path, frame)  # Sauvegarder l'image
        cap.release()
        return image_path
    else:
        print("Erreur lors de la capture de l'image.")
        cap.release()
        return None

# Exemple d'utilisation
if __name__ == "__main__":
    path = "C:/Users/msi/Desktop/Traitement image PFR2"  # Chemin de destination
    config = {
        "width": 1280,
        "height": 720,
        "autofocus": True,
        "name": "photo_test",
        "extension": ".png"
    }
    
    image_path = photographer(config=config, path=path)
    
    # Vérification si l'image est bien enregistrée
    if image_path and os.path.exists(image_path):
        print(f"L'image est bien enregistrée à : {image_path}")
        os.system(f"start {image_path}")  # Ouvre l'image sous Windows
    else:
        print("L'image n'a pas été trouvée.")


