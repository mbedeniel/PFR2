from ImageManager import ImageManager
from Color import Color
import numpy as np
import cv2

# Initialisation
image_manager = ImageManager()

# leave resources
image_manager.process_killer()

# take image
image_manager.photographer()

# Upload image
image_manager.uploader()

# HSV
image_manager.hsv_converter()

# Filtering and thresholding

######################################################### BLUE #########################################################
image_manager.binarizer(Color.BLUE)
image_manager.median_filter(7)
binaryImage = image_manager.binary_image * 255
binaryImage = binaryImage.astype(np.uint8)
cv2.imwrite('filteredImageBLUE.jpg', binaryImage)

# Segmentation
image_manager.segmentation_manager()
print("Number of BLUE object : ",len(image_manager.segmented_image))
for idx, img in enumerate(image_manager.segmented_image, 1):
    # Arrange pixel
    segmentImage = (1 - img) * 255
    segmentImage = segmentImage.astype(np.uint8)
    # Save
    cv2.imwrite(f"segmentImageBLUE{idx}.jpg", segmentImage)

######################################################### ORANGE #########################################################
image_manager.binarizer(Color.ORANGE)
image_manager.median_filter(7)
binaryImage = image_manager.binary_image * 255
binaryImage = binaryImage.astype(np.uint8)
cv2.imwrite('filteredImageORANGE.jpg', binaryImage)

# Segmentation
image_manager.segmentation_manager()
print("Number of ORANGE object : ",len(image_manager.segmented_image))
for idx, img in enumerate(image_manager.segmented_image, 1):
    # Arrange pixel
    segmentImage = (1 - img) * 255
    segmentImage = segmentImage.astype(np.uint8)
    # Save
    cv2.imwrite(f"segmentImageORANGE{idx}.jpg", segmentImage)

######################################################### YELLOW #########################################################
image_manager.binarizer(Color.YELLOW)
image_manager.median_filter(7)
binaryImage = image_manager.binary_image * 255
binaryImage = binaryImage.astype(np.uint8)
cv2.imwrite('filteredImageYELLOW.jpg', binaryImage)

# Segmentation
image_manager.segmentation_manager()
print("Number of YELLOW object : ",len(image_manager.segmented_image))
for idx, img in enumerate(image_manager.segmented_image, 1):
    # Arrange pixel
    segmentImage = (1 - img) * 255
    segmentImage = segmentImage.astype(np.uint8)
    # Save
    cv2.imwrite(f"segmentImageYELLOW{idx}.jpg", segmentImage)
image_manager.object_analyser()

# launch imageTreatment
image_manager.start()

# print of objects
print(image_manager.objects)


