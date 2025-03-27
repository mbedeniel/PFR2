import cv2
from communication import Communication

server = Communication(ip="0.0.0.0", port=12345, mode="server", period=1)  # Envoi toutes les 1s
server.start_sending()  # Active l'envoi automatique

cap = cv2.VideoCapture(0)  # Webcam
if not cap.isOpened():
    print("❌ Erreur : Impossible d'ouvrir la caméra.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Erreur : Impossible de lire la frame.")
        break

    server.set_video(frame)  # Met à jour les données vidéo

    cv2.imshow("📷 Serveur - Envoi Vidéo", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
server.close()
cv2.destroyAllWindows()
