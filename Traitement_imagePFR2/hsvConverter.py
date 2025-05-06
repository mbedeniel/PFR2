import cv2
import os
import numpy as np

def hsvConverter(rgbImage):
    """
    Convertit une image RGB (3, Hauteur, largeur) en HSV (3, H, L)
    """
    rgbImage_cv = np.transpose(rgbImage, (1, 2, 0))  
    
    # Convertir en HSV
    hsv_cv = cv2.cvtColor(rgbImage_cv, cv2.COLOR_RGB2HSV)
    
    # Repasser en (3, H, W)
    hsvImage = np.transpose(hsv_cv, (2, 0, 1))  
    
    return hsvImage

input_folder = "images"
output_folder = "images_hsv"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

for filename in os.listdir(input_folder):
    if filename.lower().endswith((".jpg", ".jpeg", ".png")):
        image_path = os.path.join(input_folder, filename)
        bgr_image = cv2.imread(image_path)

        if bgr_image is None:
            print(f"Impossible de charger {filename}")
            continue

        rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)

        rgb_image_transposed = np.transpose(rgb_image, (2, 0, 1))

        # dimensions RGB
        print(f"{filename} - RGB shape (R, G, B): {rgb_image_transposed.shape}")

        # Conversion en HSV
        hsv_image = hsvConverter(rgb_image_transposed)

        # dimensions HSV
        print(f"{filename} - HSV shape (H, S, V): {hsv_image.shape}")

        hsv_for_saving = np.transpose(hsv_image, (1, 2, 0))  # (3, H, W) to (H, W, 3)
        output_path = os.path.join(output_folder, f"hsv_{filename}")
        cv2.imwrite(output_path, hsv_for_saving)
        print(f"Image HSV enregistrée sous '{output_path}'")

print("Conversion terminée")
