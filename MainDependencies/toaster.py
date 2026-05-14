import tkinter as tk
import threading
import queue

class Toaster:
    def __init__(self, root):
        self.root = root
        self.toast_queue = queue.Queue()
        self.active_toasts = 0
        self.toast_lock = threading.Lock()
        
        # UI Settings
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        self.w, self.h = 240, 40
        self.top_y = int(self.screen_height * 0.15) # 15% down from top
        self.x = (self.screen_width // 2) - (self.w // 2)

        # Start the queue monitor
        self._check_queue()

    def _check_queue(self):
        """Monitors the queue for new messages."""
        try:
            while True:
                message = self.toast_queue.get_nowait()
                self._create_toast_window(message)
        except queue.Empty:
            pass
        # Refreshes every 16 ms
        self.root.after(100, self._check_queue)

    def send(self, message):
        """Public method to call from any thread."""
        self.toast_queue.put(message)

    def _create_toast_window(self, message):
        toast = tk.Toplevel(self.root)
        toast.withdraw()
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)
        
        # Color Logic
        bg_color = "#333333"
        if "AI Process:" in message: 
            bg_color = "#5865f2"
        elif "Error:" in message: 
            bg_color = "#c62828"
        elif "Success:" in message: 
            bg_color = "#2e7d32"
        elif "Input:" in message:
            bg_color = "#b59410"
        elif "Standby:" in message:
            bg_color = "#002204"
        elif "Attention:" in message:
            bg_color = "#dc143c"
        elif "Percentage:" in message or "Confidence:" in message or "Result:" in message:
            bg_color = "#2e7d32"

        label = tk.Label(toast, text=message, font=("Arial", 10, "bold"), 
                        bg=bg_color, fg="white", wraplength=self.w-10)
        label.pack(expand=True, fill='both')
        toast.deiconify()

        with self.toast_lock:
            my_pos = self.active_toasts
            self.active_toasts += 1

        def refresh():
            if not toast.winfo_exists(): return
            with self.toast_lock:
                visual_index = (self.active_toasts - 1) - my_pos
                current_y = self.top_y + (visual_index * (self.h + 5))
                toast.geometry(f"{self.w}x{self.h}+{self.x}+{current_y}")
            toast.after(100, refresh)

        refresh()
        toast.after(12000, toast.destroy)




