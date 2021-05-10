import os
import re
import threading
import time


class LogReader(threading.Thread):
    def __init__(self, log_file_path, alert_queue, stats_queue):
        threading.Thread.__init__(self)
        self.log_file_path = log_file_path
        self.alert_queue = alert_queue
        self.stats_queue = stats_queue
        self.thread_terminated = False

    def run(self):
        try:
            log_file = open(self.log_file_path, "r")
        except IOError:
            raise "Unable to open log file"

        log_lines = self.tail_file(log_file)
        for log_line in log_lines:
            parsed_log_line = self.parse_log_line(log_line)
            # Only add if the parsed line has been parsed correctly
            if parsed_log_line:
                self.alert_queue.append(parsed_log_line['time'])
                self.stats_queue.append(parsed_log_line)

    # Tailing file implementation is from a presentation
    # discussing different tools leveraging Python generators
    # https://github.com/dabeaz/generators/
    def tail_file(self, log_file):
        log_file.seek(0, os.SEEK_END)
        while not self.thread_terminated:
            line = log_file.readline()
            if not line:
                time.sleep(0.1)
                continue
            yield line

    def parse_log_line(self, log_line):
        # Regex adopted from...
        # https://www.oreilly.com/library/view/regular-expressions-cookbook/9781449327453/ch07s12.html
        regex = re.compile(
            r'^(?P<client>\S+),(?P<skip>\S+),(?P<userid>\S+),(?P<time>.+),'
            r'"(?P<method>[A-Z]+) (?P<section>[^ "]+)? HTTP/[0-9.]+",'
            r'(?P<status>[0-9]{3}),(?P<size>[0-9]+|-)'
        )

        matched = re.match(regex, log_line)
        if not matched:
            return None

        matched_dict = matched.groupdict()

        # In case there any log lines with malformed lines, return none
        try:
            matched_dict['time'] = int(matched['time'])
            matched_dict['size'] = int(matched['size'])
            matched_dict['section'] = matched_dict['section'].split('/')[1]
        except (ValueError, IndexError):
            return None

        return matched_dict
