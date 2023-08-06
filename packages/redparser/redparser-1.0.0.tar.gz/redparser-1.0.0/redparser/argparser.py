import sys
import re
import ipaddress
from collections import namedtuple

from .validator import *

help = '''
usage: ./util.py [OPTION]... [FILE]
usage: cat [FILE] | ./util.py [OPTION]
usage: mmap-logparser [OPTION]... [FILE]
usage: cat [FILE] | mmap-logparser[OPTION]

Parse logs of various kinds

optional arguments:
  -h, --help            show this help message and exit
  -f, --first NUM       Print first NUM lines
  -l, --last NUM        Print last NUM lines
  -t, --timestamps      Print lines that contain a timestamp in HH:MM:SS format
  -i, --ipv4 IP         Print lines that contain an IPv4 address, matching IPs (Optional) highlighted
  -I, --ipv6 IP         Print lines that contain an IPv6 address, matching IPs (Optional) highlighted

'''

def argparser(terminalargs, mmap_possible):
    # ugggh wish i could use argparser for this
    # hacky way

    args = {}

    def argcheck(key):
        if key in args.keys():
            print("Please only enter command once\n")
            print(help)
            sys.exit(1)



    len_termargs = len(terminalargs)
    if len_termargs == 0:
        print(help)
        sys.exit(1)



    if mmap_possible:
        len_termargs -= 1
        terminalargs = terminalargs[:len_termargs]

    if len_termargs == 0:
        print("Please input commands\n")
        print(help)
        sys.exit(1)
    else:
        i = 0
        while i < len_termargs:
            if terminalargs[i] == '--first' or terminalargs[i] == '-f':
                argcheck(terminalargs[i])
                if i +1 >= len_termargs or not validate_first(terminalargs[i+1]):
                    print("Input a positive number for the --first command\n")
                    print(help)
                    sys.exit(1)
                args['first'] = int(terminalargs[i+1])
                i += 2
            elif terminalargs[i] == '--last' or terminalargs[i] == '-l':
                argcheck(terminalargs[i])
                if i +1 > len_termargs or not validate_last(terminalargs[i+1]):
                    print("Input a positive number for the --last command\n")
                    print(help)
                    sys.exit(1)
                args['last'] = int(terminalargs[i+1])
                i += 2
            elif terminalargs[i] == '--timestamps' or terminalargs[i] == '-t':
                argcheck(terminalargs[i] )
                args['timestamps'] = "-1"
                i+=1

            elif terminalargs[i] == '--ipv4' or terminalargs[i] == '-i':
                argcheck(terminalargs[i] )
                invalids = ['--first', '-f','--last', 'l', '--timestamps', '-t', '-i', '--ipv4', '-I', '--ipv6']
                if i +1 < len_termargs and (terminalargs[i+1] not in invalids):
                    if not validate_ipv4(terminalargs[i+1]):
                        print("Input a valid ipv4 address for the --ipv4 command\n")
                        print(help)
                        sys.exit(1)
                    args['ipv4'] = terminalargs[i+1]
                    i += 2

                else:
                    args['ipv4'] = "-1"
                    i += 1

            elif terminalargs[i] == '--ipv6' or terminalargs[i] == '-I':
                argcheck(terminalargs[i] )
                invalids = ['--first', '-f','--last', 'l', '--timestamps', '-t', '-i', '--ipv4', '-I', '--ipv6']
                if i +1 < len_termargs and (terminalargs[i+1] not in invalids):
                    if not validate_ipv6(terminalargs[i+1]):
                        print("Input a valid ipv6 address for the --ipv6 command\n")
                        print(help)
                        sys.exit(1)
                    args['ipv6'] = terminalargs[i+1]
                    i += 2
                else:
                    args['ipv6'] = "-1"
                    i += 1

            else:
                print("You inputted an unknown commands\n")
                print(help)
                sys.exit(1)

    # now the fun part
    # later refactor to only have arg be object at beginning
    # uggh this sucks
    try:
        val = args['first']
    except KeyError:
        args['first'] = None

    try:
        val = args['last']
    except KeyError:
        args['last'] = None

    try:
        val = args['timestamps']
    except KeyError:
        args['timestamps'] = None

    try:
        val = args['ipv4']
    except KeyError:
        args['ipv4'] = None

    try:
        val = args['ipv6']
    except KeyError:
        args['ipv6'] = None
    args = namedtuple("args", args.keys())(*args.values())

    return args