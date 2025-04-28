import cv2
import numpy as np
import time
import base64

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
 
def process_frame(frame, color):
    """Process a single frame for color detection"""
    global selected_hsv, h_tol, s_tol, v_tol

    selected_hsv = hex_to_hsv(color)
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
