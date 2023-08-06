#!/usr/bin/python3

import argparse
import mmap
import sys
import re
import ipaddress
from collections import namedtuple

from .cmd_action import *
from .argparser import *


def main():



    terminalargs = sys.argv[1:]

    if '-h' in terminalargs or '--help' in terminalargs:
        print(help)
        sys.exit(1)
    len_termargs = len(terminalargs)
    if len_termargs == 0:
        print(help)
        sys.exit(1)

    try:
        with open(sys.argv[-1], 'rb') as file_obj:
            mmap_possible = 1
            args = argparser(terminalargs, mmap_possible)
            cmd_action(file_obj, args, mmap_possible)
    except Exception as e:
        try:
            if not sys.stdin.isatty():
                file_obj = sys.stdin.buffer.read()
                mmap_possible = 0
                args = argparser(terminalargs, mmap_possible)
                cmd_action(file_obj, args, mmap_possible)

        except Exception as e:
            print("Error reading log file please pipe data to python file or have log file at end of command\n")
            print(help)
            sys.exit(1)

    # now the fun part



if __name__ == '__main__':

    main()