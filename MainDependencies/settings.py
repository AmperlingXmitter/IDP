# Folder Paths
image_folder = "/home/sixseven/IDP/Prototype1/Version2/Images/"
capture_folder = "/home/sixseven/IDP/Prototype1/Version2/Images/Captures/"
resized_folder = "/home/sixseven/IDP/Prototype1/Version2/Images/Resized/"
segmented_folder = "/home/sixseven/IDP/Prototype1/Version2/Images/Segmented/"
overlayed_folder = "/home/sixseven/IDP/Prototype1/Version2/Images/Overlayed/"
log_folder = "/home/sixseven/IDP/Prototype1/Version2/Logs/"

# Logger
maximum_log_files = 30

# Button
GPIO_pin = 26
bounce_duration = 0.2 # seconds

# Camera
# Preview FPS
min_fps = 60
max_fps = 60
# Preview Resolution (px)
preview_width = 640
preview_height = 360
# Camera Capture Resolution (px)
camera_width = 4608 # 4608 max, 224 min
camera_height = 2592 # 2592 max, 224 min
# Output Image
image_format = ".jpg"
image_quality = 100 # 100 min compression, 0 max compression