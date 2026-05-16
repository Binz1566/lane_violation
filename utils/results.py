import csv
import json
import os
from datetime import datetime

import cv2


class ResultsHandler:
    def __init__(self, output_dir=None):
        self.violations = []
        self.total_frames = 0
        self.output_dir = output_dir
        self._video_writer = None

        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

    def record(self, frame_idx, obj_id, vehicle_type, lane, x1, y1, x2, y2):
        entry = {
            "frame": frame_idx,
            "object_id": obj_id,
            "vehicle_type": vehicle_type,
            "lane": lane,
            "bbox": [x1, y1, x2, y2],
        }
        self.violations.append(entry)
        return entry

    def draw_summary(self, frame, frame_violations=0):
        total = len(self.violations)
        lines = [
            f"Frame violations: {frame_violations}",
            f"Total violations: {total}",
        ]
        y = 30
        for line in lines:
            cv2.putText(
                frame, line, (10, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2,
            )
            y += 30

    def init_video_writer(self, path, frame_shape, fps=25):
        h, w = frame_shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self._video_writer = cv2.VideoWriter(path, fourcc, fps, (w, h))

    def write_frame(self, frame):
        if self._video_writer is not None:
            self._video_writer.write(frame)

    def release_video(self):
        if self._video_writer is not None:
            self._video_writer.release()
            self._video_writer = None

    def save_image(self, frame, path):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        cv2.imwrite(path, frame)

    def save_report(self, path=None):
        if path is None:
            if not self.output_dir:
                return None
            path = os.path.join(self.output_dir, "violations.json")

        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        report = {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "total_frames": self.total_frames,
            "total_violations": len(self.violations),
            "violations": self.violations,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        return path

    def save_csv(self, path=None):
        if path is None:
            if not self.output_dir:
                return None
            path = os.path.join(self.output_dir, "violations.csv")

        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["frame", "object_id", "vehicle_type", "lane", "x1", "y1", "x2", "y2"],
            )
            writer.writeheader()
            for v in self.violations:
                x1, y1, x2, y2 = v["bbox"]
                writer.writerow({
                    "frame": v["frame"],
                    "object_id": v["object_id"],
                    "vehicle_type": v["vehicle_type"],
                    "lane": v["lane"],
                    "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                })
        return path
