from ultralytics import YOLO

# chargement du modèl pré-entrainé de Yolo
model = YOLO("yolov8n.pt")  # Load the pre-trained model

# entrainement du dataset de feu et de fumée
results = model.train(data="data.yaml", epochs=20, imgsz=640, batch=16, save=True) 

print("Training completed!")
