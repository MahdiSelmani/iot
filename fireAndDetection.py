import os
import cv2
from ultralytics import YOLO
import logging

# Désactiver les logs pour ultralytics
logging.getLogger('ultralytics').setLevel(logging.ERROR)

# Charger le modèle entraîné pour le feu et la fumée
custom_model_path = './runs/detect/train/weights/best.pt'
fire_smoke_model = YOLO(custom_model_path)

# Définir le seuil de confiance
threshold = 0.6

# Utiliser la webcam locale
cap = cv2.VideoCapture(0)  # 0 is the default webcam

# Vérifier si la connexion avec la caméra locale est réussie
if not cap.isOpened():
    print("Erreur : Impossible d'accéder à la caméra locale.")
    exit()

# Boucle continue de détection
while True:
    ret, frame = cap.read()
    if not ret:
        print("Erreur : Impossible de lire l'image depuis la caméra locale.")
        break

    # Effectuer la détection avec le modèle personnalisé (feu et fumée)
    fire_smoke_results = fire_smoke_model(frame)[0]

    # Variable pour suivre si le feu ou la fumée a été détecté
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

    # Afficher le résultat de détection
    cv2.imshow("Résultat de Détection de Feu et Fumée", frame)

    # Appuyer sur 'q' pour quitter la boucle
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libérer la caméra et fermer les fenêtres
cap.release()
cv2.destroyAllWindows()
