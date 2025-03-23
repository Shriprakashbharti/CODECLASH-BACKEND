from flask import Blueprint
from controllers.liveDetectionController import get_past_detections, live_detection_feed, get_risk_level


liveDetectionRoutes = Blueprint("liveDetectionRoutes", __name__)

liveDetectionRoutes.route("/video_feed")(live_detection_feed)

liveDetectionRoutes.route("/risk-level", methods=["GET"])(get_risk_level)

liveDetectionRoutes.route("/past-detections", methods=["GET"])(get_past_detections)

