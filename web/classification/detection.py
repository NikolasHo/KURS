import io, os
from PIL import Image
from django.conf import settings

try:
    from ultralytics import YOLO
    MODEL_PATH = os.path.join(settings.BASE_DIR, 'runs', 'web-training', 'weights', 'best.pt')
    model = YOLO(MODEL_PATH) if os.path.exists(MODEL_PATH) else None
except ImportError:
    model = None


def detect_ingredients(image_file, conf_threshold=0.5):
    print("Starte Objekterkennung...")

    print(f"Modell geladen: {MODEL_PATH}") if model else print(f"Modell konnte nicht geladen werden. {MODEL_PATH}")
   
    if model is None:
        print("Kein Modell geladen.")
        return []

    print("Modell erkannt, lese Bilddaten...")

    img_bytes = image_file.read()
    try:
        img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
    except Exception as e:
        print(f"Fehler beim Laden des Bildes: {e}")
        return []

    print("Bild erfolgreich geladen und konvertiert.")
    print(f"Führe Inferenz durch mit conf_threshold={conf_threshold}...")

    results = model(img, imgsz=640, conf=conf_threshold)[0]
    print("Inferenz abgeschlossen.")

    detections = []
    print("Verarbeite Ergebnisse...")
    for cls, conf in zip(results.boxes.cls, results.boxes.conf):
        name = model.names[int(cls)]
        print(f"Erkannt: {name} mit Konfidenz {float(conf):.2f}")
        detections.append({'class': name, 'confidence': float(conf)})

    print("Objekterkennung abgeschlossen.")
    return detections
