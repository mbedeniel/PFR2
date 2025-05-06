import numpy as np

def medianFilter(thresholdImage, maskSize=1):
    
    thresholdImage = np.array(thresholdImage)
    if thresholdImage.ndim != 1:
        raise ValueError("thresholdImage doit être une matrice unidimensionnelle.")

   
    k = 2 * maskSize + 1  
    half_k = maskSize     
    padded_image = np.pad(thresholdImage, (half_k, half_k), mode='edge')

  
    filteredImage = []
    for i in range(len(thresholdImage)):
        window = padded_image[i:i + k]
        median = np.median(window)
        filteredImage.append(int(median))

    return np.array(filteredImage)


filtered = medianFilter( 'test.jpg' , 1)
print(filtered)  


