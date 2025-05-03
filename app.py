from flask import Flask
from flask_cors import CORS 
from routes.liveDetectionRoutes import liveDetectionRoutes

app = Flask(__name__)
# Configure CORS
CORS(app, resources={
    r"/live-detection/*": {
        "origins": ["https://blind-spot-detections.vercel.app"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

app.register_blueprint(liveDetectionRoutes, url_prefix="/live-detection")

if __name__ == "__main__":
    app.run(debug=True)
