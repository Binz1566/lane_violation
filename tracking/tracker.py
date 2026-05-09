class Tracker:
    def __init__(self):
        self.objects = {}
        self.next_id = 0

    def get_id(self, cx, cy):
        for oid, (px, py) in self.objects.items():
            if abs(cx - px) < 50 and abs(cy - py) < 50:
                self.objects[oid] = (cx, cy)
                return oid

        self.objects[self.next_id] = (cx, cy)
        self.next_id += 1
        return self.next_id - 1