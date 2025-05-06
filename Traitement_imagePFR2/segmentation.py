import numpy as np

def segmentImage(thresholdImage):
    thresholdImage = np.array(thresholdImage, dtype=int)
    if thresholdImage.ndim != 1:
        raise ValueError("thresholdImage doit être une matrice unidimensionnelle.")

    segments = []
    current_segment = []
    in_zone = False

    for pixel in thresholdImage:
        if pixel == 0:
            current_segment.append(0)
            in_zone = True
        else:
            if in_zone:
                segments.append(np.array(current_segment, dtype=int))
                current_segment = []
                in_zone = False

    # Ne pas oublier d'ajouter le dernier segment si l'image se termine par une zone
    if in_zone and current_segment:
        segments.append(np.array(current_segment, dtype=int))

    return segments

image = [1, 0, 0, 1, 1, 0, 0, 0, 1, 0]
segments = segmentImage(image)

for i, segment in enumerate(segments):
    print(f"Zone {i+1} :", segment)

