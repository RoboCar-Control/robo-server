import base64
from io import BytesIO
from PIL import Image
from time import sleep
from vilib import Vilib
from flask_socketio import emit
from threading import Thread

def video_loop():
    Vilib.camera_start(vflip=False, hflip=False)
    sleep(2)

    try:
        while True:
            # Get frame from camera
            frame = Vilib.get_frame()
            if frame is not None:
                # Convert to PIL Image
                image = Image.fromarray(frame)

                # Encode to JPEG
                buffer = BytesIO()
                image.save(buffer, format='JPEG')
                jpg_data = buffer.getvalue()

                # Convert to base64
                encoded = base64.b64encode(jpg_data).decode('utf-8')

                # Emit via WebSocket
                emit('video_frame', {'image': encoded})

                sleep(0.05)  # ~20 FPS
    except KeyboardInterrupt:
        print('\nStopping camera...')
        Vilib.camera_close()

def start_video_stream():
    thread = Thread(target=video_loop)
    thread.daemon = True
    thread.start()