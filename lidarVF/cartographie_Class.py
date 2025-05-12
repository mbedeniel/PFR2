import numpy as np
import time
import traceback
from rplidar import RPLidar
from icp import icp
from scipy.spatial import cKDTree

import matplotlib
matplotlib.use('Agg')  # Empêche l'affichage de la fenêtre matplotlib
import matplotlib.pyplot as plt
import threading

#-------------------------------------------------------------------
"""
install to windows: 
pip install --upgrade numpy scipy matplotlib rplidar scikit-learn

install to linux/mac:
python3 -m pip install --upgrade numpy scipy matplotlib rplidar scikit-learn

"""
#-------------------------------------------------------------------


class TransformationUtils:
    """
    Classe utilitaire pour les transformations entre les coordonnées
    polaires et cartésiennes, et pour le calcul de transformations
    entre deux scans LIDAR.
    """

    @staticmethod
    def polaire_to_cartesien(scan):
        """
        Convertit un scan LIDAR (angle, distance) en coordonnées cartésiennes (x, y).
        """
        angles = np.radians([s[1] for s in scan])
        distances = np.array([s[2] for s in scan])
        x = distances * np.cos(angles)
        y = distances * np.sin(angles)
        return np.vstack((x, y)).T

    @staticmethod
    def cartesien_to_polaire(points):
        """
        Convertit des points cartésiens (x, y) en format de scan LIDAR (qualité, angle, distance).
        points : np.array de forme (N, 2)
        Retourne un tableau de forme (N, 3) avec (qualité=0, angle, distance).
        """
        x, y = points[:, 0], points[:, 1]
        distances = np.sqrt(x**2 + y**2)
        angles = np.degrees(np.arctan2(y, x))
        return np.vstack((np.zeros_like(angles), angles, distances)).T

    @staticmethod
    def extract_transformation(scan1, scan2):
        """
        Extrait la matrice de transformation (rotation + translation)
        entre deux scans en utilisant l'algorithme ICP.
        scan1 : np.array de forme (N, 3) - Scan de référence
        scan2 : np.array de forme (N, 3) - Scan à aligner
        Retourne la matrice de transformation 3x3.
        """
        scan1_cart = TransformationUtils.polaire_to_cartesien(scan1)
        scan2_cart = TransformationUtils.polaire_to_cartesien(scan2)

        min_len = min(len(scan1_cart), len(scan2_cart))
        scan1_cart, scan2_cart = scan1_cart[:min_len], scan2_cart[:min_len]

        T, _, _ = icp(scan1_cart, scan2_cart, max_iterations=100, tolerance=0.001)

        theta = np.arctan2(T[1, 0], T[0, 0]) * 180 / np.pi
        translation = np.linalg.norm(T[:2, 2])

        # On ignore les petites variations (bruit)
        if abs(translation) < 1.8 or abs(theta) < 0.8:
            return np.identity(3)
        else:
            #print("Déplacement:", round(translation), "mm, Rotation:", round(theta), "°")
            return T

    @staticmethod
    def filter_and_cluster_points(points, threshold=10.0):
        """
        Regroupe les points proches dans des clusters pour réduire le bruit et simplifier la carte.
        points : np.array de forme (N, 2) - Points à filtrer
        threshold : distance maximale pour considérer deux points comme proches
        Retourne un tableau de points filtrés et regroupés.
        """
        if len(points) == 0:
            return points
        tree = cKDTree(points)
        clusters = tree.query_ball_tree(tree, threshold)
        return np.array([np.mean(points[cluster], axis=0) for cluster in clusters])
    
    @staticmethod
    def calculer_barycentre(scan):
        """
        Calcule le barycentre pondéré des points d'un scan LIDAR.

        scan : liste de tuples (qualité, angle en degrés, distance en mm)
        retourne : tuple (x, y) du barycentre pondéré
        """
        points = TransformationUtils.polaire_to_cartesien(scan)  # [(x1, y1), (x2, y2), ...]
        distances = np.array([d for _, _, d in scan])  # distances en mm

        if len(points) == 0 or np.sum(distances) == 0:
            return (0.0, 0.0)

        points = np.array(points)
        weights = distances  # poids linéaires, plus la distance est grande, plus ça pèse

        # barycentre pondéré
        x_bar = np.average(points[:, 0], weights=weights)
        y_bar = np.average(points[:, 1], weights=weights)
        
        return (x_bar, y_bar)



