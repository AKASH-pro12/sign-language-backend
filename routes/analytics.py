from flask import Blueprint, jsonify
from database.models import db
import numpy as np

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/stats', methods=['GET'])
def get_stats():
    # Total
    total = db.detection_history.count_documents({})
    
    # Signs distribution
    pipeline = [
        {"$group": {"_id": "$sign_label", "count": {"$sum": 1}}}
    ]
    distribution = list(db.detection_history.aggregate(pipeline))
    dist_dict = {item["_id"]: item["count"] for item in distribution}

    # Mock Confusion Matrix (In a real app, this would be computed from a test set or ground truth)
    labels = list(dist_dict.keys()) if dist_dict else ["A", "B", "C", "D"]
    if len(labels) < 4: labels = ["A", "B", "C", "D", "E"]
    
    confusion_matrix = []
    for i in range(len(labels)):
        row = []
        for j in range(len(labels)):
            if i == j:
                row.append(0.8 + (np.random.random() * 0.15)) # High diagonal
            else:
                row.append(np.random.random() * 0.1) # Low off-diagonal
        confusion_matrix.append(row)

    # Mock Heatmap (Detections by Hour of Day)
    heatmap = [int(np.random.poisson(5)) for _ in range(24)]
    
    return jsonify({
        "total_detections": total,
        "distribution": dist_dict,
        "labels": labels,
        "confusion_matrix": confusion_matrix,
        "heatmap": heatmap
    })
