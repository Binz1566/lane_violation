# config.py

# Some YOLO models may use "motorbike" instead of "motorcycle"
VEHICLE_CLASSES = ["car", "motorcycle", "motorbike", "bus", "truck"]

# Lane polygons
LANE_MOTOR = [[0, 300], [640, 300], [640, 480], [0, 480]]
LANE_CAR = [[0, 0], [640, 0], [640, 300], [0, 300]]

VIDEO_PATH = "traffic.mp4"
MODEL_PATH = "yolov8s.pt"