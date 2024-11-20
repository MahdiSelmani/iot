import os
import cv2
from ultralytics import YOLO
import logging
import time
import paho.mqtt.client as mqtt

# Désactiver les logs pour ultralytics
logging.getLogger('ultralytics').setLevel(logging.ERROR)

# Charger le modèle entraîné pour le feu et la fumée
custom_model_path = './runs/detect/train/weights/best.pt'
fire_smoke_model = YOLO(custom_model_path)

# Définir le seuil de confiance
threshold = 0.6

# Initialiser MQTT
BROKER = "localhost"
PORT = 1883
TOPIC = "fire_smoke_alert"

mqtt_client = mqtt.Client()
mqtt_client.connect(BROKER, PORT)

# Utiliser la webcam locale
cap = cv2.VideoCapture(0)  # 0 is the default webcam

# Vérifier si la connexion avec la caméra locale est réussie
if not cap.isOpened():
    print("Erreur : Impossible d'accéder à la caméra locale.")
    exit()

# Initialiser les variables pour l'enregistrement
recording = False
video_writer = None
fire_or_smoke_timer = 0  # Temps écoulé depuis la détection initiale
fire_or_smoke_confirmed = False  # État de détection confirmé
timeout_duration = 5  # Durée en secondes avant de confirmer la détection

# Boucle continue de détection
while True:
    ret, frame = cap.read()
    if not ret:
        print("Erreur : Impossible de lire l'image depuis la caméra locale.")
        break

    # Effectuer la détection avec le modèle personnalisé (feu et fumée)
    fire_smoke_results = fire_smoke_model(frame)[0]

    # Variable pour suivre si le feu ou la fumée est détecté dans cette frame
    fire_or_smoke_detected = False

    # Dessiner les boîtes englobantes et les étiquettes pour les résultats du modèle feu/fumée
    for result in fire_smoke_results.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = result
        if score > threshold:
            label = fire_smoke_results.names[int(class_id)].upper()
            if label == "FIRE":
                color = (0, 0, 255)  # Rouge pour le feu
            elif label == "SMOKE":
                color = (255, 255, 0)  # Jaune pour la fumée

            # Dessiner les boîtes et le texte
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 1)
            text = f"{label}: {score:.2f}"
            cv2.putText(frame, text, (int(x1), int(y1) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 2, cv2.LINE_AA)
            fire_or_smoke_detected = True  # Indiquer que le feu ou la fumée a été détecté

    # Gestion du timeout pour confirmation
    if fire_or_smoke_detected:
        if not fire_or_smoke_confirmed:
            # Démarrer le timer si feu ou fumée est détecté
            if fire_or_smoke_timer == 0:
                fire_or_smoke_timer = time.time()
            elif time.time() - fire_or_smoke_timer >= timeout_duration:
                # Confirmer la détection après le timeout
                fire_or_smoke_confirmed = True
                print("Détection confirmée : feu ou fumée détecté.")
                mqtt_client.publish(TOPIC, "Fire or smoke detected!")

                # Démarrer l'enregistrement vidéo
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                video_filename = f"fire_smoke_{timestamp}.avi"
                video_writer = cv2.VideoWriter(
                    video_filename,
                    cv2.VideoWriter_fourcc(*'XVID'),
                    20.0,
                    (frame.shape[1], frame.shape[0])
                )
                recording = True
                print(f"Enregistrement démarré : {video_filename}")
    else:
        # Réinitialiser le timer et l'état si aucun feu ou fumée n'est détecté
        fire_or_smoke_timer = 0
        fire_or_smoke_confirmed = False
        if recording:
            video_writer.release()
            print("Enregistrement arrêté.")
            recording = False

    # Enregistrer les images dans le fichier vidéo si enregistrement actif
    if recording and video_writer:
        video_writer.write(frame)

    # Afficher la vidéo en direct
    cv2.imshow("Fire and Smoke Detection", frame)

    # Appuyer sur 'q' pour quitter la boucle
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libérer la caméra, arrêter l'enregistrement et fermer les fenêtres
if recording and video_writer:
    video_writer.release()
cap.release()
cv2.destroyAllWindows()
mqtt_client.disconnect()
print("Programme terminé.")
