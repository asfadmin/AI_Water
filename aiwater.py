# !/usr/bin/env python3
"""
 Created By:   Jason Herning
 Date Started: 08-05-2020
 Last Updated: 08-05-2020
 File Name:    aiwater.py
 Description:  Main file holding all the argparse
"""

from argparse import Namespace, ArgumentParser
import sys


def hello(args: Namespace):
    x = f"hello {args.name}!" * args.count
    print(x)
    return x



def cmdline_args():
    # Make parser object
    p = ArgumentParser(description=__doc__)

    p.add_argument('name', help="your name")
    p.add_argument("count", type=int, help="number of times to list name")
    p.add_subparsers()
    p.set_defaults(func=hello)

    return p.parse_args()


if __name__ == '__main__':

    if sys.version_info < (3, 5, 0):
        sys.stderr.write("You need python 3.5 or later to run this script\n")
        sys.exit(1)


    args = cmdline_args()
    print(args)
    if hasattr(args, 'func'):
        args.func(args)
    else:
        args.print_help()

