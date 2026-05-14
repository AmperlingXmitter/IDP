import tkinter as tk
import threading
import time
import queue

# --- 1. SETUP THREAD-SAFE COMMUNICATION ---
toast_queue = queue.Queue()
active_toasts = 0
toast_lock = threading.Lock()

def request_toast(message):
    """Call this from ANY thread (Camera, AI, etc.)"""
    toast_queue.put(message)

# --- 2. MAIN THREAD UI HANDLER ---
def check_for_toasts(root):
    """This function runs in the Main Thread and watches the queue."""
    try:
        while True:
            msg = toast_queue.get_nowait()
            create_toast_window(msg) # Build the UI here
    except queue.Empty:
        pass
    
    # Check again in 250ms
    root.after(250, lambda: check_for_toasts(root))

def create_toast_window(message):
    """Actually creates the Toplevel window (called only by main thread)"""
    global active_toasts
    
    # Use Toplevel (secondary window) instead of Tk()
    toast = tk.Toplevel() 
    toast.withdraw()
    
    w, h = 240, 40
    x = (screen_width // 2) - (w // 2)
    top_y = int(screen_height * 0.20)
    
    toast.overrideredirect(True)
    toast.attributes("-topmost", True)
    toast.deiconify()
    
    bg_color = "#333333"
    if "Grade" in message: bg_color = "#2e7d32"
    elif "Error" in message: bg_color = "#c62828"
    
    label = tk.Label(toast, text=message, font=("Arial", 10, "bold"), 
                    bg=bg_color, fg="white", wraplength=w-10)
    label.pack(expand=True, fill='both')

    with toast_lock:
        my_pos = active_toasts
        active_toasts += 1

    def refresh():
        if not toast.winfo_exists(): return
        with toast_lock:
            visual_index = (active_toasts - 1) - my_pos
            current_y = top_y + (visual_index * (h + 5))
            toast.geometry(f"{w}x{h}+{x}+{current_y}")
        toast.after(250, refresh)

    refresh()
    toast.after(10000, toast.destroy)

# --- 3. EXECUTION ---
root = tk.Tk()
root.withdraw() # The root must stay alive for the whole program

# Get screen size once
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Start the 'Queue Watcher'
check_for_toasts(root)

# Simulate background threads (like your Camera)
def simulate_captures():
    for i in range(5):
        request_toast(f"Image Captured {i}!")
        time.sleep(1)

threading.Thread(target=simulate_captures, daemon=True).start()

print("Main loop running. Close the terminal or program to stop.")
root.mainloop()
