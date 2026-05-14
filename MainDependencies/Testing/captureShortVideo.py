from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
import time
import datetime

camera = Picamera2()

# 1. Configure for video (this optimizes for a steady frame rate)
config = camera.create_video_configuration()
camera.configure(config)

# 2. Start the camera (keeping your working preview)
camera.start(show_preview=True)

encoder = H264Encoder(bitrate=10000000)

# Create a unique filename for the video
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
video_path = f"/home/danial/IDP/Ver1/Videos/video_{timestamp}.h264"

print(f"Recording started: {video_path}")

# 3. Start recording to the file
camera.start_recording(encoder, video_path)

# 4. Record for 10 seconds
time.sleep(10)

# 5. Stop recording and clean up
camera.stop_recording()
print("Recording finished.")

camera.close()
