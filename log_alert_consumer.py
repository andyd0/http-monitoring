from collections import deque
from datetime import datetime
import threading


class LogAlertConsumer(threading.Thread):
    def __init__(self, time_window, threshold, timestamps_queue):
        self.timestamps_queue = timestamps_queue
        self.alert_queue = deque()
        self.time_window = time_window
        self.threshold = threshold
        self.window_start = None
        self.alerted = False
        self.thread_terminated = False
        self.message = ""

    def run(self):
        while not self.thread_terminated:
            while self.timestamps_queue:
                timestamp = self.timestamps_queue.popleft()

                self.alert_queue.append(timestamp)
                while self.timestamps_queue and self.timestamps_queue[0] == timestamp:
                    self.alert_queue.append(self.timestamps_queue.popleft())

                # Since the start time may not be the first line
                if not self.window_start or self.window_start > timestamp:
                    self.window_start = timestamp

                # Timestamps may skip a second so can't be exact
                if (timestamp - self.window_start) >= self.time_window:
                    self.should_alert_or_recover(timestamp)
                    self.window_start += 1

    def remove_out_of_window_timestamps(self):
        while self.alert_queue and self.window_start > self.alert_queue[0]:
            self.alert_queue.popleft()

    def has_breached_traffic(self):
        self.remove_out_of_window_timestamps()
        return (len(self.alert_queue) / self.time_window) > self.threshold

    def should_alert_or_recover(self, timestamp):
        current_state = self.has_breached_traffic()
        if not self.alerted and current_state:
            self.alerted = True
            self.message = self.alert_message(timestamp)
        elif self.alerted and not current_state:
            self.alerted = False
            self.message = self.recovered_message(timestamp)

    def alert_message(self, timestamp):
        date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        message = (
            f'High traffic generated an alert - hits = {self.total_count}, '
            f'triggered at {date}'
        )
        return message

    def recovered_message(self, timestamp):
        date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        message = (
            f'Traffic normalized - hits = {len(self.total_count)}, '
            f'recovered at {date}'
        )
        return message
