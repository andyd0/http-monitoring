from collections import deque
from datetime import datetime
from time import time
import threading


class LogAlertConsumer(threading.Thread):
    def __init__(self, time_window, threshold, timestamps_queue):
        threading.Thread.__init__(self)
        self.timestamps_queue = timestamps_queue
        self.alert_queue = deque()
        self.time_window = time_window
        self.threshold = threshold
        self.alerted = False
        self.thread_terminated = False

        self.alert_data = {}
        self.alert_data['alert_count'] = 0

    def run(self):
        start_real_time = time()

        while not self.thread_terminated:
            while self.timestamps_queue:
                timestamp = self.timestamps_queue.popleft()
                self.alert_queue.append(timestamp)

                # A second block may be missing entirely so can't
                # be exact
                if (time() - start_real_time) >= self.time_window:
                    self.should_alert_or_recover(timestamp)

    def remove_out_of_window_timestamps(self, timestamp):
        while self.alert_queue and \
                (timestamp - self.time_window) > self.alert_queue[0]:
            self.alert_queue.popleft()

    def has_breached_traffic(self, timestamp):
        self.remove_out_of_window_timestamps(timestamp)
        return (len(self.alert_queue) / self.time_window) > self.threshold

    def should_alert_or_recover(self, timestamp):
        current_state = self.has_breached_traffic(timestamp)
        if not self.alerted and current_state:
            self.alerted = True
            self.alert_message(timestamp)
        elif self.alerted and not current_state:
            self.alerted = False
            self.recovered_message(timestamp)

    def alert_message(self, timestamp):
        self.alert_data['alert_count'] += 1
        date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        self.alert_data['msg_line1'] = f'High traffic generated an alert:'
        self.alert_data['msg_line2'] = f'hits = {len(self.alert_queue)}, triggered at {date}'

    def recovered_message(self, timestamp):
        date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        self.alert_data['msg_line1'] = f'Traffic normalized - hits = {len(self.alert_queue)}'
        self.alert_data['msg_line2'] = f'recovered at {date}'

    def updated_alert_data(self):
        return self.alert_data
