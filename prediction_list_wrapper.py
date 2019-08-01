import argparse
import subprocess
from water_mark.etl_water_mark import detect_windows_OS


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-weight',
        help='Path to h5 weight file'
    )
    parser.add_argument(
        '-input_list',
        help="""Path to txt file cointaining paths to dirs (1/line)
             containing vh vv file pairs
             """
    )
    args = parser.parse_args()
    ins = args.input_list
    with open(ins, 'r') as txt_file:
        path = txt_file.readline().strip()
        while path:
            python = 'python'
            if detect_windows_OS():
                python = 'python3'
            subprocess.call(
                f"{python} main.py {args.weight} {path}",
                shell=True
            )
            path = txt_file.readline().strip()


if __name__ == '__main__':
    main()
