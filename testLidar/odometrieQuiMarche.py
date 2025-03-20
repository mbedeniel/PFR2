import numpy as np
import time
import matplotlib.pyplot as plt
from rplidar import RPLidar
from icp import icp 

# --- CONFIGURATION LIDAR ---
PORT_NAME = "/dev/cu.SLAB_USBtoUART"  # ⚠️ Modifier selon le port réel du LIDAR
lidar = RPLidar(PORT_NAME, baudrate=115200)

# --- FONCTIONS UTILES ---
def polaire_to_cartesien(scan):

    angles = []
    distances = []
    
    for s in scan:
        angles.append(s[1])
        distances.append(s[2])
    
    
    angles = np.radians(np.array(angles))
    distances = np.array(distances)

    # Conversion en coordonnées cartésiennes (x, y)
    x_points = distances * np.cos(angles)
    y_points = distances * np.sin(angles)
    

    return np.vstack((x_points, y_points)).T  

def extract_transformation(scan1, scan2):
    """
    Fonction pour extraire la transformation entre deux scans.
    Calcule la rotation et la translation à partir des scans en coordonnées cartésiennes.
    """
    # Conversion des scans en coordonnées cartésiennes
    scan1_cart = polaire_to_cartesien(scan1)
    scan2_cart = polaire_to_cartesien(scan2)

    # Vérifie que les deux scans ont le même nombre de points
    if scan1_cart.shape != scan2_cart.shape:
        min_len = min(scan1_cart.shape[0], scan2_cart.shape[0])
        scan1_cart = scan1_cart[:min_len]
        scan2_cart = scan2_cart[:min_len]

    # Appel de l'ICP pour obtenir la transformation
    T, distances, iterations = icp(scan1_cart, scan2_cart, max_iterations=50, tolerance=0.0001)

    # Calcul de la rotation (theta) et de la translation
    theta = np.arctan2(T[1, 0], T[0, 0]) * 180 / np.pi  # Conversion de la rotation en degrés
    translation = np.linalg.norm(T[:2, 2])  # Calcul de la norme du vecteur de translation

    return theta, translation, T

# --- INITIALISATION AFFICHAGE ---
plt.ion()
fig, ax = plt.subplots()
ax.set_xlim(-500, 500)
ax.set_ylim(-500, 500)

# --- BOUCLE PRINCIPALE ---
scan_counter = 0
previous_scan = None

try:
    print(" Initialisation du LIDAR...")
    lidar.stop()
    lidar.stop_motor()
    time.sleep(1)

    lidar.start_motor()
    time.sleep(2)
    print(" LIDAR prêt !")

    for scan in lidar.iter_scans():
        scan_counter += 1
        
        lidar.stop()
        time.time(0.5)
        lidar.start()


        if previous_scan is None:
            previous_scan = scan
            continue

        # Estimer transformation avec ICP
        theta, translation, T = extract_transformation(previous_scan, scan)

        print(f" Translation: {translation:.2f} mm,  Rotation: {theta:.2f}°")

        # Convertir les scans en coordonnées cartésiennes
        scan1_cart = polaire_to_cartesien(previous_scan)
        scan2_cart = polaire_to_cartesien(scan)

        # Transformation du scan précédent pour vérification
        scan1_transformed = np.dot(T[:2, :2], scan1_cart.T).T + T[:2, 2]

        # Affichage
        ax.cla()
        ax.set_xlim(-500, 500)
        ax.set_ylim(-500, 500)
        ax.scatter(scan1_cart[:, 0], scan1_cart[:, 1], s=1, c='red', label='Scan précédent')
        ax.scatter(scan2_cart[:, 0], scan2_cart[:, 1], s=1, c='blue', label='Scan actuel')
        ax.scatter(scan1_transformed[:, 0], scan1_transformed[:, 1], s=1, c='green', label='Scan vérif')
        ax.legend(loc='upper right')
        plt.draw()
        plt.pause(0.1)

        previous_scan = scan  # Mise à jour du scan précédent

except Exception as e:
    print(f" Erreur: {e}")

finally:
    lidar.stop()
    lidar.stop_motor()
    lidar.disconnect()
    print(" LIDAR arrêté.")
