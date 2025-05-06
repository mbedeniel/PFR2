import cv2
import numpy as np
def combined_thresholder(hsvImage):
    h, s, v = cv2.split(hsvImage)
    thresholdImage = np.ones_like(h, dtype=np.uint8)

    
    mask_blue = (h >= 100) & (h <= 130) & (s > 50) & (v > 50)
    mask_orange = (h >= 10) & (h <= 20) & (s > 50) & (v > 50)
    mask_yellow = (h >= 20) & (h <= 35) & (s > 50) & (v > 50)

    mask_total = mask_blue | mask_orange | mask_yellow
    thresholdImage[mask_total] = 0  
    return thresholdImage

image = cv2.imread(r'C:\Users\msi\Desktop\Traitement image PFR2\images\test.jpg') # Path de l'image 
if image is None:
    print("Erreur : image non trouvée")
    exit()

image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

result = combined_thresholder(image_hsv) * 255


cv2.imwrite('seuillage.png', result)