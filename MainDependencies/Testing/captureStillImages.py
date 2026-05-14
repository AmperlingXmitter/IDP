from picamera2 import Picamera2
import time
import datetime

camera = Picamera2()

# Configure camera for still image capture
camera_configuration = camera.create_still_configuration()
camera.configure(camera_configuration)

# Start camera
camera.start()
time.sleep(2) # Allow camera to adjust exposure, white balance, etc.

# Create a unique filename using the current date and time
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
# Ensure the path ends with a filename like 'image_20260111_0835.jpg'
image_path = f"/home/danial/IDP/Ver1/StillImages/capture_{timestamp}.jpg"

try:
    camera.capture_file(image_path)
    print(f"Success! Image saved at: {image_path}")
except Exception as e:
    print(f"An error occurred: {e}")

print(f"Image saved at {image_path}")

# Stop camera
camera.close()
