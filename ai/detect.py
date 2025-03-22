import os
import sys
import cv2
import numpy as np
from ultralytics import YOLO
import json

sys.stdout.flush()

# Function to enhance foggy images using CLAHE
def enhance_image(image_path):
    image = cv2.imread(image_path)
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    # Apply CLAHE to L-channel
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)

    # Merge and convert back to BGR
    enhanced_lab = cv2.merge((l, a, b))
    enhanced_image = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
    return enhanced_image

model = YOLO("models/yolov8m.pt")

image_path = sys.argv[1]

# ✅ Save output in a persistent directory (`/uploads/`)
output_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(output_dir, exist_ok=True)

enhanced_image_path = os.path.join(output_dir, "enhanced_image.jpg")
detected_image_path = os.path.join(output_dir, "detected_output.jpg")

image = enhance_image(image_path)

cv2.imwrite(enhanced_image_path, image)

# Perform object detection with lower confidence threshold
results = model(image, conf=0.25)  # Reduce confidence for foggy conditions

detections = []
for r in results:
    for box in r.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = round(float(box.conf[0]), 2)
        class_id = int(box.cls[0])  
        label = model.model.names[class_id] if hasattr(model, 'model') else str(class_id)

        # Store detection in JSON format
        detections.append({
            "bbox": [x1, y1, x2, y2],
            "confidence": conf,
            "class": label
        })

        # Draw bounding box and label
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(image, f"{label} ({conf})", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

cv2.imwrite(detected_image_path, image)

# ✅ Return a URL that actually works (no `/tmp/`)
print(json.dumps({
    "detections": detections,
    "imageUrl": f"https://object-detection-tbc1.onrender.com/uploads/detected_output.jpg"
}, indent=2))
sys.stdout.flush()
sys.exit(0)
