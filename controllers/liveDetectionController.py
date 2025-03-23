import cv2
import os
import datetime
import numpy as np
from flask import Blueprint, Response, jsonify
from pymongo import MongoClient
from flask_cors import cross_origin
from ultralytics import YOLO

# Load YOLO model
model = YOLO("models/yolov8m.pt")

# MongoDB Setup
client = MongoClient("mongodb://localhost:27017/")
db = client["BlindSpotDetection"]
detections_collection = db["Detections"]
live_detection_bp = Blueprint("live_detection", __name__)
# Ensure output directory exists
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads", "DetectedOutput")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global risk level
risk_level = 0  

def add_fog_effect(image, intensity=0.5):
    """Simulate foggy conditions by blending the image with a white overlay."""
    fog = np.full_like(image, 255, dtype=np.uint8)  
    foggy_image = cv2.addWeighted(image, 1 - intensity, fog, intensity, 0)
    return foggy_image

def add_motion_blur(image, kernel_size=5):
    """Apply motion blur to simulate rainy conditions."""
    kernel = np.zeros((kernel_size, kernel_size))
    kernel[int((kernel_size - 1) / 2), :] = np.ones(kernel_size)
    kernel /= kernel_size
    return cv2.filter2D(image, -1, kernel)

def enhance_image(image):
    """Apply CLAHE contrast enhancement and add fog/rain simulation."""
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)

    enhanced_lab = cv2.merge((l, a, b))
    enhanced_image = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

    # Apply fog and rain effects randomly
    enhanced_image = add_fog_effect(enhanced_image, intensity=0.3)
    enhanced_image = add_motion_blur(enhanced_image, kernel_size=3)

    return enhanced_image

def calculate_risk(detections):
    """Calculates risk level based on object size, distance, and speed."""
    risk_level = 0
    for obj in detections:
        confidence = obj["confidence"]
        distance = obj["distance"]  

        # Increase risk if object is close and moving fast
        if distance < 1.5 and confidence > 0.5:
            risk_level = max(risk_level, 2)  # High risk
        elif distance < 3.0:
            risk_level = max(risk_level, 1)  # Medium risk

    return risk_level

def generate_frames():
    """Continuously capture frames, process, and return as MJPEG stream."""
    global risk_level  

    camera = cv2.VideoCapture(0)  
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    camera.set(cv2.CAP_PROP_FPS, 10)

    while True:
        success, frame = camera.read()
        if not success:
            break

        enhanced_frame = enhance_image(frame)
        
        # Perform object detection
        results = model(enhanced_frame, conf=0.3)

        detections = []
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence = float(box.conf[0])

                # Estimate distance (basic estimation)
                distance = max(0.5, 5 - (x2 - x1) / 50)

                detections.append({
                    "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                    "confidence": confidence, "distance": distance
                })

                # Draw bounding box
                color = (0, 255, 0) if distance > 3 else (0, 0, 255)
                cv2.rectangle(enhanced_frame, (x1, y1), (x2, y2), color, 2)

        # Calculate risk level
        risk_level = calculate_risk(detections)

        # Save detection data to MongoDB
        detections_collection.insert_one({
            "timestamp": datetime.datetime.utcnow(),
            "detections": detections,
            "risk_level": risk_level
        })

        # Save the latest frame
        output_path = os.path.join(UPLOAD_FOLDER, "live_detected.jpg")
        cv2.imwrite(output_path, enhanced_frame)

        # Convert frame to JPEG
        _, buffer = cv2.imencode('.jpg', enhanced_frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

    camera.release()

@cross_origin() 
def live_detection_feed():
    """Returns live video feed."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@cross_origin() 
def get_risk_level():
    """Returns the current risk level as JSON."""
    global risk_level
    return jsonify({"risk_level": risk_level})

@cross_origin() 
def get_past_detections():
    """Fetch past detections from MongoDB."""
    past_detections = list(detections_collection.find().sort("timestamp", -1).limit(10))
    
    for detection in past_detections:
        detection["_id"] = str(detection["_id"])
        detection["timestamp"] = detection["timestamp"].isoformat()

    return jsonify({"past_detections": past_detections})