import cv2
import numpy as np
import argparse
from config import VIDEO_PATH, MODEL_PATH
from detection.detector import Detector
from tracking.tracker import Tracker
from lane.lane_detector import LaneDetector
from violation.violation_detector import ViolationDetector
from utils.draw import draw_box, draw_center, draw_lanes

def process_frame(frame, detector, tracker, lane_detector, violation_detector):
    detections = detector.detect(frame)

    for label, x1, y1, x2, y2 in detections:
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2

        obj_id = tracker.get_id(cx, cy)
        lane = lane_detector.get_lane(cx, cy)
        violation = violation_detector.check(label, lane)

        color = (0, 255, 0)
        text = f"{label} ID:{obj_id}"

        if violation:
            color = (0, 0, 255)
            text += " VIOLATION"

        draw_box(frame, x1, y1, x2, y2, text, color)
        draw_center(frame, cx, cy)

    draw_lanes(frame, lane_detector.lane_motor, lane_detector.lane_car)
    return frame

def main():
    parser = argparse.ArgumentParser(description="Lane violation detection (video or single image).")
    parser.add_argument("--video", type=str, default=None, help="Path to input video.")
    parser.add_argument("--image", type=str, default=None, help="Path to input image.")
    parser.add_argument("--save", type=str, default=None, help="Optional path to save output image (image mode).")
    parser.add_argument("--model", type=str, default=MODEL_PATH, help="YOLO model path/name (e.g. yolov8s.pt).")
    args = parser.parse_args()

    # Init modules
    detector = Detector(args.model)
    tracker = Tracker()
    lane_detector = LaneDetector()
    violation_detector = ViolationDetector()

    if args.image:
        frame = cv2.imread(args.image)
        if frame is None:
            raise FileNotFoundError(f"Could not read image: {args.image}")

        lane_detector.build_lanes(frame)
        out = process_frame(frame, detector, tracker, lane_detector, violation_detector)
        cv2.imshow("Lane Violation Detection", out)

        if args.save:
            cv2.imwrite(args.save, out)

        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return

    video_path = args.video or VIDEO_PATH
    cap = cv2.VideoCapture(video_path)
    lanes_built = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if not lanes_built:
            lane_detector.build_lanes(frame)
            lanes_built = True

        out = process_frame(frame, detector, tracker, lane_detector, violation_detector)
        cv2.imshow("Lane Violation Detection", out)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()