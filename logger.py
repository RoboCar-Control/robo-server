from datetime import datetime

def log_event(event_type, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{event_type.upper()}] {message}")
    # You can also write to a file if needed
