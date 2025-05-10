import cv2
import numpy as np
import os
import matplotlib.pyplot as plt


def plot_contour_approximation(image: np.ndarray, epsilon_values: list):
    """
    Affiche l'impact de la variation de l'epsilon sur l'approximation des contours.

    Args:
        image (np.ndarray): Image en niveaux de gris avec l'objet dont on veut détecter les contours.
        epsilon_values (list): Liste des valeurs d'epsilon à tester pour l'approximation des contours.
    """
    # Convertir l'image en niveaux de gris
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Appliquer un seuillage pour obtenir une image binaire
    _, binary_image = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    # Trouver les contours de l'image binaire
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Initialisation de la figure pour l'affichage
    plt.figure(figsize=(12, 8))

    # Afficher l'image originale
    plt.subplot(len(epsilon_values) + 1, 2, 1)
    plt.imshow(binary_image, cmap='gray')
    plt.title("Image Binaire")
    plt.axis('off')

    # Afficher les contours originaux
    plt.subplot(len(epsilon_values) + 1, 2, 2)
    plt.imshow(binary_image, cmap='gray')
    plt.title("Contours originaux")
    plt.axis('off')

    # Affichage des approximations avec différentes valeurs d'epsilon
    for i, epsilon in enumerate(epsilon_values):
        approx_image = np.copy(binary_image)
        for contour in contours:
            # Appliquer l'approximation des contours pour chaque valeur d'epsilon
            approx = cv2.approxPolyDP(contour, epsilon, True)

            # Dessiner l'approximation du contour sur une nouvelle image
            cv2.drawContours(approx_image, [approx], -1, (255, 0, 0), 2)

        # Afficher l'approximation pour la valeur d'epsilon
        plt.subplot(len(epsilon_values) + 1, 2, i * 2 + 3)
        plt.imshow(approx_image, cmap='gray')
        plt.title(f"Approximation epsilon = {epsilon}")
        plt.axis('off')

    # Afficher tous les subplots
    plt.tight_layout()
    plt.show()


# Exemple d'utilisation
if __name__ == "__main__":
    # URL de l'image
    image_url = "https://helpingwithmath.com/wp-content/uploads/2022/03/image-109.png"

    # Télécharger l'image via une requête HTTP (vous pouvez aussi télécharger manuellement l'image)
    import urllib.request

    img_path = 'image/forme.png'
    urllib.request.urlretrieve(image_url, img_path)

    # Charger l'image téléchargée
    image = cv2.imread(img_path)

    if image is None:
        print(f"Erreur : Impossible de charger l'image depuis {img_path}. Vérifiez le chemin du fichier.")
        exit(1)

    # Liste des valeurs epsilon à tester
    epsilon_values = [0.01, 0.04, 0.3, 0.7, 0.9]

    # Appeler la fonction pour afficher les résultats
    plot_contour_approximation(image, epsilon_values)
