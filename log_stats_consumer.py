from collections import Counter
from collections import deque
from time import time
import threading


class LogStatsConsumer(threading.Thread):
    """A class used to process log lines to produce stats for the display

    Attributes:
        interval (int): Update stats at every interval
        logs_queue (deque): Queue to get log lines as they are produced
        stats_queue (deque): Local queue to move logs from logs queue
        window_section_counts (Counter): Counter of section counts per interval
        window_status_counts (Counter): Counter of status counts per interval
        thread_terminated (boolean): Flag to kill thread
        stats_data (dict): Hashmap of data that will be used for displaying
    """

    def __init__(self, interval, logs_queue):
        threading.Thread.__init__(self)
        self.interval = interval
        self.logs_queue = logs_queue
        self.stats_queue = deque()
        self.window_section_counts = None
        self.window_status_counts = None
        self.thread_terminated = False
        self.stats_data = {'hits': 0, 'size': 0}

    def run(self):
        """
        Starts the thread process
        """
        section_counts, status_counts = Counter(), Counter()
        start_real_time = time()

        while not self.thread_terminated:
            while self.logs_queue:
                self.stats_queue.append(self.logs_queue.popleft())
                if (time() - start_real_time) >= self.interval:
                    start_real_time = time()
                    self.__save_stats(section_counts, status_counts)
                    section_counts, status_counts = Counter(), Counter()

    def __update_counts(self, section_counts, status_counts):
        """
        Gets log data from the local queue to update counts
        """
        while self.stats_queue:
            log_data = self.stats_queue.popleft()
            self.stats_data['hits'] += 1
            self.stats_data['size'] += log_data['size']
            section_counts[log_data['section']] += 1
            status_counts[log_data['status'][0]+"XX"] += 1

    def __save_stats(self, section_counts, status_counts):
        """
        Copies the counters into data to be used by display
        so that new ones can be created for next interval
        """
        self.__update_counts(section_counts, status_counts)
        self.window_section_counts = Counter(section_counts)
        self.window_status_counts = Counter(status_counts)

    def updated_counts(self):
        return self.window_section_counts, self.window_status_counts

    def updated_total_stats(self):
        return self.stats_data
