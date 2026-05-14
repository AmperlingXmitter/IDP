from picamera2 import Picamera2, Preview
import tkinter as tk
import time

# Use tkinter to get the hardware's native resolution
root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.destroy()

print(f"Screen width: {screen_width}")
print(f"Screen height: {screen_height}")

camera = Picamera2()
camera.start_preview(Preview.QTGL, x=0, y=0, width=screen_width, height=screen_height)
camera.start()

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
