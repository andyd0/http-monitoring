from collections import deque
from log_alert_consumer import LogAlertConsumer
from log_stats_consumer import LogStatsConsumer
from log_reader import LogReader
from display import Display
import argparse


# Threading implementation adopted from
# "Python thread sample with handling Ctrl-C"
# https://gist.github.com/ruedesign/5218221
def start_monitoring(input_file_path, time_window, threshold):
    alerts_queue = deque()
    stats_queue = deque()

    reader = LogReader(input_file_path, alerts_queue, stats_queue)
    alerts = LogAlertConsumer(time_window, threshold, alerts_queue)
    stats = LogStatsConsumer(threshold, stats_queue)
    display = Display(reader, stats, alerts)

    threads = [reader, display, stats, alerts]
    for t in threads:
        t.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="HTTP Log Monitor App")
    parser.version = '1.0'

    parser.add_argument('INPUT_FILE_PATH', type=str, help="Path to log file")
    parser.add_argument('--threshold', action='store', type=int, default=10,
                        help='Set the threshold for number of requests per'
                        'second that after 2 minutes should trigger an alert.'
                        'Default is 10 seconds.')
    parser.add_argument('--time_window', action='store', type=int, default=120,
                        help='Set the window of time for alert. Default is '
                        '120 seconds.')
    parser.add_argument('--version', action='version')

    args = parser.parse_args()

    start_monitoring(args.INPUT_FILE_PATH, args.time_window, args.threshold)
