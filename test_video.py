import requests
import io

print("--- Testing /detect/video with dummy file ---")
# Create a dummy file in memory
dummy_file = io.BytesIO(b"this is not a real video, but it will test the route's error handling")
dummy_file.name = "dummy.mp4"

try:
    files = {'file': dummy_file}
    response = requests.post("http://127.0.0.1:5000/detect/video", files=files)
    print("Status Code:", response.status_code)
    print("Response:", response.json())
except Exception as e:
    print("Error:", e)
