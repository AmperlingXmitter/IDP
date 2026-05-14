from picamera2 import Picamera2, Preview
from libcamera import controls
from gpiozero import Button
from pynput import keyboard
import tkinter as tk
import datetime
import os
import time
import threading
from MainDependencies.toaster import Toaster
# from ImageProcessingAlgorithms import *

#--------------------SETUP--------------------

folder = "/home/sixseven/IDP/Prototype1/Version1/Captures/"

# Setup GPIO
GPIO_pin = 26
capture_button = Button(GPIO_pin, pull_up=True, bounce_time=0.2)

# Tkinter Toaster Setup
root = tk.Tk()
root.withdraw() # Keep the hidden root window alive
# Setup Toaster Sliding System
ui_toaster = Toaster(root)
# Get Native Resolution
screen_width = ui_toaster.screen_width
screen_height = ui_toaster.screen_height

# Setup Camera
camera = Picamera2()
min_fps = 10
max_fps = 10
min_fps_micros = int(1000000 / min_fps)
max_fps_micros = int(1000000 / max_fps)
# Preview Optimised for Speed
preview_config = camera.create_preview_configuration(
    main={"size": (64, 36), "format": "YUV420"},
    controls={
        "FrameDurationLimits": (min_fps_micros, max_fps_micros),
        "NoiseReductionMode": 1,  # 1 = Fast (Minimal ISP overhead)
        "AeConstraintMode": 1,    # 1 = Highlight (Prevents slow exposure calcs)
    },
    buffer_count=6 # just enough to reduce stutter
)
# Capture Optimised for Quality
capture_config = camera.create_still_configuration(
    main={"size": (4608, 2592), "format": "YUV420"}, 
    controls={
        "NoiseReductionMode": 2,  # 2 = HighQuality (Best detail, slower)
        "Sharpness": 1.5          # Slight boost to edge clarity
    }
)
# Set JPEG quality to max (100 = no compression)
image_format = ".jpg"
camera.options["quality"] = 100

# Setup Preview
camera.configure(preview_config)
print("Starting preview...")
try:
    camera.start_preview(Preview.QTGL, x=0, y=0, width=screen_width, height=screen_height)
    camera.start()
    time.sleep(2)
except Exception as error_text:
    print(f"Preview error: {error_text}")

print("Camera is ready!")

#--------------------FUNCTIONS--------------------

def check_folder_exists():
    # Create folder if it doesn't exist
    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
            print(f"Folder created at: {folder}")
        except Exception as error_text:
            print(f"Folder creation failed: {error_text}")

def execute_capture_process(image_path):
    try:
        camera.switch_mode_and_capture_file(capture_config, image_path)
        print(f"Capture successful! Saved to: {image_path}")
        
        ui_toaster.send("Image Saved!")
        
    except Exception as error_text:
        print(f"Capture failed: {error_text}")
        
        ui_toaster.send("Error: Capture Failed!")

def capture_photo():
    ui_toaster.send("Capturing Image...")
            
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    image_path = f"{folder}capture_{timestamp}{image_format}"
    
    threading.Thread(target=execute_capture_process, args=(image_path,), daemon=True).start()

def show_user_guide():
    print("--- USER GUIDE ---")
    print(f"1. Press the PHYSICAL BUTTON (GPIO {GPIO_pin})")
    print("2. Press [SPACEBAR] on keyboard")
    print("3. Press [Q] to exit")
    print("4. Press [H] for help")

    ui_toaster.send("4. Press [H] for help.")
    ui_toaster.send("3. Press [Q] to exit.")
    ui_toaster.send("2. Press [SPACEBAR] to capture.")
    ui_toaster.send("1. Press the BUTTON to capture.")
    ui_toaster.send("USER GUIDE:")

# Keyboard Trigger
def on_press(key):
    try:
        # Capture on Spacebar
        if key == keyboard.Key.space:
            print("Spacebar pressed!")
            capture_photo()
        # Quit on 'q'/'Q'
        if hasattr(key, 'char') and key.char.lower() == 'q':
            print("Q pressed! Quitting...")
            
            ui_toaster.send("Shutting Down!")
            
            root.after(0, root.destroy)
            return False
        if hasattr(key, 'char') and key.char.lower() == 'h':
            show_user_guide()
    except Exception as error_text:
        print(f"Keyboard error: {error_text}")

#--------------------MAIN--------------------

check_folder_exists()
show_user_guide()

# Physical Button Trigger
print("Starting button listener...")
capture_button.when_pressed = capture_photo

# Non-blocking Keyboard Listener
listener = keyboard.Listener(on_press=on_press)
print("Starting keyboard listener...")
listener.start()

try:
    root.mainloop()
finally:
    print("Closing preview...")
    camera.stop_preview()
    
    print("Closing camera...")
    camera.close()
    
    print("Closing keyboard listener...")
    listener.stop()
    
    print("Done.")
