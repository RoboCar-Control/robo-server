import sys

sys.path.append('env/lib/python3.11/site-packages')

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
from picamera2 import Picamera2
from ultralytics import YOLO
import subprocess
import psutil

user = os.getlogin()
user_home = os.path.expanduser(f'~{user}')
battery = ADC('A4')

model = YOLO("yolov8n.pt")

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

pan_angle = 0
tilt_angle = 0
def move_head(direction):
    global pan_angle, tilt_angle

    if 'u' == direction:
        tilt_angle+=5
        if tilt_angle>30:
            tilt_angle=30
    elif 'd' == direction:
        tilt_angle-=5
        if tilt_angle<-30:
            tilt_angle=-30
    elif 'r' == direction:
        pan_angle+=5
        if pan_angle>30:
            pan_angle=30
    elif 'l' == direction:
        pan_angle-=5
        if pan_angle<-30:
            pan_angle=-30

    px.set_cam_tilt_angle(tilt_angle)
    px.set_cam_pan_angle(pan_angle)
    


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

def get_battery_voltage():
    voltage = battery.read()
    return voltage

def get_wifi_ssid():
    result = subprocess.check_output(['iwgetid', '-r'])
    ssid = result.decode('utf-8').strip()
    return ssid if ssid else "Not connected"

def get_cup_status():
    cpu_usage = psutil.cpu_percent(interval=1)
    return cpu_usage

yolo_running = True

def close_stream():
    global yolo_running
    yolo_running = False
    #generate_frames()

def generate_frames():
    camera = Picamera2()
    camera.start()
    global yolo_running
    yolo_running = True
    try:
        while yolo_running:
            frame = camera.capture_array()
            if frame.shape[2] == 4:
                frame = frame[:, :, :3]
            results = model(frame)

            model_frame = results[0].plot()
            ret, buffer = cv2.imencode('.jpg', model_frame)
            if not ret:
                print("Failed to encode frame")
                continue

            jpg_as_text = base64.b64encode(buffer).decode('utf-8')
            yield jpg_as_text

            time.sleep(0.03)
    finally:
        camera.close()