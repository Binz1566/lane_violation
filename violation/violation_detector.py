class ViolationDetector:
    def check(self, vehicle_type, lane):
        if vehicle_type in ["motorcycle", "motorbike"] and lane != "motor_lane":
            return True
        if vehicle_type in ["car", "bus", "truck"] and lane != "car_lane":
            return True
        return False