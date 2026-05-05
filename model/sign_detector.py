import cv2
import numpy as np
import joblib
import os
from cvzone.HandTrackingModule import HandDetector
from tensorflow.keras.models import load_model

class SignDetector:
    def __init__(self):
        # Load Model & Files from local model directory
        base_path = os.path.dirname(__file__)
        model_path = os.path.join(base_path, "isl_117word_model.h5")
        scaler_path = os.path.join(base_path, "scaler.pkl")
        class_names_path = os.path.join(base_path, "class_names.pkl")

        print(f"Loading model from {model_path}...")
        self.model = load_model(model_path)
        self.scaler = joblib.load(scaler_path)
        self.class_names = joblib.load(class_names_path)

        # Initialize CVZone HandDetector (uses Mediapipe internally)
        self.detector = HandDetector(staticMode=True, maxHands=2, detectionCon=0.5)
        print("Real Model initialized with CVZone (Inference Mode)")

    def predict(self, image):
        if image is None:
            print("[DEBUG] Received empty image")
            return {"label": "ERROR", "confidence": 0.0}

        # Preprocess: Hand detection using CVZone
        try:
            hands, image = self.detector.findHands(image, draw=False)
        except Exception as e:
            print(f"[DEBUG] Error in findHands: {str(e)}")
            return {"label": "CV ERROR", "confidence": 0.0}

        if not hands:
            print("[DEBUG] No hands found in image")
            return {"label": "NO HAND DETECTED", "confidence": 0.0}

        # Landmark Extraction
        # Teammate's model likely expects 21 landmarks (x, y, z) = 63 features
        lm = []
        try:
            if self.detector.results.multi_hand_landmarks:
                # We strictly use the first detected hand's landmarks to fit the 63-feature model shape
                for p in self.detector.results.multi_hand_landmarks[0].landmark:
                    lm.extend([p.x, p.y, p.z])
                
                if len(lm) != 63:
                    print(f"[DEBUG] Unexpected landmark count: {len(lm)}")
                    return {"label": "LANDMARK ERROR", "confidence": 0.0}
            else:
                print("[DEBUG] multi_hand_landmarks is None")
                return {"label": "LANDMARK ERROR", "confidence": 0.0}
        except Exception as e:
            print(f"[DEBUG] Error extracting landmarks: {str(e)}")
            return {"label": "LANDMARK ERROR", "confidence": 0.0}

        # Scale and Predict
        try:
            lm_scaled = self.scaler.transform([lm])
            preds = self.model.predict(lm_scaled, verbose=0)[0]
            
            top_idx = preds.argmax()
            label = self.class_names[top_idx]
            confidence = float(preds[top_idx])

            # Calculate relative bounding box
            h, w, c = image.shape
            
            # Combine bounding boxes if multiple hands detected
            if len(hands) == 1:
                bx, by, bw, bh = hands[0]['bbox']
            else:
                # Calculate union of all hand bounding boxes
                x_min = min(hand['bbox'][0] for hand in hands)
                y_min = min(hand['bbox'][1] for hand in hands)
                x_max = max(hand['bbox'][0] + hand['bbox'][2] for hand in hands)
                y_max = max(hand['bbox'][1] + hand['bbox'][3] for hand in hands)
                bx, by, bw, bh = x_min, y_min, x_max - x_min, y_max - y_min
            
            # Add padding to bbox (optional, CVZone usually makes it tight)
            # Ensure within image bounds
            bx = max(0, bx - 20)
            by = max(0, by - 20)
            bw = min(w - bx, bw + 40)
            bh = min(h - by, bh + 40)

            # Convert to percentages for responsive frontend overlay
            bbox_percent = [
                bx / w,
                by / h,
                bw / w,
                bh / h
            ]

            print(f"[DEBUG] Prediction: {label} ({confidence:.4f})")

            return {
                "label": label,
                "confidence": round(confidence, 4),
                "bbox": bbox_percent
            }
        except Exception as e:
            print(f"[DEBUG] Error during prediction: {str(e)}")
            return {"label": "PREDICTION ERROR", "confidence": 0.0}

# Global instance
detector = SignDetector()
