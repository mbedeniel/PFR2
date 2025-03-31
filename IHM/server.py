from communication import Communication
import cv2



def image_to_frame(image_path):
    # Lire l'image depuis le fichier
    frame = cv2.imread(image_path)
    
    # Vérifie si l'image a été lue correctement
    if frame is None:
        print("Erreur lors de la lecture de l'image.")
        return None
    
    # Retourne l'image comme un frame
    return frame


# Initialisation du serveur
server = Communication(mode="server")
"""
cap = cv2.VideoCapture(0)  # Webcam
if not cap.isOpened():
    print(" Erreur : Impossible d'ouvrir la caméra.")
    exit()
"""


def server_receive(data):
    print("Serveur a reçu:", data)
    #server.send({"response": "Message reçu du serveur"})

server.receive(server_receive)

print("Serveur en attente de connexions...")
while True:
    # Boucle infinie pour maintenir le serveur actif
    #ret, frame = cap.read()
    #if not ret:
    #    print(" Erreur : Impossible de lire la frame.")
    #    break
#   
    #data =  {"video":frame}
    data = "Ok from serveur"
    server.send(data)  # Met à jour les données vidéo

    #cv2.imshow("Serveur - Envoi Vidéo", data["video"])
    #if cv2.waitKey(1) & 0xFF == ord("q"):
    #    break
