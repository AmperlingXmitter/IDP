import sys
# --- FIX FOR PYTHON 3.12+ (Module 'imp' removal) ---
try:
    import imp
except ImportError:
    import types
    # Create a fake 'imp' module to satisfy old library dependencies
    fake_imp = types.ModuleType('imp')
    sys.modules['imp'] = fake_imp
    # Add the specific functions flatbuffers looks for
    fake_imp.find_module = lambda name, path=None: None
    print("Python 3.13 detected: Applied 'imp' module shim.")

print("Importing dependencies...")

from picamera2 import Picamera2, Preview
from libcamera import controls
from libcamera import Transform
from gpiozero import Button
from pynput import keyboard

import tkinter as tk
import time
import datetime
import threading

from MainDependencies import settings
from MainDependencies import api_bridge
from MainDependencies.toaster import Toaster
from MainDependencies.logger import start_logging
from MainDependencies.createMissingFolders import create_folder_if_missing

from ImageProcessingAlgorithms.deploy import run_full_process as Deploy
#from ImageProcessingAlgorithms.deploy import preprocess_image as resizer
#from ImageProcessingAlgorithms.deploy import analyze_image as segmenter
#from ImageProcessingAlgorithms.deploy import overlay_mask as classifier

print("Imported dependencies.")

#--------------------SETUP--------------------
print("Starting setup process...")

# Folder Paths
image_folder = settings.image_folder
capture_folder = settings.capture_folder
resized_folder = settings.resized_folder
segmented_folder = settings.segmented_folder
overlayed_folder = settings.overlayed_folder
log_folder = settings.log_folder

imp_paths = {
    "image": image_folder,
    "capture": capture_folder,
    "resized": resized_folder,
    "segmented": segmented_folder,
    "overlayed": overlayed_folder
}

print("Folder Paths:");
print(f"- Image Folder Path: {image_folder}")
print(f"- Capture Folder Path: {capture_folder}")
print(f"- Resized Folder Path: {resized_folder}")
print(f"- Segmented Folder Path: {segmented_folder}")
print(f"- Overlayed Folder Path: {overlayed_folder}")
print(f"- Log Folder Path: {log_folder}")

create_folder_if_missing(image_folder)
create_folder_if_missing(capture_folder)
create_folder_if_missing(resized_folder)
create_folder_if_missing(segmented_folder)
create_folder_if_missing(overlayed_folder)
create_folder_if_missing(log_folder)

# Setup Logger
maximum_log_files = settings.maximum_log_files
start_logging(log_folder, count = maximum_log_files)

print("Logger:")
print(f"- Started logging to {log_folder}.")
print(f"- Maximum Number of Log Files: {maximum_log_files}")

# Setup API Server
print("API Server:")
try:
    api_bridge.start_api()
    print("- API Server started on port 5000")
except Exception as error_text:
    print(f"API Error: {error_text}")

# Setup GPIO
GPIO_pin = settings.GPIO_pin
bounce_duration = settings.bounce_duration
capture_button = Button(GPIO_pin, pull_up=True, bounce_time = bounce_duration)

print("Button:")
print(f"- GPIO Pin Number: {GPIO_pin}")
print(f"- Bounce Duration: {bounce_duration} seconds")

# Setup Camera
# Preview FPS
min_fps = settings.min_fps
max_fps = settings.max_fps
# Preview Resolution
preview_width = settings.preview_width
preview_height = settings.preview_height
# Camera Capture Resolution
camera_width = settings.camera_width
camera_height = settings.camera_height
# Output Image
image_format = settings.image_format

print("Camera:")
print(f"- Preview FPS Range: {min_fps} to {max_fps}")
print(f"- Preview Resolution: {preview_width} x {preview_height} px")
print(f"- Camera Resolution: {camera_width} x {camera_height} px")
print(f"- Captured Image Format: {settings.image_format} File")
print(f"- Captured Image Quality: {settings.image_quality}%")

camera = Picamera2()
camera.options["quality"] = settings.image_quality
min_fps_micros = int(1000000 / min_fps)
max_fps_micros = int(1000000 / max_fps)

