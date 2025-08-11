import io
import os
import base64
import numpy as np
from PIL import Image
from django.conf import settings

# Try importing YOLO and load the trained model if it exists
try:
    from ultralytics import YOLO
    MODEL_PATH = os.path.join(settings.BASE_DIR, 'runs', 'web-training', 'weights', 'best.pt')
    model = YOLO(MODEL_PATH) if os.path.exists(MODEL_PATH) else None
except ImportError:
    model = None


def debug_print(message):
    if settings.DEBUG:
        print(message)


def detect_ingredients(image_file, conf_threshold=0.5, return_image=False):
    """
    Run YOLO on an uploaded image.

    Returns:
      - if return_image == False: detections: List[{'class', 'confidence', 'box':[x1,y1,x2,y2]}]
      - if return_image == True:  (detections, data_url_png)
    """
    debug_print("Starting object detection...")

    if not model:
        debug_print(f"Model could not be loaded. Expected at: {os.path.join(settings.BASE_DIR, 'runs', 'web-training', 'weights', 'best.pt')}")
        return [] if not return_image else ([], None)

    # Wichtig: stream des Uploads an den Anfang
    try:
        image_file.seek(0)
    except Exception:
        pass

    try:
        img = Image.open(io.BytesIO(image_file.read())).convert('RGB')
    except Exception as e:
        debug_print(f"Error loading image: {e}")
        return [] if not return_image else ([], None)

    results = model(img, imgsz=640, conf=conf_threshold)[0]

    # Detections inkl. Boxen
    detections = []
    if results.boxes is not None and len(results.boxes) > 0:
        xyxy = results.boxes.xyxy.cpu().numpy()
        cls_ids = results.boxes.cls.cpu().numpy()
        confs = results.boxes.conf.cpu().numpy()
        for (x1, y1, x2, y2), cls_id, conf in zip(xyxy, cls_ids, confs):
            name = model.names[int(cls_id)]
            detections.append({
                'class': name,
                'confidence': float(conf),
                'box': [int(x1), int(y1), int(x2), int(y2)]
            })

    if not return_image:
        return detections

    # Annotiertes Bild erzeugen
    # results.plot() liefert ein BGR-ndarray; wir drehen die Kanäle nach RGB
    plotted = results.plot()
    plotted_rgb = plotted[:, :, ::-1]  # BGR -> RGB
    pil_annotated = Image.fromarray(plotted_rgb)

    buf = io.BytesIO()
    pil_annotated.save(buf, format='PNG')
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode('utf-8')
    data_url = f"data:image/png;base64,{b64}"

    return detections, data_url
