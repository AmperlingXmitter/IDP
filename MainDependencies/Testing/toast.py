import tkinter as tk

def show_toast(message, duration=5000):
    toast = tk.Tk()
    toast.title("")
    # Center the toast on the screen
    w, h = 300, 50
    x = (toast.winfo_screenwidth() // 2) - (w // 2)
    y = (toast.winfo_screenheight() // 2) - (h // 2)
    
    toast.geometry(f"{w}x{h}+{x}+{y}")
    toast.overrideredirect(True) # Removes window borders/buttons
    toast.attributes("-topmost", True) # Stays above the preview
    
    label = tk.Label(toast, text=message, font=("Arial", 14), bg="black", fg="white")
    label.pack(expand=True, fill='both')
    
    # Close after 'duration' milliseconds
    toast.after(duration, toast.destroy)
    toast.mainloop
    
show_toast("Bruh.")