preview_config = camera.create_preview_configuration(
    main={"size": (preview_width, preview_height), "format": "YUV420"},
    controls={
        "FrameDurationLimits": (min_fps_micros, max_fps_micros),
        "NoiseReductionMode": 1,  # 1 = Fast (Minimal ISP overhead)
        "AeConstraintMode": 1,    # 1 = Highlight (Prevents slow exposure calcs)
        "AfMode": 2,              # 2 = Enable Continuous Autofocus
    },
    buffer_count=7, # just enough to reduce stutter
    #,transform=Transform(hflip = True, vflip = True) # flip upside down
)

capture_config = camera.create_still_configuration(
    main={"size": (camera_width, camera_height), "format": "YUV420"}, 
    controls={
        "NoiseReductionMode": 2,  # 2 = HighQuality (Best detail, slower)
        "Sharpness": 2.0,          # Slight boost to edge clarity
        "AfMode": 2,       # <--- NEW: Enable Continuous Autofocus
    }
    #,transform=Transform(hflip = True, vflip = True) # flip upside down
)

# Toaster Setup
root = tk.Tk()
root.withdraw() # Keep Hidden Root Window Alive
root.overrideredirect(True)
# Sliding System
ui_toaster = Toaster(root)
# Get Native Resolution
screen_width = ui_toaster.screen_width
screen_height = ui_toaster.screen_height

print("Toaster:")
print(f"- Screen Resolution: {screen_width} x {screen_height} px")

# Setup Camera Preview
camera.configure(preview_config)
print("Starting camera preview...")
try:
    camera.start_preview(Preview.QTGL, x=0, y=0, width=screen_width, height=screen_height)
    camera.start()
    time.sleep(2)
except Exception as error_text:
    print(f"Preview error: {error_text}")

print("Camera is ready.")

# Setup System Lock
is_ai_busy = False

api_bridge.latest_data["status"] = "System Ready!"

print("Setup process finished.")

#--------------------FUNCTIONS--------------------

#####--------------------FLAG FUNCTIONS--------------------

def update_status(status):
    api_bridge.latest_data["status"] = status      
    print(status)
    ui_toaster.send(status)
    time.sleep(1)

def set_is_ai_busy_flag(flag):
    global is_ai_busy
    
    is_ai_busy = flag
    
    if is_ai_busy == False:
        update_status("Standby: System Ready!")
    
    print(f"Is AI Busy?: Set to {flag}.")
    
def get_is_ai_busy_flag():
    global is_ai_busy
    
    if is_ai_busy:
        print("Error: System Busy... Please wait.")
        ui_toaster.send("Error: System Busy... Please wait.")
        update_status(api_bridge.latest_data["status"])
        time.sleep(1)
    
    return is_ai_busy
    
#####--------------------UI FUNCTIONS--------------------

def show_user_guide():
    print("--- USER GUIDE ---")
    print("1. Press the BUTTON to capture.")
    print("2. Press [SPACEBAR] to capture.")
    print("3. Press [Q] to exit.")
    print("4. Press [H] for help.")

    ui_toaster.send("4. Press [H] for help.")
    time.sleep(1)
    ui_toaster.send("3. Press [Q] to exit.")
    time.sleep(1)
    ui_toaster.send("2. Press [SPACEBAR] to capture.")
    time.sleep(1)
    ui_toaster.send("1. Press the BUTTON to capture.")
    time.sleep(1)
    ui_toaster.send("USER GUIDE")
    time.sleep(1)

#####--------------------IMAGE PROCESSING FUNCTIONS--------------------

