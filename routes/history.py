from flask import Blueprint, jsonify, request
from database.models import db

history_bp = Blueprint('history', __name__)

@history_bp.route('/', methods=['GET'])
def get_history():
    history_cursor = db.detection_history.find().sort("timestamp", -1).limit(50)
    history = []
    for h in history_cursor:
        history.append({
            "id": str(h["_id"]),
            "sign_label": h["sign_label"],
            "confidence": h["confidence"],
            "input_type": h["input_type"],
            "timestamp": h["timestamp"].isoformat() if "timestamp" in h else None
        })
    return jsonify(history)

@history_bp.route('/clear', methods=['DELETE'])
def clear_history():
    try:
        db.detection_history.delete_many({})
        return jsonify({"message": "History cleared"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
