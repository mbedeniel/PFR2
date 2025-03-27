import socket
import threading
import struct
import pickle
import time

class Communication:
    def __init__(self, ip="0.0.0.0", port=12345, mode="server", period=0.1):

        self.ip = ip
        self.port = port
        self.mode = mode
        self.running = True
        self.connexions = []
        self.fonction = None

        self.data = {"video": None, "Joystick": (0, 0)}
        self.period = period
        self.sending_thread = None
        self.sending_active = False

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if mode == "server":
            self.s.bind((self.ip, self.port))
            self.s.listen(5)
            threading.Thread(target=self.accept_connections, daemon=True).start()
        else:
            try:
                self.s.connect((self.ip, self.port))
                print("Client connecté à {self.ip}:{self.port}")
                threading.Thread(target=self.listen_messages, args=(self.s,), daemon=True).start()
            except Exception as e:
                print("Erreur de connexion:", e)

    def accept_connections(self):
        """Accepte les connexions clients (mode serveur)."""
        while self.running:
            try:
                conn, addr = self.s.accept()
                self.connexions.append(conn)
                print("Connexion établie avec", addr)
                threading.Thread(target=self.listen_messages, args=(conn,), daemon=True).start()
            except Exception as e:
                print("Erreur acceptation:", e)
                break

    def send(self):
        """Envoie les données sérialisées à tous les clients."""
        data = pickle.dumps(self.data)  # Sérialisation
        size = struct.pack("Q", len(data))  # Encode la taille sur 8 octets

        if self.mode == "server":
            for conn in self.connexions:
                try:
                    conn.sendall(size + data)  # Envoi de la taille suivie des données
                except Exception as e:
                    print("Erreur d'envoi:", e)
                    self.connexions.remove(conn)
        else:
            try:
                self.s.sendall(size + data)
            except Exception as e:
                print("Erreur d'envoi:", e)

    def listen_messages(self, conn):
        """Écoute et traite les messages reçus."""
        while self.running:
            try:
                size_data = conn.recv(8)  # Lire la taille (8 octets)
                if not size_data:
                    break

                size = struct.unpack("Q", size_data)[0]
                data = b""
                while len(data) < size:
                    packet = conn.recv(4096)
                    if not packet:
                        break
                    data += packet

                received_data = pickle.loads(data)  # Désérialisation
                print("Données reçues:", received_data)

                if self.fonction:
                    self.fonction(received_data)

            except Exception as e:
                print("Erreur réception:", e)
                break

        conn.close()
        if conn in self.connexions:
            self.connexions.remove(conn)

    def set_video(self, frame):
        """Modifie la donnée vidéo."""
        self.data["video"] = frame

    def set_joystick(self, x, y):
        """Modifie les valeurs du joystick."""
        self.data["Joystick"] = (x, y)

    def send_periodically(self):
        """Envoie les données à intervalle régulier."""
        self.sending_active = True
        while self.running and self.sending_active:
            self.send()
            time.sleep(self.period)

    def start_sending(self):
        """Démarre l'envoi automatique des données."""
        if not self.sending_thread or not self.sending_thread.is_alive():
            self.sending_thread = threading.Thread(target=self.send_periodically, daemon=True)
            self.sending_thread.start()
            print("📡 Envoi automatique démarré !")

    def stop_sending(self):
        """Arrête l'envoi automatique des données."""
        self.sending_active = False
        print("Envoi automatique arrêté.")

    def close(self):
        """Ferme la connexion."""
        self.running = False
        self.stop_sending()
        for conn in self.connexions:
            conn.close()
        self.s.close()
        print("Communication fermée.")

    def receive(self, fonction):
        """Définit la fonction à exécuter lors de la réception de données."""
        self.fonction = fonction
