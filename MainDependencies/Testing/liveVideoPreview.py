from picamera2 import Picamera2
import time

camera = Picamera2()

# Create a configuration for previewing
# This defaults to a resolution suitable for your monitor
config = camera.create_preview_configuration()
camera.configure(config)

# Start the camera and the preview window
camera.start(show_preview=True)

print("Live stream started. Press Ctrl+C in the terminal to stop.")

try:
    # Keep the window open
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nClosing camera...")
finally:
    camera.stop_preview()
    camera.close()
