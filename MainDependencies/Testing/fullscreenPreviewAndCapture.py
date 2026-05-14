from picamera2 import Picamera2, Preview
from libcamera import controls
from gpiozero import Button
from pynput import keyboard
import tkinter as tk
import time
import datetime
import os
import threading

folder = "/home/sixseven/IDP/Prototype1/Version1/Captures/"
image_format = ".jpg"

# Setup GPIO
GPIO_pin = 26
capture_button = Button(GPIO_pin, pull_up=True, bounce_time=0.2)

# Use tkinter to get the hardware's native resolution
root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.destroy()

print(f"Screen width: {screen_width}")
print(f"Screen height: {screen_height}")

# Setup Camera
camera = Picamera2()

fps_micros = int(1000000 / 10)

preview_config = camera.create_preview_configuration(
    # Using 'main' for the display window, but keeping resolution tiny
    main={"size": (256, 144), "format": "YUV420"},
    controls={
        "FrameDurationLimits": (fps_micros, fps_micros),
        "NoiseReductionMode": 1,  # 1 = Fast (Minimal ISP overhead)
        "AeConstraintMode": 1,    # 1 = Highlight (Prevents slow exposure calcs)
    },
    # Set buffer_count to 6 to handle background tasks without stutter
    buffer_count=6 
)

capture_config = camera.create_still_configuration(
    # Targeting the full resolution of the IMX708 sensor
    main={"size": (4608, 2592), "format": "YUV420"}, 
    controls={
        "NoiseReductionMode": 2,  # 2 = HighQuality (Best detail, slower)
        "Sharpness": 1.5          # Slight boost to edge clarity
    }
)

# Set the global JPEG quality to max (100 is no compression)
camera.options["quality"] = 100

#preview_config = camera.create_preview_configuration()
#capture_config = camera.create_still_configuration()

camera.configure(preview_config)

# Setup Preview
print("Starting preview...")
camera.start_preview(Preview.QTGL, x=0, y=0, width=screen_width, height=screen_height)
camera.start()
time.sleep(2)
print("Camera is ready!")

# Stop Event
stop_signal = threading.Event()

def capture_photo():
    # Create folder if it doesn't exist
    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
            print(f"Folder created at: {folder}")
        except Exception as error_text:
            print(f"Folder creation failed: {error_text}")
            
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    image_path = f"{folder}capture_{timestamp}{image_format}"
    
    try:
        camera.switch_mode(capture_config)
        camera.capture_file(image_path)
        camera.switch_mode(preview_config)
        print(f"Capture successful! Saved to: {image_path}")
    except Exception as error_text:
        print(f"Capture failed: {error_text}")

# Keyboard Trigger
def on_press(key):
    try:
        # Capture on Spacebar
        if key == keyboard.Key.space:
            print("Spacebar pressed!")
            capture_photo()
        # Quit on 'q'
        if hasattr(key, 'char') and key.char.lower() == 'q':
            print("Q pressed! Quitting...")
            stop_signal.set()
            return False
    except Exception as error_text:
        print(f"Keyboard error: {error_text}")

# Physical Button Trigger
print("Starting button listener...")
capture_button.when_pressed = capture_photo

# Non-blocking Keyboard Listener
listener = keyboard.Listener(on_press=on_press)
print("Starting keyboard listener...")
listener.start()

print("--- CAPTURE TRIGGERS ---")
print(f"1. Press the PHYSICAL BUTTON (GPIO {GPIO_pin})")
print("2. Press [SPACEBAR] on keyboard")
print("3. Press [Q] to exit")

try:
    stop_signal.wait()
finally:
    print("Closing preview...")
    camera.stop_preview()
    
    print("Closing camera...")
    camera.close()
    
    print("Closing keyboard listener...")
    listener.stop()
    print("Done.")


