from ImageManager import ImageManager
from Color import Color
import numpy as np
import cv2

# Initialisation
image_manager = ImageManager()

# Capture de l'image
#image_manager.photographer()

image_manager.path = "./image/cubeYBO.jpg"

# Upload image
image_manager.uploader()
cv2.imwrite("uploadImage.jpg", cv2.cvtColor(image_manager.rgbImage, cv2.COLOR_RGB2BGR))

# HSV
image_manager.hsvConverter()

# Filtering and thresholding

######################################################### BLUE #########################################################
image_manager.binarizer(Color.BLUE)
image_manager.medianFilter(7)

binaryImage = image_manager.binaryImage * 255
binaryImage = binaryImage.astype(np.uint8)

cv2.imwrite('filteredImageBLUE.jpg', binaryImage)

# Segmentation
image_manager.segmentation()

print("Number of BLUE object : ",len(image_manager.segmentedImage))
for idx, img in enumerate(image_manager.segmentedImage, 1):
    # Arrange pixel
    segmentImage = (1 - img) * 255
    segmentImage = segmentImage.astype(np.uint8)
    # Save
    cv2.imwrite(f"segmentImageBLUE{idx}.jpg", segmentImage)

######################################################### ORANGE #########################################################
image_manager.binarizer(Color.ORANGE)
image_manager.medianFilter(7)

binaryImage = image_manager.binaryImage * 255
binaryImage = binaryImage.astype(np.uint8)

cv2.imwrite('filteredImageORANGE.jpg', binaryImage)

# Segmentation
image_manager.segmentation()

print("Number of ORANGE object : ",len(image_manager.segmentedImage))
for idx, img in enumerate(image_manager.segmentedImage, 1):
    # Arrange pixel
    segmentImage = (1 - img) * 255
    segmentImage = segmentImage.astype(np.uint8)
    # Save
    cv2.imwrite(f"segmentImageORANGE{idx}.jpg", segmentImage)

######################################################### YELLOW #########################################################
image_manager.binarizer(Color.YELLOW)
image_manager.medianFilter(7)

binaryImage = image_manager.binaryImage * 255
binaryImage = binaryImage.astype(np.uint8)

cv2.imwrite('filteredImageYELLOW.jpg', binaryImage)

# Segmentation
image_manager.segmentation()

print("Number of YELLOW object : ",len(image_manager.segmentedImage))
for idx, img in enumerate(image_manager.segmentedImage, 1):
    # Arrange pixel
    segmentImage = (1 - img) * 255
    segmentImage = segmentImage.astype(np.uint8)
    # Save
    cv2.imwrite(f"segmentImageYELLOW{idx}.jpg", segmentImage)


