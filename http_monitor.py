import argparse
import random
import time


def simulate(file):
    logfile = open(file, "r")
    while True:
        line = logfile.readline()
        yield line
        time.sleep((random.randrange(50, 100)/100))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="HTTP Monitor")
    parser.version = '1.0'

    parser.add_argument('FILE_PATH', type=str, help="Path to log file")
    parser.add_argument('--threshold', action='store', type=int,
                        help='Set the threshold for number of requests per'
                        'second that after 2 minutes should trigger an alert')
    parser.add_argument('--simulate', action='store_true',
                        help='Simulate file passed in that will be log between'
                        '0.5 and 1 seconds')
    parser.add_argument('--version', action='version')

    args = parser.parse_args()
    log_lines = simulate(args.FILE_PATH)

    if args.simulate:
        for line in log_lines:
            print(line, end='')
