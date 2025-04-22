from flask import Flask, Response
from flask_socketio import SocketIO, emit
import robot_controller as robot
import logger


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins='*')
HOST = "0.0.0.0"
active_streams = {}

@app.route('/')
def index():
    return "Picar-X WebSocket Control Server"

def video_stream():
    for frame in robot.generate_frames():
        emit('video_frame', {'image': frame})
        socketio.sleep(0.03) 

@socketio.on('connect')
def on_connect():
    logger.log_event('connect', 'Client connected')
    battery = robot.get_battery_voltage()
    wifi = robot.get_wifi_ssid()
    cpu = robot.get_cup_status()
    emit('status', {'message': 'Connected', 'voltage': battery, 'wifi': wifi, 'cpu':cpu})

@socketio.on('manual_control')
def handle_manual_control(data):
    direction = data.get('direction')
    speed = data.get('speed', 50)
    robot.move(direction, speed)
    emit('status', {'message': f'Moving {direction} at speed {speed}'})

@socketio.on('increase_speed')
def increase_speed(data):
    speed = data.get('speed')
    robot.increase_speed(speed)
    emit('status', {'message': f"Speed increase by {speed}"})

@socketio.on('stop')
def on_stop():
    robot.stop()
    logger.log_event('manual', "Stop command received")
    emit('status', {'message': "Stopped"})

@socketio.on('start_autonomous')
def on_start_autonomous():
    robot.start_autonomous()
    logger.log_event('autonomous', "Autonomous mode started")
    emit('status', {'message': "Autonomous mode activated"})

@socketio.on('stop_autonomous')
def on_stop_autonomous():
    robot.stop_autonomous()
    logger.log_event('autonomous', "Autonomous mode stopped")
    emit('status', {'message': "Autonomous mode stopped"})

@socketio.on('video-stream')
def handle_video_stream():
    for frame in robot.generate_frames():
        socketio.emit('video_frame', {'image': frame})
        socketio.sleep(0.03)

@socketio.on('start_recording')
def on_start_recording():
    logger.log_event('video', "Started recording")
    emit('status', {'message': "Recording started"})
    # Add actual recording logic here

@socketio.on('stop_recording')
def on_stop_recording():
    logger.log_event('video', "Stopped recording")
    emit('status', {'message': "Recording stopped"})

@socketio.on("head_control")
def on_move_head(data):
    direction = data.get('direction')
    robot.move_head(direction)
    emit('status', {'message': f'Moving head {direction}'})


if __name__ == '__main__':
    print("starting server", flush=True)
    socketio.run(app, host=HOST, port=5000)