class LidarScanner:
    """
    Classe qui gère l'initialisation, l'arrêt, et l'accès aux scans du LIDAR.
    Utilise la bibliothèque rplidar pour communiquer avec le LIDAR.
    """

    def __init__(self, port="/dev/cu.SLAB_USBtoUART", baudrate=115200):

        self.lidar = RPLidar(port, baudrate=baudrate)

    def start(self):
        """
        Démarre le LIDAR proprement.
        """
        self.lidar.stop()
        self.lidar.stop_motor()
        time.sleep(1)
        self.lidar.start_motor()
        time.sleep(2)
        print("LIDAR prêt !")

    def stop(self):
        """
        Arrête et déconnecte le LIDAR proprement.
        """
        self.lidar.stop()
        self.lidar.stop_motor()
        self.lidar.disconnect()
        print("LIDAR arrêté.")

    def iter_scans(self):
        """
        Retourne un générateur de scans du LIDAR.
        """
        return self.lidar.iter_scans()


class LidarLocaliser:
    """
    Classe principale pour gérer la localisation du robot et la construction de la carte.
    """

    def __init__(self, scanner, scan_interval=100, map_filename='Carte.png', scan_actual=False):
        """Cette classe gère la localisation du robot en utilisant un LIDAR.
        Elle traite les scans à intervalles réguliers, applique l'algorithme ICP
        pour estimer la transformation entre les scans, et met à jour la carte.
        Elle utilise également des méthodes de filtrage et de regroupement pour
        améliorer la qualité de la carte.
        Elle gère l'affichage graphique de la carte et la sauvegarde de l'image.

        Parametres
        ----------
        scanner : LidarScanner
            Instance de la classe LidarScanner pour interagir avec le LIDAR.
        scan_interval : int, optional
            Intervalle entre les scans à traiter (par défaut 100).
        map_filename : str, optional
            Nom du fichier pour sauvegarder la carte (par défaut 'Carte.png').
        scan_actual : bool, optional
            Indique si le scan actuel doit être affiché sur la carte (par défaut False).
        
        """
        self.scanner = scanner
        self.scan_interval = scan_interval
        self.map_filename = map_filename
        self.T_cumul = np.identity(3)
        self.pos_robot = [[0, 0]]
        self.all_points = []
        self.previous_scan = None
        self.init_scan = None
        self.scan_counter = 0
        self.scan_actual = scan_actual
        self.objet = []

        self.fig, self.ax = plt.subplots()

    def addObjet(self, objet):
        """
        Ajoute un objet à la liste des objets à afficher sur la carte.
        
        Parametres
        ----------
        objet : list
            Liste contenant les coordonnées de l'objet à ajouter.
        """
        self.objet.append(objet)
    
    def localize(self):
        """
        Boucle principale de localisation : traite les scans à intervalles réguliers,
        applique l'ICP, met à jour la carte et retourne la position du robot.
        """
        try:
            self.scanner.start()
            for scan in self.scanner.iter_scans():
                self.scan_counter += 1
                if self.scan_counter % self.scan_interval != 0:
                    continue

                if self.previous_scan is None:
                    self.previous_scan = scan
                    self.init_scan = scan
                    continue

                T = TransformationUtils.extract_transformation(self.previous_scan, scan)
                self.T_cumul = T @ self.T_cumul
                T_inv = np.linalg.pinv(self.T_cumul)

                scan_cart = TransformationUtils.polaire_to_cartesien(scan)
                transformed_points = np.dot(np.hstack([scan_cart, np.ones((len(scan_cart), 1))]), T_inv.T)[:, :2]
                transformed_scan = TransformationUtils.cartesien_to_polaire(transformed_points)

                T_check = TransformationUtils.extract_transformation(self.init_scan, transformed_scan)

                if np.allclose(T_check, np.identity(3)):
                    self.all_points.extend(transformed_points)
                    filtered_points = TransformationUtils.filter_and_cluster_points(np.array(self.all_points))
                    self.previous_scan = scan

                    self.pos_robot = [[0, 0]]
                    self.pos_robot = np.dot(np.hstack([self.pos_robot, np.ones((1, 1))]), T_inv.T)[:, :2]
                    
                    R = T_inv[:2, :2]
                    theta = np.arctan2(R[1, 0], R[0, 0])  # angle en radians
                    theta_deg = np.degrees(theta)         # angle en degrés si besoin

                    # Mise à jour graphique
                    self._update_plot(scan_cart, filtered_points)

                    # Distance droite et gauche
                    dAvant = None
                    dArriere = None
                    dDroite = None
                    dGauche = None
                    
                    for i in range(len(scan)):
                        if np.around(scan[i][1], decimals=0) == 0 or np.around(scan[i][1], decimals=0) == 360:
                            dAvant = scan[i][2]
                        elif np.around(scan[i][1], decimals=0) == 90:
                            dDroite = scan[i][2]
                        elif np.around(scan[i][1], decimals=0) == 180:
                            dArriere = scan[i][2]
                        elif np.around(scan[i][1], decimals=0) == 270:
                            dGauche = scan[i][2]
                    
                    yield self.pos_robot[0],theta_deg ,dAvant , dArriere, dDroite, dGauche, TransformationUtils.calculer_barycentre(scan)
                else:
                    #print("Scan ignoré (incohérent)")
                    self.T_cumul = np.linalg.pinv(T) @ self.T_cumul

        except Exception as e:
            print("Erreur :", e)
            
            traceback.print_exc()
        finally:
            self.scanner.stop()

    def _update_plot(self, scan_cart, filtered_points):
        """
        Met à jour le graphique et sauvegarde l'image de la carte.
        
        Parametres
        ----------
        scan_cart : np.array
            Points du scan actuel en coordonnées cartésiennes.
        filtered_points : np.array
            Points filtrés et regroupés de la carte.
        """
        self.ax.cla()

        self.ax.set_xlim(filtered_points[:, 0].max()*1.2, filtered_points[:, 0].min()*1.2)
        self.ax.set_ylim(filtered_points[:, 1].max()*1.2, filtered_points[:, 1].min()*1.2)

        if self.scan_actual:
            self.ax.scatter(scan_cart[:, 0], scan_cart[:, 1], s=1, c='red', label='Scan actuel')
        
        self.ax.scatter(filtered_points[:, 0], filtered_points[:, 1], s=1, c='blue', label='Carte')
        self.ax.scatter(self.pos_robot[0][0], self.pos_robot[0][1], s=20, color='green', label='Robot')

        cpt = 0
        for objet in self.objet:
            cpt += 1 
            T_inv = np.linalg.pinv(self.T_cumul)
            positionObjet = [[objet[0], objet[1]]]
            positionObjet = np.dot(np.hstack([positionObjet, np.ones((1, 1))]), T_inv.T)[:, :2]
            self.ax.scatter(positionObjet[0][0], positionObjet[0][1], s=20, color=objet[2], label='Objet_' + str(cpt))
            
        self.ax.legend(loc='upper right')
        plt.savefig(self.map_filename)



if __name__ == "__main__":
    
    scanner = LidarScanner()
    localiser = LidarLocaliser(scanner, 
                               scan_interval=10, 
                               map_filename='map_output.png', 
                               scan_actual=False)
    iter = 0
    for position,theta_deg,_,_,_,_,centre in localiser.localize():
        #print("Position actuelle du robot :", position)
        
        if iter == 200:
            print("Ajout d'un objet à la carte")
            ob2 = [centre[0], centre[1], 'purple']  
            localiser.addObjet(ob2)
            
        if iter == 200:
            break
        
        iter += 1
