import cv2
import numpy as np

class LaneDetector:
    def __init__(self):
        pass

    def build_lanes(self, frame):
        h, w = frame.shape[:2]

        # Tune these ratios to adjust lane size/position
        y_top = int(0.25 * h)   # smaller => lanes go higher (taller)
        y_bottom = int(1.00 * h)

        # Shared boundary between lanes (slanted).
        # - car_lane: "upright" trapezoid (bottom wider than top)
        # - motor_lane: "inverted" trapezoid (top wider than bottom)
        x_split_top = int(0.60 * w)
        x_split_bottom = int(0.70 * w)
        x_split_top = max(1, min(w - 2, x_split_top))
        x_split_bottom = max(1, min(w - 2, x_split_bottom))

        # Car lane (upright trapezoid): left side, wider at bottom
        self.lane_car = np.array([
            (0, y_top),
            (x_split_top, y_top),
            (x_split_bottom, y_bottom),
            (0, y_bottom),
        ], np.int32)

        # Motor lane (inverted trapezoid): right side, wider at top
        self.lane_motor = np.array([
            (x_split_top, y_top),
            (w - 1, y_top),
            (w - 1, y_bottom),
            (x_split_bottom, y_bottom),
        ], np.int32)

    def get_lane(self, cx, cy):
        if cv2.pointPolygonTest(self.lane_motor, (cx, cy), False) >= 0:
            return "motor_lane"
        elif cv2.pointPolygonTest(self.lane_car, (cx, cy), False) >= 0:
            return "car_lane"
        return "unknown"