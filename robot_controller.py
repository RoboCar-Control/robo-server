#from robot_hat import battery
from picarx import Picarx
from vilib import Vilib
from time import sleep, time, strftime, localtime
from robot_hat.utils import reset_mcu
import os

user = os.getlogin()
user_home = os.path.expanduser(f'~{user}')

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
            print("distance: ",distance)
            if distance >= SafeDistance:
                px.set_dir_servo_angle(0)
                px.forward(POWER)
            elif distance >= DangerDistance:
                px.set_dir_servo_angle(30)
                px.forward(POWER)
                time.sleep(0.1)
            else:
                px.set_dir_servo_angle(-30)
                px.backward(POWER)
                time.sleep(0.5)
    finally:
        px.forward(0)

def take_photo():
    _time = strftime('%Y-%m-%d-%H-%M-%S',localtime(time()))
    name = 'photo_%s'%_time
    path = f"{user_home}/Pictures/picar-x/"
    Vilib.take_photo(name, path)
    print('\nphoto save as %s%s.jpg'%(path,name))

def stop_autonomous():
    px.stop()

# def get_battery_voltage():
#     voltage = battery.get_voltage()
#     return voltage
