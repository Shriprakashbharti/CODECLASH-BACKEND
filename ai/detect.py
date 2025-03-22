import sys
import cv2
import numpy as np
from ultralytics import YOLO
import json
import os
import sys
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

# Load YOLOv8 model
model = YOLO("models/yolov8m.pt")

# Get image path from command-line argument
image_path = sys.argv[1]

# Enhance the image for foggy conditions
image = enhance_image(image_path)


# output_dir =r"\Users\jaypr\OneDrive\Desktop\CODECLASH\backend\uploads\DetectedOutput"
output_dir =r"\uploads\DetectedOutput"
os.makedirs(output_dir, exist_ok=True)

output_paths = os.path.join(output_dir, "detected_output.jpg")
# Save enhanced image for reference
# enhance_dir=r"\Users\jaypr\OneDrive\Desktop\CODECLASH\backend\uploads\enhance"
enhance_dir=r"\uploads\enhance"
os.makedirs(enhance_dir, exist_ok=True)
output_path = os.path.join(enhance_dir, "enhanced_test.jpg")

cv2.imwrite(output_path, image)

# Perform object detection with lower confidence threshold
results = model(image, conf=0.25)  # Reduce confidence for foggy conditions

# Extract detections and draw bounding boxes
detections = []
for r in results:
    for box in r.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = round(float(box.conf[0]), 2)
        class_id = int(box.cls[0])  # Get class ID safely
        
        # Ensure model class names are correctly accessed
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

# Save the final detection image
cv2.imwrite(output_paths, image)

# Show the result (optional)
cv2.imshow("Enhanced Detection", image)
cv2.waitKey(1000)
cv2.destroyAllWindows()

# Output detection results in JSON format
print(json.dumps({
    "detections": detections,
    "imageUrl": f"http://localhost:5000/uploads/DetectedOutput/detected_output.jpg"
}, indent=2))
sys.stdout.flush()
sys.exit(0)