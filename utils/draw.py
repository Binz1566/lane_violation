import cv2

def draw_box(frame, x1, y1, x2, y2, text, color):
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    cv2.putText(frame, text, (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

def draw_center(frame, cx, cy):
    cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)

def draw_lanes(frame, lane_motor, lane_car):
    cv2.polylines(frame, [lane_motor], True, (255, 255, 0), 2)
    cv2.polylines(frame, [lane_car], True, (0, 255, 255), 2)