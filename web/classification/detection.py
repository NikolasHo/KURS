import io
import os
from PIL import Image
from django.conf import settings

# Try importing YOLO and load the trained model if it exists
try:
    from ultralytics import YOLO
    MODEL_PATH = os.path.join(settings.BASE_DIR, 'runs', 'web-training', 'weights', 'best.pt')
    model = YOLO(MODEL_PATH) if os.path.exists(MODEL_PATH) else None
except ImportError:
    model = None


# Debug print helper - only prints when DEBUG is True in Django settings
def debug_print(message):
    if settings.DEBUG:
        print(message)


# Detects objects (ingredients) in an uploaded image using the trained YOLO model
def detect_ingredients(image_file, conf_threshold=0.5):
    debug_print("Starting object detection...")

    # Ensure the model is available
    if model:
        debug_print(f"Model loaded from: {MODEL_PATH}")
    else:
        debug_print(f"Model could not be loaded. Expected at: {MODEL_PATH}")
        debug_print("No model loaded.")
        return []

    debug_print("Model available, reading image data...")

    # Read and convert the uploaded image to RGB format
    try:
        img = Image.open(io.BytesIO(image_file.read())).convert('RGB')
    except Exception as e:
        debug_print(f"Error loading image: {e}")
        return []

    debug_print("Image successfully loaded and converted.")
    debug_print(f"Running inference with conf_threshold={conf_threshold}...")

    # Perform inference with the YOLO model
    results = model(img, imgsz=640, conf=conf_threshold)[0]
    debug_print("Inference complete.")

    # Process detection results
    detections = []
    debug_print("Processing results...")
    for cls, conf in zip(results.boxes.cls, results.boxes.conf):
        name = model.names[int(cls)]
        debug_print(f"Detected: {name} with confidence {float(conf):.2f}")
        detections.append({'class': name, 'confidence': float(conf)})

    debug_print("Object detection finished.")
    return detections
