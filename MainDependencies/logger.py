import sys
import os
import datetime

class RollingLogger:
    def __init__(self, log_dir, max_logs=10):
        self.log_dir = os.path.abspath(log_dir)
        self.max_logs = max_logs
        os.makedirs(self.log_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.filename = os.path.join(self.log_dir, f"session_{timestamp}.log")
        
        self.terminal = sys.stdout
        self.log_file = open(self.filename, "a", encoding="utf-8")
        self.cleanup()

    def write(self, message):
        self.terminal.write(message)
        self.log_file.write(message)
        self.log_file.flush()
        os.fsync(self.log_file.fileno()) # Force write to physical disk

    def flush(self):
        self.terminal.flush()
        self.log_file.flush()

    def cleanup(self):
        files = [os.path.join(self.log_dir, f) for f in os.listdir(self.log_dir) if f.endswith('.log')]
        files.sort(key=os.path.getmtime)
        while len(files) > self.max_logs:
            oldest = files.pop(0)
            try:
                os.remove(oldest)
            except: pass

def start_logging(directory, count=10):
    logger_instance = RollingLogger(directory, count)
    sys.stdout = logger_instance
    sys.stderr = logger_instance
