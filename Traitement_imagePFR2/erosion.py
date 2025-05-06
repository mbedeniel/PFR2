import numpy as np

def erosionFilter(thresholdImage, elementType):
    # Convertir en tableau numpy 1D
    thresholdImage = np.array(thresholdImage, dtype=int)
    if thresholdImage.ndim != 1:
        raise ValueError("thresholdImage doit être une matrice unidimensionnelle.")

    # Définir la taille de l'élément structurant selon le type
    if elementType == "SQUARE":
        struct_size = 3
    elif elementType == "RECTANGLE":
        struct_size = 5
    elif elementType == "CERCLE":
        struct_size = 3  
    else:
        raise ValueError("elementType doit être 'SQUARE', 'RECTANGLE' ou 'CERCLE'.")

    half = struct_size // 2
    padded_image = np.pad(thresholdImage, (half, half), mode='constant', constant_values=1)

    
    filteredImage = []
    for i in range(len(thresholdImage)):
        window = padded_image[i:i + struct_size]
        if np.all(window == 0):
            filteredImage.append(0)
        else:
            filteredImage.append(1)

    return np.array(filteredImage, dtype=int)

image = [1, 0, 0, 0, 1, 0, 0, 1]
result = erosionFilter(image, "SQUARE")
print(result)

