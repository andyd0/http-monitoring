from random import random
import time


def simulate(input_file, output_file):
    with open(input_file, "r") as log_lines:
        with open(output_file, 'w', buffering=1) as log_file:
            for log_line in log_lines:
                if log_line:
                    log_file.write(log_line)
                time.sleep(random())


if __name__ == '__main__':
    log_lines = simulate('sample_csv.txt', 'log-file.log')
