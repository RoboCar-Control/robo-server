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
    emit('status', {'message': 'Connected to robot server', 'voltage': battery})

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
    # sid = request.sid
    # if sid in active_streams:
    #     print(f"Stream already active for {sid}")
    #     return

    # print(f"Starting stream for {sid}")
    # active_streams[sid] = True

    for frame in robot.generate_frames():
        # if not active_streams.get(sid):
        #     print(f"Stopping stream for {sid}")
        #     break
        socketio.emit('video_frame', {'image': frame})
        socketio.sleep(0.03)
        #active_streams.pop(sid, None)

    #socketio.start_background_task(target=stream)

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

# @socketio.on('disconnect')
# def handle_disconnect():
#     sid = request.sid
#     print(f"Client disconnected: {sid}")
#     active_streams.pop(sid, None)

if __name__ == '__main__':
    print("starting server", flush=True)
    socketio.run(app, host=HOST, port=5000)
