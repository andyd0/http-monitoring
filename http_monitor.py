from collections import deque
import argparse


# Threading implementation to consider infinite run till keyboard interupt
# inspired by "Python thread sample with handling Ctrl-C"
# https://gist.github.com/ruedesign/5218221
def start_monitoring(input_file_path, threshold):
    return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="HTTP Monitor")
    parser.version = '1.0'

    parser.add_argument('INPUT_FILE_PATH', type=str, help="Path to log file")
    parser.add_argument('--threshold', action='store', type=int,
                        help='Set the threshold for number of requests per'
                        'second that after 2 minutes should trigger an alert')
    parser.add_argument('--version', action='version')

    args = parser.parse_args()

    start_monitoring(args.INPUT_FILE_PATH, args.threshold)
