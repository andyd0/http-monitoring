class LogAlerts:
    def __init__(self, threshold):
        self.threshold = threshold
        self.per_second = {}
        self.alerted = False

    def add_timestamp(self, timestamp):
        key = timestamp % self.threshold
        self.per_second[key] = self.per_second.get(key, 0) + 1

    def should_alert(self):
        total_requests = 0

        for _, count in self.per_second.items():
            total_requests += count

        return round((total_requests / count), 2) > self.threshold
