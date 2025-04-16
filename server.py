import eventlet
eventlet.monkey_patch()

from flask import Flask, Response
from flask_socketio import SocketIO, emit
import robot_controller as robot
import logger


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins='*')

@app.route('/')
def index():
    return "Picar-X WebSocket Control Server"

# @app.route('/video_feed')
# def video_feed():
#     return Response(generate_frames(),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')

@socketio.on('connect')
def on_connect():
    logger.log_event('connect', 'Client connected')
    emit('status', {'message': 'Connected to robot server'})

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

@socketio.on('start_recording')
def on_start_recording():
    logger.log_event('video', "Started recording")
    emit('status', {'message': "Recording started"})
    # Add actual recording logic here

@socketio.on('stop_recording')
def on_stop_recording():
    logger.log_event('video', "Stopped recording")
    emit('status', {'message': "Recording stopped"})
    # Add actual stop-recording logic here

# @socketio.on('get_battery')
# def handle_battery():
#     voltage = robot.get_battery_voltage()
#     emit('battery_status', {'voltage': voltage})

# @socketio.on('start_video')
# def handle_start_video():
#     start_video_stream()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
