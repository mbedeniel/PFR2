import numpy as np
import time
import matplotlib.pyplot as plt
from rplidar import RPLidar
from icp import icp  # Utilisation de l'implémentation ICP que tu as fournie
import traceback
from scipy.spatial import cKDTree

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

def cartesien_to_polaire(points):
    x_points = points[:, 0]
    y_points = points[:, 1]

    # Calcul de la distance
    distances = np.sqrt(x_points**2 + y_points**2)

    # Calcul de l'angle en degrés
    angles = np.degrees(np.arctan2(y_points, x_points))

    # Construction du scan formaté comme un scan LIDAR [(qualité, angle, distance)]
    scan_polaire = np.vstack((np.zeros_like(angles), angles, distances)).T  # Qualité mise à 0

    return scan_polaire


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
    T, distances, iterations = icp(scan1_cart, scan2_cart, max_iterations=100, tolerance=0.00001)
    
    # Calcul de la rotation (theta) et de la translation
    theta = np.arctan2(T[1, 0], T[0, 0]) * 180 / np.pi  # Conversion de la rotation en degrés
    translation = np.linalg.norm(T[:2, 2])  # Calcul de la norme du vecteur de translation
    
    if (translation < 2 and translation > -2) or (theta < 0.8 and theta > -0.8):
        #print("La rotation est de : ", theta)
        #print("La translation est de : ", translation)
        print("Le lidar n'a pas bougé")
        T = np.identity(3)
    else: 
        print("le lidar a avancé de : ", np.around(translation), " mm")
        print("et a tourné de : ", np.around(theta), " d°")
    
    return T

def filter_and_cluster_points(points, threshold=10.0):
    """
    Regroupe les points proches les uns des autres.
    Utilise cKDTree pour trouver les points proches dans un voisinage.
    """
    if len(points) == 0:
        return points
    
    tree = cKDTree(points)
    clusters = tree.query_ball_tree(tree, threshold)

    filtered_points = []
    for cluster in clusters:
        cluster_points = np.mean(points[cluster], axis=0)  # Calcul du centre du cluster
        filtered_points.append(cluster_points)
    
    return np.array(filtered_points)

# --- INITIALISATION AFFICHAGE ---
plt.ion()
fig, ax = plt.subplots()
ax.set_xlim(-1500, 1500)
ax.set_ylim(-1500, 1500)

# --- BOUCLE PRINCIPALE ---
scan_counter = 0
previous_scan = None
init_scan = None

pos_robot = [[0, 0]]
all_points = []  # Liste pour stocker tous les points observés
global_position = np.array([0.0, 0.0], dtype=np.float64)  # Position globale initiale du LIDAR
T_cumul = np.identity(3)  # Matrice de transformation cumulative, initialisée à la matrice identité

# --- MATRICE DE TRANSFORMATION ---
transformation_history = []  # Liste pour stocker les transformations cumulées

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
        

        if scan_counter % 150 != 0:
            continue

        if previous_scan is None:
            init_scan = scan
            previous_scan = scan
            continue

        # Estimer transformation avec ICP
        T = extract_transformation(previous_scan, scan)

        # Appliquer la transformation cumulée à chaque scan
        
        
        
        
        T_cumul = T @ T_cumul 

        T_inverse = np.linalg.pinv(T_cumul)

        scan_cart = polaire_to_cartesien(scan)

        # Appliquer la transformation inversée aux points du scan
        transformed_points = np.dot(np.hstack([scan_cart, np.ones((scan_cart.shape[0], 1))]), T_inverse.T)[:, :2]

        transformed_scan = cartesien_to_polaire(transformed_points)
        
        # Extraire la transformation entre init_scan et les points transformés
        T_transformed = extract_transformation(init_scan, transformed_scan)
        
        theta = np.arctan2(T_transformed[1, 0], T_transformed[0, 0]) * 180 / np.pi  # Conversion de la rotation en degrés
        translation = np.linalg.norm(T_transformed[:2, 2])  # Calcul de la norme du vecteur de translation
        
        if (translation < 2 and translation > -2) or (theta < 0.8 and theta > -0.8):
            # Ajouter les points transformés à la liste globale
            all_points.extend(transformed_points)

            # Filtrer les points proches
            filtered_points = filter_and_cluster_points(np.array(all_points))

            previous_scan = scan  # Mise à jour du scan précédent
            
            pos_robot = np.dot(np.hstack([pos_robot, np.ones((len(pos_robot), 1))]), T_inverse.T)[:, :2]
        else : 
            
            print("Le scan n'est pas similaire")
            print("Il est donc ignoré")
            T_cumul = np.linalg.pinv(T) @ T_cumul 
        
        
        
        # Affichage : vider l'axe à chaque itération pour actualiser l'affichage
        ax.cla()
        ax.set_xlim(-600, 600)
        ax.set_ylim(-600, 600)
        
        ax.scatter(scan_cart[:, 0], scan_cart[:, 1], s=1, c='red', label='Scan actuel')
        ax.scatter(filtered_points[:, 0], filtered_points[:, 1], s=1, c='blue', label='Carte')

        ax.scatter(pos_robot[0][0], pos_robot[0][1], s=20, color='green', label='Position du robot')
        ax.legend(loc='upper right')
        plt.draw()
        plt.pause(0.1)

        

except Exception as e:
    print(f"Erreur: {e}")
    traceback.print_exc()

finally:
    lidar.stop()
    lidar.stop_motor()
    lidar.disconnect()
    print("LIDAR arrêté.")

    # Afficher l'historique des transformations
    print("\nHistorique des transformations cumulées :")
    for i, T in enumerate(transformation_history):
        print(f"Transformation {i}:")
        print(T)
