import io
import os
from PIL import Image
from django.conf import settings

try:
    from ultralytics import YOLO
    MODEL_PATH = os.path.join(settings.BASE_DIR, 'runs', 'web-training', 'weights', 'best.pt')
    model = YOLO(MODEL_PATH) if os.path.exists(MODEL_PATH) else None
except ImportError:
    model = None


def detect_ingredients(image_file, conf_threshold=0.5):
    print("Starting object detection...")

    if model:
        print(f"Model loaded from: {MODEL_PATH}")
    else:
        print(f"Model could not be loaded. Expected at: {MODEL_PATH}")
        print("No model loaded.")
        return []

    print("Model available, reading image data...")

    try:
        img = Image.open(io.BytesIO(image_file.read())).convert('RGB')
    except Exception as e:
        print(f"Error loading image: {e}")
        return []

    print("Image successfully loaded and converted.")
    print(f"Running inference with conf_threshold={conf_threshold}...")

    results = model(img, imgsz=640, conf=conf_threshold)[0]
    print("Inference complete.")

    detections = []
    print("Processing results...")
    for cls, conf in zip(results.boxes.cls, results.boxes.conf):
        name = model.names[int(cls)]
        print(f"Detected: {name} with confidence {float(conf):.2f}")
        detections.append({'class': name, 'confidence': float(conf)})

    print("Object detection finished.")
    return detections
