from ultralytics import YOLO
from config import VEHICLE_CLASSES

class Detector:
    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def detect(self, frame):
        results = self.model(frame)[0]
        detections = []

        for box in results.boxes:
            cls_id = int(box.cls[0])
            label = self.model.names[cls_id]

            # Normalize common label variants
            if label == "motorbike":
                label = "motorcycle"

            if label not in VEHICLE_CLASSES:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            detections.append((label, x1, y1, x2, y2))

        return detections