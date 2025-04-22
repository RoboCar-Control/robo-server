import cv2
import logger
import time
import base64

def generate_frames():
    print("teste")
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        logger.error("Camera failed to open")
        print("test")
        return

    while True:
        success, frame = camera.read()
        if not success:
            logger.error("Failed to read frame from camera")
            break

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            logger.error("Failed to encode frame")
            continue

        jpg_as_text = base64.b64encode(buffer).decode('utf-8')
        print(jpg_as_text)
        yield jpg_as_text

        time.sleep(0.03)
    #camera.release()

if __name__ == '__main__':
    generate_frames()