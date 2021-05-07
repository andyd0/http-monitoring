from collections import Counter


class LogStatsConsumer:
    def __init__(self, interval=10):
        self.interval = interval
        self.count_segments = Counter()
        self.status_codes = Counter()

    def reset_stats(self):
        self.count_segments = Counter()
