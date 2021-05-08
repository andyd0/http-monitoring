from datetime import datetime
import threading


class LogAlertConsumer(threading.Thread):
    def __init__(self, time_window, threshold, alert_queue):
        self.alert_queue = alert_queue
        self.time_window = time_window
        self.threshold = threshold
        self.window_start = None
        self.hashed = {}
        self.total_count = 0
        self.alerted = False
        self.thread_terminated = False
        self.message = ""

    def run(self):
        while not self.thread_terminated:
            while self.alert_queue:
                timestamp = self.alert_queue.get()
                self.add_timestamp(timestamp)

                # Since the start time may not be the first line
                if not self.window_start or self.window_start > timestamp:
                    self.window_start = timestamp

                # Timestamps may skip a second so can't be exact
                if (timestamp - self.window_start) >= self.time_window:
                    self.remove_out_of_window_timestamp()
                    self.should_alert_or_recover(timestamp)
                    self.window_start += 1

    def add_timestamp(self, timestamp):
        key = timestamp % (self.time_window + 1)
        old_timestamp, count = self.hashed.get(key, [None, None])
        if not old_timestamp:
            self.hashed[key] = [timestamp, 1]
        elif old_timestamp == timestamp:
            self.hashed[key] = [timestamp, count + 1]
        self.total_count += 1

    def remove_out_of_window_timestamp(self):
        key = self.window_start % (self.time_window + 1)
        old_timestamp, count = self.hashed[key]
        if old_timestamp == self.window_start:
            self.total_count -= count
            self.hashed[key] = [None, None]

    def has_breached_traffic(self):
        return self.total_count / self.time_window > self.threshold

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
