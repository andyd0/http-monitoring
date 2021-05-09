import argparse
import time


def simulate(input_file, output_file):
    with open(input_file, "r") as log_lines:
        with open(output_file, 'w') as log_file:
            for line in log_lines:
                log_file.write(line)
                time.sleep(0.1)


if __name__ == '__main__':
    log_lines = simulate('sample_csv.txt', 'log-file.log')
