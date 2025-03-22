from ultralytics import YOLO
import cv2

# Load YOLOv8 model
model = YOLO("models/yolov8n.pt")

# Load and detect objects in an image
image_path = "test.jpg"
image = cv2.imread(image_path)

results = model(image)

# Show detection results
for r in results:
    for box in r.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = round(float(box.conf[0]), 2)
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(image, f"Conf: {conf}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

cv2.imshow("Detection", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
