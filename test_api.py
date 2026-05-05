import requests
import base64
import os

print("--- Testing /detect/webcam ---")
# To test webcam, we need a base64 encoded image string like "data:image/jpeg;base64,..."
# Create a dummy 1x1 black image in base64
# This is a 1x1 px black PNG in base64
dummy_base64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="

try:
    response = requests.post("http://127.0.0.1:5000/detect/webcam", json={"image": dummy_base64})
    print("Status Code:", response.status_code)
    print("Response:", response.json())
except Exception as e:
    print("Error:", e)

print("\n--- Testing /detect/video ---")
# To test video, we need to upload a small dummy mp4 file
# For now, let's just make sure the endpoint doesn't crash on invalid files or missing files
try:
    # First test missing file
    response = requests.post("http://127.0.0.1:5000/detect/video")
    print("No file status:", response.status_code)
    
    # Test text file pretending to be video
    files = {'file': ('dummy.mp4', b"dummy content", 'video/mp4')}
    response = requests.post("http://127.0.0.1:5000/detect/video", files=files)
    print("Dummy file status:", response.status_code)
    print("Dummy file response:", response.json())
except Exception as e:
    print("Error:", e)
