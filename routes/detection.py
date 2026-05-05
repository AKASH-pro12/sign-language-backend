from flask import Blueprint, request, jsonify
from model.sign_detector import detector # Assuming this import works based on sys.path or structure
import cv2
import numpy as np
import base64
from database.models import db
from datetime import datetime
import os
import tempfile

detection_bp = Blueprint('detection', __name__)

@detection_bp.route('/webcam', methods=['POST'])
def detect_webcam():
    data = request.json
    if not data or 'image' not in data:
        return jsonify({"error": "No image provided"}), 400
    
    try:
        # Image comes as base64 string
        # data:image/jpeg;base64,...
        header, encoded = data['image'].split(",", 1)
        nparr = np.frombuffer(base64.b64decode(encoded), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        result = detector.predict(img)
        
        # Save to history if confidence is high enough and it's a valid sign
        if result['confidence'] > 0.6 and result['label'] not in ["NO HAND DETECTED", "ERROR", "LANDMARK ERROR", "CV ERROR", "Waiting..."]:
            entry = {
                "sign_label": result['label'],
                "confidence": result['confidence'],
                "input_type": 'webcam',
                "timestamp": datetime.utcnow()
            }
            db.detection_history.insert_one(entry)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@detection_bp.route('/image', methods=['POST'])
def detect_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    nparr = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    result = detector.predict(img)
    
    # Save to history
    entry = {
        "sign_label": result['label'],
        "confidence": result['confidence'],
        "input_type": 'image',
        "timestamp": datetime.utcnow()
    }
    db.detection_history.insert_one(entry)
    
    return jsonify(result)

@detection_bp.route('/video', methods=['POST'])
def detect_video():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    
    fd, filename = tempfile.mkstemp(suffix=".mp4")
    os.close(fd)
    file.save(filename)
    
    cap = cv2.VideoCapture(filename)
    predictions = []
    
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process every 5th frame to speed up
        if frame_count % 5 == 0:
            res = detector.predict(frame)
            if res['label'] not in ["NO HAND DETECTED", "ERROR", "LANDMARK ERROR", "CV ERROR"]:
                predictions.append(res)
        
        frame_count += 1
        if frame_count > 300: # Limit to 300 frames for safety
            break
            
    cap.release()
    try:
        os.remove(filename)
    except Exception as e:
        print(f"Error removing temp file: {e}")

    if not predictions:
        return jsonify({"label": "NO HAND DETECTED", "confidence": 0.0, "bbox": [0,0,0,0]})

    # Find most common prediction
    from collections import Counter
    # Separate labels and confidences to find the most common label
    # predictions is a list of Dicts: [{'label': 'A', 'confidence': 0.8}, ...]
    labels = [p['label'] for p in predictions]
    most_common_label = Counter(labels).most_common(1)[0][0]
    
    # Calculate average confidence for the most common label
    relevant_confidences = [p['confidence'] for p in predictions if p['label'] == most_common_label]
    avg_confidence = sum(relevant_confidences) / len(relevant_confidences) if relevant_confidences else 0.8
    
    # The bbox will correspond to the last valid frame's bbox or an average bbox. 
    # For a video route result, a general unified representation or simply omitting bbox works best since it's dynamic. 
    # We will return the bbox of the last occurrence of the most common label.
    last_bbox = [0, 0, 0, 0]
    for p in reversed(predictions):
        if p['label'] == most_common_label and 'bbox' in p:
            last_bbox = p['bbox']
            break
            
    # Save to history
    entry = {
        "sign_label": most_common_label,
        "confidence": round(avg_confidence, 4),
        "input_type": 'video',
        "timestamp": datetime.utcnow()
    }
    db.detection_history.insert_one(entry)
    
    return jsonify({"label": most_common_label, "confidence": round(avg_confidence, 4), "bbox": last_bbox})
