import cv2
import numpy as np
 
# Global variables for color detection
selected_hsv = np.array([0, 0, 255])  # Default to white
h_tol, s_tol, v_tol = 10, 100, 100  # Default tolerances
running = True
def hex_to_hsv(hex_code):
    """Convert hex color to HSV"""
    hex_code = hex_code.lstrip('#')
    bgr = np.uint8([[
        [int(hex_code[4:6], 16), int(hex_code[2:4], 16), int(hex_code[0:2], 16)]
    ]])
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    return hsv[0][0]
 
def get_flexible_range(hsv, h_tol, s_tol, v_tol):
    """Calculate HSV range based on tolerances"""
    h, s, v = hsv
    lower = np.array([max(h - h_tol, 0), max(s - s_tol, 0), max(v - v_tol, 0)])
    upper = np.array([min(h + h_tol, 179), min(s + s_tol, 255), min(v + v_tol, 255)])
    return lower, upper
 
def process_frame(frame):
    """Process a single frame for color detection"""
    global selected_hsv, h_tol, s_tol, v_tol
    
    # Get HSV bounds
    lower, upper = get_flexible_range(selected_hsv, h_tol, s_tol, v_tol)
    
    # Convert and detect
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_frame, lower, upper)
    
    # Find and draw bounding boxes
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    detections = []
    
    for cnt in contours:
        if cv2.contourArea(cnt) > 500:
            x, y, w, h = cv2.boundingRect(cnt)
            detections.append({
                'x': x,
                'y': y,
                'width': w,
                'height': h
            })
            
            # Draw on frame (for visualization)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, "Detected", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    return frame, detections
 
def video_processing():
    """Main video processing loop"""
    cap = cv2.VideoCapture(0)
    
    while running:
        ret, frame = cap.read()
        if not ret:
            break
            
        processed_frame, detections = process_frame(frame)
        # For local display (optional)
        cv2.imshow('Color Detection', processed_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
 
    cap.release()
    cv2.destroyAllWindows()
 
#video_processing()
 
 
# @socketio.on('startDetection')
# def handle_start():
#     """Start the color detection"""
#     global running
#     running = True
#     socketio.start_background_task(video_processing)
#     print("Color detection started")
 
# @socketio.on('stopDetection')
# def handle_stop():
#     """Stop the color detection"""
#     global running
#     running = False
#     print("Color detection stopped")
 
# @socketio.on('setColor')
# def handle_set_color(data):
#     """Handle color updates from frontend"""
#     global selected_hsv
    
#     try:
#         if data['type'] == 'hex':
#             selected_hsv = hex_to_hsv(data['value'])
#         elif data['type'] == 'hsv':
#             h, s, v = data['value']['h'], data['value']['s'], data['value']['v']
#             selected_hsv = np.array([h, s, v])
        
#         print(f"Updated color to HSV: {selected_hsv}")
#         socketio.emit('colorUpdated', {'hsv': selected_hsv.tolist()})
#     except Exception as e:
#         print(f"Error setting color: {str(e)}")
 
# @socketio.on('setTolerance')
# def handle_set_tolerance(data):
#     """Handle tolerance updates from frontend"""
#     global h_tol, s_tol, v_tol
    
#     try:
#         h_tol = data.get('h', h_tol)
#         s_tol = data.get('s', s_tol)
#         v_tol = data.get('v', v_tol)
#         print(f"Updated tolerances - H: {h_tol}, S: {s_tol}, V: {v_tol}")
#     except Exception as e:
#         print(f"Error setting tolerances: {str(e)}")