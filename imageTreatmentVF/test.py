import matplotlib
import numpy as np
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
from ImageManager import ImageManager
from Color import Color

# Initialisation
image_manager = ImageManager()
image_path = './image/cubeYBO.jpg'
image_manager.path = image_path
image_manager.uploader()

# Affichage de l'image RGB
plt.figure(figsize=(16, 30))
plt.subplot(7, 4, 1)
plt.imshow(image_manager.rgbImage)
plt.title("rgbImage")
plt.axis('off')

# HSV
image_manager.hsvConverter()


### === BLEU ===
image_manager.binarizer(Color.BLUE)
image_manager.medianFilter(maskSize=7)

plt.subplot(7, 4, 5)
plt.imshow(image_manager.filteredImage, cmap='gray')
plt.title("filteredImageBLUE")
plt.axis('off')

# Segmentation
image_manager.segmentation()

# Calculer les tailles des segments
segment_sizes = [np.count_nonzero(seg) for seg in image_manager.segmentedImage]

# Trier les segments par taille (du plus grand au plus petit)
sorted_segments = sorted(zip(segment_sizes, image_manager.segmentedImage), key=lambda x: x[0], reverse=True)

# Afficher les 2 plus grands segments
plt.figure(figsize=(16, 12))
for i, (size, seg) in enumerate(sorted_segments[:2]):
    plt.subplot(1, 2, i + 1)
    plt.imshow(seg, cmap='gray')
    plt.title(f"Largest Segment {i + 1} ({size} pixels)")
    plt.axis('off')

plt.tight_layout()
plt.show()



### === ORANGE ===
image_manager.binarizer(Color.ORANGE)
image_manager.medianFilter(maskSize=7)

plt.subplot(7, 4, 13)
plt.imshow(image_manager.filteredImage, cmap='gray')
plt.title("filteredImageORANGE")
plt.axis('off')

# Segmentation
image_manager.segmentation()

# Calculer les tailles des segments
segment_sizes = [np.count_nonzero(seg) for seg in image_manager.segmentedImage]

# Trier les segments par taille (du plus grand au plus petit)
sorted_segments = sorted(zip(segment_sizes, image_manager.segmentedImage), key=lambda x: x[0], reverse=True)

# Afficher les 2 plus grands segments
plt.figure(figsize=(16, 12))
for i, (size, seg) in enumerate(sorted_segments[:2]):
    plt.subplot(1, 2, i + 1)
    plt.imshow(seg, cmap='gray')
    plt.title(f"Largest Segment {i + 1} ({size} pixels)")
    plt.axis('off')

plt.tight_layout()
plt.show()



### === JAUNE ===
image_manager.binarizer(Color.YELLOW)
image_manager.medianFilter(maskSize=7)

plt.subplot(7, 4, 21)
plt.imshow(image_manager.filteredImage, cmap='gray')
plt.title("filteredImageYELLOW")
plt.axis('off')

# Segmentation
image_manager.segmentation()

# Calculer les tailles des segments
segment_sizes = [np.count_nonzero(seg) for seg in image_manager.segmentedImage]

# Trier les segments par taille (du plus grand au plus petit)
sorted_segments = sorted(zip(segment_sizes, image_manager.segmentedImage), key=lambda x: x[0], reverse=True)

# Afficher les 2 plus grands segments
plt.figure(figsize=(16, 12))
for i, (size, seg) in enumerate(sorted_segments[:2]):
    plt.subplot(1, 2, i + 1)
    plt.imshow(seg, cmap='gray')
    plt.title(f"Largest Segment {i + 1} ({size} pixels)")
    plt.axis('off')

plt.tight_layout()
plt.show()


plt.tight_layout()
plt.show()
