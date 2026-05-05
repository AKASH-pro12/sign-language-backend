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

# Database Config
client = MongoClient('mongodb://localhost:27017/')
# We attach the db instance to the app configuration so blueprints can access it if needed
# Alternatively, we can use the db instance from database.models directly
app.config['MONGO_CLIENT'] = client

# Register Blueprints
app.register_blueprint(detection_bp, url_prefix='/detect')
app.register_blueprint(history_bp, url_prefix='/history')
app.register_blueprint(analytics_bp, url_prefix='/analytics')

@app.route('/')
def index():
    return jsonify({"message": "Sign Language Detection API Running"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
