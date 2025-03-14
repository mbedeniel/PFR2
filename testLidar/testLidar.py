import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from rplidar import RPLidar

matplotlib.use('TkAgg')

PORT_NAME = "/dev/cu.SLAB_USBtoUART"

lidar = RPLidar(PORT_NAME)  # Teste avec 115200 baud
print("start")
# 🔧 Configuration de la fenêtre Matplotlib
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
ax.set_ylim(0, 6000)  # Distance max en mm
ax.set_title("Visualisation RPLidar en temps réel")


def update_plot():
    for scan in lidar.iter_scans():
        
        angles = np.radians([m[1] for m in scan])  # Conversion en radians
        distances = [m[2] for m in scan]

        ax.clear()
        ax.set_ylim(0, 6000)
        ax.set_title("Visualisation RPLidar en temps réel")
        ax.scatter(angles, distances, s=5, c='red')  # Affichage des points

        plt.pause(0.1)  # Pause pour l'affichage en temps réel

try:
    update_plot()
except KeyboardInterrupt:
    print("Arrêt du programme...")
finally:
    lidar.stop()
    lidar.disconnect()
    print("Lidar déconnecté.")
