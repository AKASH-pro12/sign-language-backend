import cv2
import numpy as np
import joblib
import os
import urllib.request
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from tensorflow.keras.models import load_model

class SignDetector:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.class_names = None
        self.detector = None

    def load_resources(self):
        if self.model is not None:
            return

        # Load Model & Files from local model directory
        base_path = os.path.dirname(__file__)
        model_path = os.path.join(base_path, "isl_117word_model.h5")
        scaler_path = os.path.join(base_path, "scaler.pkl")
        class_names_path = os.path.join(base_path, "class_names.pkl")
        task_path = os.path.join(base_path, "hand_landmarker.task")

        print(f"Loading model from {model_path}...")
        self.model = load_model(model_path)
        self.scaler = joblib.load(scaler_path)
        self.class_names = joblib.load(class_names_path)

        # Download MediaPipe task model if not exists
        if not os.path.exists(task_path):
            print("Downloading MediaPipe Hand Landmarker task model...")
            url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
            urllib.request.urlretrieve(url, task_path)
            print("Downloaded.")

        # Initialize MediaPipe HandLandmarker
        base_options = python.BaseOptions(model_asset_path=task_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=2,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        print("Real Model initialized with MediaPipe Tasks API")

    def predict(self, image):
        self.load_resources()
        if image is None:
            print("[DEBUG] Received empty image")
            return {"label": "ERROR", "confidence": 0.0}

        try:
            # Convert OpenCV BGR image to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
            
            # Detect hands
            detection_result = self.detector.detect(mp_image)
            
            if not detection_result.hand_landmarks:
                print("[DEBUG] No hands found in image")
                return {"label": "NO HAND DETECTED", "confidence": 0.0}

            # Landmark Extraction (use first hand)
            lm = []
            first_hand_landmarks = detection_result.hand_landmarks[0]
            for p in first_hand_landmarks:
                lm.extend([p.x, p.y, p.z])

            if len(lm) != 63:
                print(f"[DEBUG] Unexpected landmark count: {len(lm)}")
                return {"label": "LANDMARK ERROR", "confidence": 0.0}

            # Scale and Predict
            lm_scaled = self.scaler.transform([lm])
            preds = self.model.predict(lm_scaled, verbose=0)[0]
            
            top_idx = preds.argmax()
            label = self.class_names[top_idx]
            confidence = float(preds[top_idx])

            # Calculate bounding box from normalized landmarks
            h, w, c = image.shape
            
            # Combine bounding boxes if multiple hands detected
            all_x = []
            all_y = []
            for hand_lms in detection_result.hand_landmarks:
                for p in hand_lms:
                    all_x.append(p.x * w)
                    all_y.append(p.y * h)
                    
            bx = int(min(all_x))
            by = int(min(all_y))
            x_max = int(max(all_x))
            y_max = int(max(all_y))
            bw = x_max - bx
            bh = y_max - by

            # Add padding
            bx = max(0, bx - 20)
            by = max(0, by - 20)
            bw = min(w - bx, bw + 40)
            bh = min(h - by, bh + 40)

            bbox_percent = [bx / w, by / h, bw / w, bh / h]

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
