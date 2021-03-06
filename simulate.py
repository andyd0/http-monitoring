from random import random
import argparse
import time


def simulate(input_file, output_file):
    """Starts up all of the services via threads

    Args:
        input_file_path (str): Path of file that has log data
        output_file (int): Path of file that will have logs written to
    """
    try:
        with open(input_file, "r") as log_lines:
            with open(output_file, 'w', buffering=1) as log_file:
                for log_line in log_lines:
                    if log_line:
                        log_file.write(log_line)
                    time.sleep(random())
    except IOError:
        raise "Unable to open log files"
    except KeyboardInterrupt:
        print("\nSimulation interrupted")
        with open(output_file, 'w') as log_file:
            log_file.truncate(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Simulate logging")
    parser.version = '1.0'

    parser.add_argument('DATA_FILE_PATH', type=str, help="path to data file")
    parser.add_argument('LOG_FILE', type=str, help="path to log file")

    args = parser.parse_args()

    simulate(args.DATA_FILE_PATH, args.LOG_FILE)
