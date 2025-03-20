import numpy as np
import matplotlib.pyplot as plt
from rplidar import RPLidar, RPLidarException
import time 

# Configuration du port du Lidar
PORT_NAME = "/dev/ttyUSB0"  # Remplacez par le port approprié à votre système
lidar = RPLidar(None, PORT_NAME)

# Configuration de la fenêtre Matplotlib
plt.ion()
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
ax.set_ylim(0, 6000)  # Distance maximale en mm
ax.set_title("Visualisation RPLidar en temps réel")
scatter = ax.scatter([], [], s=5, c='red')  # Initialisation des points

try:
    iterator = lidar.iter_scans()
    erreur = 0
    while True:
        try:
            scan = next(iterator)
            angles = np.radians([m[1] for m in scan])  # Conversion en radians
            distances = [m[2] for m in scan]

            scatter.set_offsets(np.c_[angles, distances])
            plt.pause(0.1)  # Pause pour l'affichage en temps réel

        except RPLidarException as e:
            erreur += 1 
            print(f"Erreur lors de la lecture du Lidar : {e}")
            time.sleep(1)
            lidar.clear_input()  # Nettoyage du tampon en cas d'erreur
            time.sleep(1)
            if erreur == 5:
                break
            
except KeyboardInterrupt:
    print("Arrêt du programme par l'utilisateur...")
finally:
    lidar.stop()
    lidar.disconnect()
    print("Lidar déconnecté.")
