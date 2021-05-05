from datetime import datetime
import heapq


class LogAlerts:
    def __init__(self, time_window, threshold):
        self.time_window = time_window
        self.threshold = threshold
        self.min_heap = []
        self.alerted = False

    def add_timestamp(self, timestamp):
        heapq.heappush(self.min_heap, timestamp)

    def should_alert_or_recover(self, timestamp):
        current_state = self.has_breached_traffic(timestamp)
        if not self.alerted and current_state:
            self.alerted = True
            return self.alert_message(timestamp)
        elif self.alerted and not current_state:
            self.alerted = False
            return self.recovered_message(timestamp)

    def has_breached_traffic(self, timestamp):
        self.remove_out_of_window_timestamps(timestamp)
        return len(self.min_heap) / self.time_window > self.threshold

    def remove_out_of_window_timestamps(self, timestamp):
        while self.min_heap and timestamp - self.min_heap[0] >= 120:
            heapq.heappop(self.min_heap)

    def alert_message(self, timestamp):
        date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        message = (
            f'High traffic generated an alert - hits = {len(self.min_heap)}, '
            f'triggered at {date}'
        )
        return message

    def recovered_message(self, timestamp):
        date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        message = (
            f'Traffic normalized - hits = {len(self.min_heap)}, '
            f'recovered at {date}'
        )
        return message
