from collections import Counter
from collections import deque
import threading


class LogStatsConsumer(threading.Thread):
    def __init__(self, interval, logs_queue):
        self.interval = interval
        self.logs_queue = logs_queue
        self.stats_queue = deque()
        self.count_segments = Counter()
        self.status_codes = Counter()
        self.window_start = None
        self.thread_terminated = False

    def run(self):
        while not self.thread_terminated:
            while self.stats_queue:

                log_data = self.alert_queue.popleft()
                timestamp = log_data['time']

                self.stats_queue.append(log_data)

                if not self.window_start or self.window_start > timestamp:
                    self.window_start = log_data.timestamp

                if (timestamp - self.window_start) > self.interval:
                    self.reset_stats()

                self.count_segments[log_data.segment] += 1
                self.status_codes[log_data.status_code[0]+"XX"] += 1

    def reset_stats(self):
        self.count_segments = Counter()
        self.status_codes = Counter()
