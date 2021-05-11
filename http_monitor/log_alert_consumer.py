from collections import deque
from datetime import datetime
from time import time
import threading


class LogAlertConsumer(threading.Thread):
    """A class used to process the timestamps queue to check if
    there should be an alert or system has recovered

    Attributes:
        timestamps_queue (deque): timestamps to process as they are produced
        alert_queue (deque): Local queue to move from producer queue
        time_window (int): Used to check if should alert / recover within time
        threshold (int): Threshold for hits/sec to check
        timesstamps_queue (deque): Deque with timestamps coming from the reader
        alerted (boolean): Flag to handle flipping between alert and recover
        thread_terminated (boolean): Flag to kill thread
        alert_data (dict): Hashmap of data that will be used for displaying
    """

    def __init__(self, time_window, threshold, timestamps_queue):
        """
        Args:
            time_window (int): Window of time in seconds to check hits/sec for
                any alert messaging
            threshold (int): Threshold for hits/sec to check
            timesstamps_queue (deque): Deque with timestamps from the reader
        """
        threading.Thread.__init__(self)
        self.timestamps_queue = timestamps_queue
        self.alert_queue = deque()
        self.time_window = time_window
        self.threshold = threshold
        self.alerted = False
        self.thread_terminated = False
        self.alert_data = {'alert_count': 0}

    def run(self):
        """
        Starts the thread process
        """
        start_real_time = time()

        while not self.thread_terminated:
            while self.timestamps_queue:
                timestamp = self.timestamps_queue.popleft()
                self.alert_queue.append(timestamp)

                if (time() - start_real_time) >= self.time_window:
                    self.__should_alert_or_recover(timestamp)

    def updated_alert_data(self):
        """
        Returns most up to date alert data for displaying
            purposes

        Returns:
            dict: Dict of data that will be used for displaying
        """
        return self.alert_data

    def __remove_out_of_window_timestamps(self, timestamp):
        """
        Removes any time stamps in the alert queue that are
        no longer in the window
        """
        while self.alert_queue and \
                (timestamp - self.time_window) > self.alert_queue[0]:
            self.alert_queue.popleft()

    def __has_breached_threshold(self, timestamp):
        """
        Approximate average of number of hits / second by taking the
        size of the local queue and divided it by the time window size
        """
        self.__remove_out_of_window_timestamps(timestamp)
        return (len(self.alert_queue) / self.time_window) > self.threshold

    def __should_alert_or_recover(self, timestamp):
        """
        Checks to see which state the alert service is currently in

        Ideally this is a private method but used in testing
        """
        current_state = self.__has_breached_threshold(timestamp)
        if not self.alerted and current_state:
            self.alerted = True
            self.__alert_message(timestamp)
        elif self.alerted and not current_state:
            self.alerted = False
            self.__recovered_message(timestamp)

    def __alert_message(self, timestamp):
        """
        Create alert message using timestamp from log
        """
        self.alert_data['alert_count'] += 1
        date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        self.alert_data['type'] = 'alert'
        self.alert_data['msg_line1'] = f'High traffic generated an alert:'
        self.alert_data['msg_line2'] = (
            f'hits = {len(self.alert_queue)}, triggered at {date}'
        )

    def __recovered_message(self, timestamp):
        """
        Create recovered message using timestamp from log
        """
        date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        self.alert_data['type'] = 'recovered'
        self.alert_data['msg_line1'] = (
            f'Traffic normalized - hits = {len(self.alert_queue)}'
        )
        self.alert_data['msg_line2'] = f'recovered at {date}'
