import argparse
import os
from datetime import datetime

import cv2

from config import MODEL_PATH, OUTPUT_DIR, VIDEO_PATH
from detection.detector import Detector
from lane.lane_detector import LaneDetector
from tracking.tracker import Tracker
from utils.draw import draw_box, draw_center, draw_lanes
from utils.results import ResultsHandler
from violation.violation_detector import ViolationDetector


def process_frame(frame, detector, tracker, lane_detector, violation_detector, results, frame_idx=0):
    detections = detector.detect(frame)
    frame_violations = 0

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
            results.record(frame_idx, obj_id, label, lane, x1, y1, x2, y2)
            frame_violations += 1

        draw_box(frame, x1, y1, x2, y2, text, color)
        draw_center(frame, cx, cy)

    draw_lanes(frame, lane_detector.lane_motor, lane_detector.lane_car)
    results.draw_summary(frame, frame_violations)
    return frame


def make_output_dir(base_dir):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(base_dir, timestamp)
    os.makedirs(path, exist_ok=True)
    return path


def main():
    parser = argparse.ArgumentParser(description="Lane violation detection (video or single image).")
    parser.add_argument("--video", type=str, default=None, help="Path to input video.")
    parser.add_argument("--image", type=str, default=None, help="Path to input image.")
    parser.add_argument("--model", type=str, default=MODEL_PATH, help="YOLO model path/name (e.g. yolov8s.pt).")
    parser.add_argument(
        "--output-dir", type=str, default=None,
        help=f"Save image, video, and logs to a timestamped subfolder (default base: {OUTPUT_DIR}).",
    )
    parser.add_argument("--save", type=str, default=None, help="Save annotated image to this path.")
    parser.add_argument("--save-video", type=str, default=None, help="Save annotated video to this path.")
    parser.add_argument("--no-display", action="store_true", help="Disable on-screen preview.")
    parser.add_argument("--no-log", action="store_true", help="Do not save violation JSON/CSV logs.")
    args = parser.parse_args()

    output_dir = None
    if args.output_dir is not None:
        base = args.output_dir if args.output_dir else OUTPUT_DIR
        output_dir = make_output_dir(base)
        print(f"Results will be saved to: {output_dir}")

    results = ResultsHandler(output_dir=output_dir)

    detector = Detector(args.model)
    tracker = Tracker()
    lane_detector = LaneDetector()
    violation_detector = ViolationDetector()

    window_name = "Lane Violation Detection"

    if args.image:
        frame = cv2.imread(args.image)
        if frame is None:
            raise FileNotFoundError(f"Could not read image: {args.image}")

        lane_detector.build_lanes(frame)
        out = process_frame(frame, detector, tracker, lane_detector, violation_detector, results)
        results.total_frames = 1

        if not args.no_display:
            cv2.imshow(window_name, out)

        save_path = args.save or (os.path.join(output_dir, "result.jpg") if output_dir else None)
        if save_path:
            results.save_image(out, save_path)
            print(f"Saved image: {save_path}")

        if output_dir and not args.no_log:
            results.save_report()
            results.save_csv()
            print(f"Saved logs: {output_dir}")

        if not args.no_display:
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        return

    video_path = args.video or VIDEO_PATH
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Could not open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    lanes_built = False
    frame_idx = 0

    video_out_path = args.save_video or (os.path.join(output_dir, "result.mp4") if output_dir else None)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if not lanes_built:
            lane_detector.build_lanes(frame)
            lanes_built = True
            if video_out_path:
                results.init_video_writer(video_out_path, frame.shape, fps)

        out = process_frame(
            frame, detector, tracker, lane_detector, violation_detector, results, frame_idx,
        )
        results.write_frame(out)
        results.total_frames += 1
        frame_idx += 1

        if not args.no_display:
            cv2.imshow(window_name, out)
            if cv2.waitKey(1) & 0xFF == 27:
                break

    cap.release()
    results.release_video()

    if video_out_path and os.path.exists(video_out_path):
        print(f"Saved video: {video_out_path}")

    if output_dir and not args.no_log:
        results.save_report()
        results.save_csv()
        print(f"Total violations: {len(results.violations)}")
        print(f"Saved logs: {output_dir}")

    if not args.no_display:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