def execute_image_processing(image_path, timestamp):
    global is_ai_busy
    
    try:
        result = Deploy(
            image_path,
            imp_paths,
            timestamp,
            update_status
        )
        
        if result["detected"] == False:
            return
        
        # STEP 1: SEGMENTATION
        #update_status("AI Process: Segmenting Image...")
        #segment = segmenter.evaluate(image_path, analysis_folder, timestamp)
        #update_status("Success: AI Segmented the Image!")
        
        #ratio = segment["ratio"]
        
        #print(f"Ratio: {ratio:.4f}")
        #ui_toaster.send(f"Ratio: {ratio}")
        #time.sleep(1)

        # STEP 2: CLASSIFICATION
        #update_status("AI Process: Classifying Image...")
        #result = classifier.predict_image(image_path)
        #update_status("Success: AI Classified the Image!")        
        
        #grade = result["class"]
        #confidence = result["confidence"] * 100
        
        #print(f"Grade: {grade}), Confidence: {confidence:.2f}%")
        #ui_toaster.send(f"Grade: {grade}), Confidence: {confidence:.2f}%")
        #time.sleep(1)
        
        # Update Data in main.py
        api_bridge.latest_data.update({
            "status": "Success: AI Scan Complete!",
            "timestamp": timestamp,
            "percentage": round(float(result["percentage"]), 2),
            "grade": result["grade"],
            "confidence": round(float(result["confidence"]), 2),
            "original_image" : image_path,
            "segmented_image" : result["segmented_path"],
            "overlayed_image" : result["overlayed_path"]
        })
        
        update_status("Success: AI Scan Complete!")
        
    except Exception as error_text:
        update_status("Error: AI Scan Failed.")       
        print(f"- {error_text}")
    
    finally:
        time.sleep(10)
        set_is_ai_busy_flag(False) # UNLOCK NO MATTER WHAT

#####--------------------CAMERA FUNCTIONS--------------------

def execute_capture_process(image_path, timestamp):
    try:
        camera.switch_mode_and_capture_file(capture_config, image_path)
        update_status("Success: Image Saved!")
        time.sleep(1)
        
        # Start Image Processing
        threading.Thread(target=execute_image_processing, args=(image_path, timestamp), daemon=True).start()
        
    except Exception as error_text:
        update_status("Error: Capture Failed.")
        print(f"- {error_text}")
        time.sleep(10)
        set_is_ai_busy_flag(False)

def capture_photo():
    if get_is_ai_busy_flag():
        return
    
    set_is_ai_busy_flag(True) # LOCK

    update_status("AI Process: Capturing Image...")
            
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    image_path = f"{capture_folder}capture_{timestamp}{image_format}"

    # Capture Image
    threading.Thread(target=execute_capture_process, args=(image_path, timestamp), daemon=True).start()

#####--------------------Input FUNCTIONS--------------------

# Keyboard Trigger
def on_press(key):
    try:
        # Quit on 'q'/'Q'
        if hasattr(key, 'char') and key.char.lower() == 'q':
            print(f"Input: {key} pressed! Shutting Down!")
            ui_toaster.send(f"Input: {key} pressed!")
            time.sleep(1)
            
            update_status("Attention: System Shut Down!")
            time.sleep(10)
            
            root.after(0, root.destroy)
            time.sleep(5)
            
            return False

        # Capture Image on Spacebar
        if key == keyboard.Key.space:
            print("Input: Spacebar pressed!")
            ui_toaster.send("Input: Spacebar pressed!")
            time.sleep(1)
            
            if get_is_ai_busy_flag() == True:            
                return
            
            capture_photo()
        
        # Show Help on 'h'/'H'
        if hasattr(key, 'char') and key.char.lower() == 'h':
            print(f"Input: {key} pressed!")
            ui_toaster.send(f"Input: {key} pressed!")
            time.sleep(1)
            
            if get_is_ai_busy_flag() == True:            
                return
            
            show_user_guide()
            
    except Exception as error_text:
        print(f"Keyboard error: {error_text}")

def check_for_remote_trigger():
    if api_bridge.trigger_requested:
        print("Input: Remote trigger received!")
        ui_toaster.send("Input: Remote trigger received!")
        
        if get_is_ai_busy_flag() == True:            
            return
        
        api_bridge.trigger_requested = False
        capture_photo()
    
    root.after(100, check_for_remote_trigger)

#--------------------MAIN--------------------

print("Starting main process...")

update_status("Standby: System Ready!")

print("Showing user guide...")
show_user_guide()

# Physical Button Trigger
print("Starting button listener...")
capture_button.when_pressed = capture_photo

# Non-blocking Keyboard Listener
listener = keyboard.Listener(on_press=on_press)
print("Starting keyboard listener...")
listener.start()

# Remote Trigger
print("Starting remote trigger listener...")
check_for_remote_trigger()

try:
    root.mainloop()
finally:
    print("Finished main process.")
    print("Starting shut down process...")
    
    print("Closing preview...")
    camera.stop_preview()
    
    print("Closing camera...")
    camera.close()
    
    print("Closing keyboard listener...")
    listener.stop()
    
    print("Shut down process finished.")



