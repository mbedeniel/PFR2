import os
import cv2

def uploader(path=None, nameImage=None):
    
    if not nameImage:
        print("Erreur : Le nom de l'image doit être fourni.")
        return None
    
    # Si aucun chemin n'est fourni, utiliser le répertoire courant
    if not path:
        path = os.getcwd()  
    
    
    image_path = os.path.join(path, nameImage)

    if not os.path.exists(image_path):
        print(f"Erreur : L'image '{nameImage}' n'existe pas à l'emplacement spécifié.")
        return None

    image = cv2.imread(image_path)

    if image is None:
        print(f"Erreur : Impossible de lire l'image '{nameImage}'.")
        return None

    rgbImage = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    output_path_original = os.path.join(path, "image_original.jpg")
    output_path_rgb = os.path.join(path, "image_rgb_output.jpg")
    
    cv2.imwrite(output_path_original, image)
    
    # Enregistrer l'image convertie (RGB), il faut la reconvertir en BGR pour l'enregistrer
    cv2.imwrite(output_path_rgb, cv2.cvtColor(rgbImage, cv2.COLOR_RGB2BGR))

    print(f"Les images ont été enregistrées : {output_path_original}, {output_path_rgb}")
    
    # Retourner l'image RGB pour d'autres usages si nécessaire
    return rgbImage

path = r"C:\Users\msi\Desktop\Traitement image PFR2\images"  # Chemin vers le dossier contenant l'image
nameImage = "test.jpg" 

  
rgbImage = uploader(path=path, nameImage=nameImage)
    
   
if rgbImage is not None:
        print("Images traitées avec succès !")
        print(f"Dimensions de l'image RGB : {rgbImage.shape}") 
else:
        print("Échec du chargement de l'image.")
