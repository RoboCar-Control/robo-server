from robot_hat import ADC
from picarx import Picarx
# from vilib import Vilib
from time import sleep, time, strftime, localtime
from robot_hat.utils import reset_mcu
import os
import cv2
import logger
import base64
import time

user = os.getlogin()
user_home = os.path.expanduser(f'~{user}')
battery = ADC('A4')

reset_mcu()
sleep(0.2)
px = Picarx()

status = ''
def move(direction, speed):
    if direction == 'forward':
        status = direction
        px.set_dir_servo_angle(0)
        px.forward(speed)
    elif direction == 'left':
        status = direction
        px.set_dir_servo_angle(-30)
        px.forward(speed)
    elif direction == 'right':
        status = direction
        px.set_dir_servo_angle(30)
        px.forward(speed)
    elif direction == 'backward':
        status = direction
        px.set_dir_servo_angle(0)
        px.backward(speed)

def stop():
    px.stop()

def increase_speed(speed):
    move(status, speed)

def start_autonomous():
    POWER = 50
    SafeDistance = 40
    DangerDistance = 20

    try:
        while True:
            distance = round(px.ultrasonic.read(), 2)
            print(f"Distance: {distance} cm", end=' - ')

            if distance >= SafeDistance:
                print("Moving forward")
                px.set_dir_servo_angle(0)
                px.forward(POWER)
            elif DangerDistance <= distance < SafeDistance:
                print("Avoiding obstacle")
                px.set_dir_servo_angle(30)
                px.forward(POWER)
                time.sleep(0.1)
            else:
                print("Too close! Reversing")
                px.set_dir_servo_angle(-30)
                px.backward(POWER)
                time.sleep(0.5)
    except KeyboardInterrupt:
        print("Autonomous mode interrupted.")
    finally:
        px.forward(0)
        print("Motors stopped.")

# def take_photo():
#     _time = strftime('%Y-%m-%d-%H-%M-%S',localtime(time()))
#     name = 'photo_%s'%_time
#     path = f"{user_home}/Pictures/picar-x/"
#     Vilib.take_photo(name, path)
#     print('\nphoto save as %s%s.jpg'%(path,name))

def stop_autonomous():
    px.stop()

def get_battery_voltage():
    voltage = battery.read()
    return voltage

def generate_frames():
    camera = cv2.VideoCapture(0)
    camera.set(3, 640)
    camera.set(4, 480)
    if not camera.isOpened():
        logger.error("Camera failed to open")
        return

    while True:
        success, frame = camera.read()
        print(frame)
        if not success:
            print("Failed to read frame from camera")
            break

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            logger.error("Failed to encode frame")
            continue

        jpg_as_text = base64.b64encode(buffer).decode('utf-8')
        yield jpg_as_text

        time.sleep(0.03)
    camera.release()