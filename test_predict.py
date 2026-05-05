import cv2
import numpy as np
from model.sign_detector import detector

print("--- Testing predict function with a blank image ---")
# Create a blank 480x640 blank image
blank_image = np.zeros((480, 640, 3), dtype=np.uint8)

try:
    result = detector.predict(blank_image)
    print("Result:", result)
except Exception as e:
    print("Error:", e)
