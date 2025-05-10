import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
from ImageManager import ImageManager
from Color import Color
from StructuredElement import StructuredElement

# Initialisation
image_manager = ImageManager()
image_path = './image/img5.jpeg'
image_manager.path = image_path
image_manager.uploader()

# Affichage de l'image RGB
plt.figure(figsize=(16, 12))
plt.subplot(3, 4, 1)
plt.imshow(image_manager.rgbImage)
plt.title("rgbImage")
plt.axis('off')

# HSV
image_manager.hsvConverter()
plt.subplot(3, 4, 2)
plt.imshow(image_manager.hsvImage)
plt.title("hsvImage")
plt.axis('off')

# === BLEU ===
image_manager.binarizer(Color.BLUE)
plt.subplot(3, 4, 3)
plt.imshow(image_manager.binaryImage, cmap='gray')
plt.title("binaryImageBLUE")
plt.axis('off')

image_manager.medianFilter(maskSize=7)
plt.subplot(3, 4, 4)
plt.imshow(image_manager.medianFiltedImage, cmap='gray')
plt.title("medianFiltedBLUE")
plt.axis('off')

image_manager.erosionFilter(StructuredElement.CIRCLE, elementSize=7)
plt.subplot(3, 4, 5)
plt.imshow(image_manager.erosionFiltedImage, cmap='gray')
plt.title("erosionBLUE (circle, size=2)")
plt.axis('off')

# === ORANGE ===
image_manager.binarizer(Color.ORANGE)
plt.subplot(3, 4, 6)
plt.imshow(image_manager.binaryImage, cmap='gray')
plt.title("binaryImageORANGE")
plt.axis('off')

image_manager.medianFilter(maskSize=7)
plt.subplot(3, 4, 7)
plt.imshow(image_manager.medianFiltedImage, cmap='gray')
plt.title("medianFiltedORANGE")
plt.axis('off')

image_manager.erosionFilter(StructuredElement.CIRCLE, elementSize=7)
plt.subplot(3, 4, 8)
plt.imshow(image_manager.erosionFiltedImage, cmap='gray')
plt.title("erosionORANGE (circle, size=2)")
plt.axis('off')

# === JAUNE ===
image_manager.binarizer(Color.YELLOW)
plt.subplot(3, 4, 9)
plt.imshow(image_manager.binaryImage, cmap='gray')
plt.title("binaryImageYELLOW")
plt.axis('off')

image_manager.medianFilter(maskSize=7)
plt.subplot(3, 4, 10)
plt.imshow(image_manager.medianFiltedImage, cmap='gray')
plt.title("medianFiltedYELLOW")
plt.axis('off')

image_manager.erosionFilter(StructuredElement.CIRCLE, elementSize=7)
plt.subplot(3, 4, 11)
plt.imshow(image_manager.erosionFiltedImage, cmap='gray')
plt.title("erosionYELLOW (circle, size=2)")
plt.axis('off')

plt.tight_layout()
plt.show()
