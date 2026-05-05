from flask import Flask, jsonify
from flask_cors import CORS
from database.models import db
import os
from pymongo import MongoClient

# Import Blueprints
from routes.detection import detection_bp
from routes.history import history_bp
from routes.analytics import analytics_bp

app = Flask(__name__)
CORS(app)

# Database Config (temporary local - will change later)
client = MongoClient('mongodb://localhost:27017/')
app.config['MONGO_CLIENT'] = client

# Register Blueprints
app.register_blueprint(detection_bp, url_prefix='/detect')
app.register_blueprint(history_bp, url_prefix='/history')
app.register_blueprint(analytics_bp, url_prefix='/analytics')

@app.route('/')
def index():
    return jsonify({"message": "Sign Language Detection API Running"})

# ✅ IMPORTANT FIX FOR RENDER
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)