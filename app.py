from flask import Flask
from flask_cors import CORS 
from routes.liveDetectionRoutes import liveDetectionRoutes

app = Flask(__name__)
CORS(app) 

app.register_blueprint(liveDetectionRoutes, url_prefix="/live-detection")

if __name__ == "__main__":
    app.run(debug=True)
