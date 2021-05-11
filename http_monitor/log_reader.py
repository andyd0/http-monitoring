import os
import re
import threading
import time


class LogReader(threading.Thread):
    """A class used to read and parse log lines. It will also populate
    queues for the consumers

    Attributes
    ----------
    log_file_path (str): Path to log file that should be tailed
    alert_queue (deque): Deque to be used by the Alert Consumer
    stats_queue (deque): Deque to be used by the Stats Consumer
    thread_terminated (boolean): Flag to kill thread
    """

    def __init__(self, log_file_path, alert_queue, stats_queue):
        """
        Args:
            log_file_path (str): Path to log file that should be tailed
            alert_queue (deque): Deque to be used by the Alert Consumer
            stats_queue (deque): Deque to be used by the Stats Consumer
        """
        threading.Thread.__init__(self)
        self.log_file_path = log_file_path
        self.alert_queue = alert_queue
        self.stats_queue = stats_queue
        self.thread_terminated = False

    def run(self):
        """
        Starts the thread process
        """
        try:
            with open(self.log_file_path, "r") as log_file:
                log_lines = self.__tail_file(log_file)
                for log_line in log_lines:
                    parsed_log_line = self.__parse_log_line(log_line)
                    # Only add if the parsed line has been parsed correctly
                    if parsed_log_line:
                        self.alert_queue.append(parsed_log_line['time'])
                        self.stats_queue.append(parsed_log_line)
        except IOError:
            raise "Unable to open log file"

    # Tailing file implementation is from a presentation
    # discussing different tools leveraging Python generators
    # https://github.com/dabeaz/generators/
    def __tail_file(self, log_file):
        """
        Tails the provided file for new log entries
        """
        log_file.seek(0, os.SEEK_END)
        while not self.thread_terminated:
            line = log_file.readline()
            if not line:
                time.sleep(0.1)
                continue
            yield line

    def __parse_log_line(self, log_line):
        """
        Parses a log line using regex to get required data points.
        """
        # Regex adopted from...
        # https://www.oreilly.com/library/view/regular-expressions-cookbook/9781449327453/ch07s12.html
        regex = re.compile(
            r'^(?P<client>\S+),(?P<skip>\S+),(?P<userid>\S+),(?P<time>.+),'
            r'"(?P<method>[A-Z]+) (?P<section>[^ "]+)? HTTP/[0-9.]+",'
            r'(?P<status>[0-9]{3}),(?P<size>[0-9]+|-)'
        )

        # In case there any log lines with malformed lines, return none.
        # Likely enough log lines that a few ones missed won't make a
        # difference
        matched = re.match(regex, log_line)
        if not matched:
            return None

        matched_dict = matched.groupdict()

        try:
            matched_dict['time'] = int(matched['time'])
            matched_dict['size'] = int(matched['size'])
            matched_dict['section'] = matched_dict['section'].split('/')[1]
        except (ValueError, IndexError):
            return None

        return matched_dict
