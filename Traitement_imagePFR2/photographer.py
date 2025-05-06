import cv2
import os

def photographer(config=None, path="captures"):
    """
    Capture une image depuis la webcam et l'enregistre dans  le dossier captures
    Args:
        config (dict, optional): Paramètres de capture.
        path (str, optional): Dossier de sauvegarde

    Returns:
        str: Chemin absolu de l'image capturée
    """
    default_config = {
        "width": 640,
        "height": 480,
        "autofocus": True,
        "name": "image",
        "extension": ".jpg"
    }

    if config is None:
        config = default_config
    else:
        for key, value in default_config.items():
            config.setdefault(key, value)

    os.makedirs(path, exist_ok=True)

    existing_files = [f for f in os.listdir(path)
                      if f.startswith(config["name"] + "_") and f.endswith(config["extension"])]
    
    existing_numbers = []
    for f in existing_files:
        try:
            num = int(f.split("_")[1].split(".")[0])
            existing_numbers.append(num)
        except:
            pass
    
    next_number = max(existing_numbers) + 1 if existing_numbers else 1
    filename = f"{config['name']}_{next_number}{config['extension']}"
    full_path = os.path.abspath(os.path.join(path, filename))

    # caapture webcam
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config["width"])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config["height"])

    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Impossible de capturer l'image")
        return None

    cv2.imwrite(full_path, frame)
    print(f"Image capturée : {full_path}")
    return full_path

photographer()