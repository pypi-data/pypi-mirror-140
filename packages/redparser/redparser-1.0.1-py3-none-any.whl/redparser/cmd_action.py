import re
import random

from .validator import *
from .mmap_parser import *
from .memory_parser import  *

def lighter(line):
    """
    prints table of formatted text format options
    """
    # fg = random.randint(30, 38)
    # just make text black
    fg = 30
    s1 = ''
    # bg = random.randint(40, 48)
    # don't want a black backgroun
    bg = random.randint(41,48)
    if bg == fg:
        if fg < 35:
            bg = bg in range(45, 48)
        else:
            bg = bg in range(40, 44)

    format = ';'.join([str(1), str(fg), str(bg)])
    s1 += '\x1b[%sm %s \x1b[0m' % (format, line)
    return s1

def highlighter_ipv4(results):
    pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    ipv4s = pattern.findall(results)
    for ip in set(ipv4s):
        results = results.replace(ip, lighter(ip))
    return results

def highlighter_ipv6(results):
    ipv6_address = re.compile(
        '(?:(?:[0-9A-Fa-f]{1,4}:){6}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|::(?:[0-9A-Fa-f]{1,4}:){5}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){4}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){3}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,2}[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){2}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,3}[0-9A-Fa-f]{1,4})?::[0-9A-Fa-f]{1,4}:(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,4}[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,5}[0-9A-Fa-f]{1,4})?::[0-9A-Fa-f]{1,4}|(?:(?:[0-9A-Fa-f]{1,4}:){,6}[0-9A-Fa-f]{1,4})?::)')

    ipv6s = ipv6_address.findall(results)
    for ip in set(ipv6s):
        results = results.replace(ip, lighter(ip))
    return results

def highlight_both(results):
    ipv6_address = re.compile(
        '(?:(?:[0-9A-Fa-f]{1,4}:){6}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|::(?:[0-9A-Fa-f]{1,4}:){5}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){4}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){3}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,2}[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){2}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,3}[0-9A-Fa-f]{1,4})?::[0-9A-Fa-f]{1,4}:(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,4}[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,5}[0-9A-Fa-f]{1,4})?::[0-9A-Fa-f]{1,4}|(?:(?:[0-9A-Fa-f]{1,4}:){,6}[0-9A-Fa-f]{1,4})?::)')

    ipv6s = ipv6_address.findall(results)
    for ip in set(ipv6s):
        results = results.replace(ip, lighter(ip))

    pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    ipv4s = pattern.findall(results)
    for ip in set(ipv4s):
        results = results.replace(ip, lighter(ip))

    return results

def cmd_action(file_object, args, mmap_possible):
    try:
        if args.first:
            if args.timestamps:
                if args.ipv4 and args.ipv6:
                    if mmap_possible:
                        print(highlight_both(first(file_object, args.first, timestamp, ipv4_ipv6_all)))
                    else:
                        print(highlight_both(memory_first(file_object, args.first, timestamp, ipv4_ipv6_all)))
                elif args.ipv4:
                    if mmap_possible:
                        print(highlighter_ipv4(first(file_object, args.first, timestamp, ipv4)))
                    else:
                        print(highlighter_ipv4(memory_first(file_object, args.first, timestamp, ipv4)))
                elif args.ipv6:
                    if mmap_possible:
                        print(highlighter_ipv6(first(file_object, args.first, timestamp, ipv6)))
                    else:
                        print(highlighter_ipv6(memory_first(file_object, args.first, timestamp, ipv6)))
                else:
                    if mmap_possible:
                        print(first(file_object, args.first, timestamp))
                    else:
                        print(memory_first(file_object, args.first, timestamp))
            elif args.ipv4 and args.ipv6:
                if mmap_possible:
                    print(highlight_both(first(file_object, args.first, ipv4_ipv6_all)))
                else:
                    print(highlight_both(memory_first(file_object, args.first, ipv4_ipv6_all)))
            elif args.ipv4:
                if mmap_possible:
                    print(highlighter_ipv4(first(file_object, args.first, ipv4)))
                else:
                    print(highlighter_ipv4(memory_first(file_object, args.first, ipv4)))
            elif args.ipv6:
                if mmap_possible:
                    print(highlighter_ipv6(first(file_object, args.first, ipv6)))
                else:
                    print(highlighter_ipv6(memory_first(file_object, args.first, ipv6)))

            else:
                if mmap_possible:
                    print(first(file_object, args.first))
                else:
                    print(memory_first(file_object, args.first))

        elif args.last:
            if args.timestamps:
                if args.ipv4 and args.ipv6:
                    if mmap_possible:
                        print(highlight_both(last(file_object, args.last, timestamp, ipv4_ipv6_all)))
                    else:
                        print(highlight_both(memory_last(file_object, args.last, timestamp, ipv4_ipv6_all)))
                elif args.ipv4:
                    if mmap_possible:
                        print(highlighter_ipv4(last(file_object, args.last, timestamp, ipv4)))
                    else:
                        print(highlighter_ipv4(memory_last(file_object, args.last, timestamp, ipv4)))
                elif args.ipv6:
                    if mmap_possible:
                        print(highlighter_ipv6(last(file_object, args.last, timestamp, ipv6)))
                    else:
                        print(highlighter_ipv6(memory_last(file_object, args.last, timestamp, ipv6)))
                else:
                    if mmap_possible:
                        print(last(file_object, args.last, timestamp))
                    else:
                        print(memory_last(file_object, args.last, timestamp))
            elif args.ipv4 and args.ipv6:
                if mmap_possible:
                    print(highlight_both(last(file_object, args.last, ipv4_ipv6_all)))
                else:
                    print(highlight_both(memory_last(file_object, args.last, ipv4_ipv6_all)))
            elif args.ipv4:
                if mmap_possible:
                    print(highlighter_ipv4(last(file_object, args.last, ipv4)))
                else:
                    print(highlighter_ipv4(memory_last(file_object, args.last, ipv4)))
            elif args.ipv6:
                if mmap_possible:
                    print(highlighter_ipv6(last(file_object, args.last, ipv6)))
                else:
                    print(highlighter_ipv6(memory_last(file_object, args.last, ipv6)))

            else:
                if mmap_possible:
                    print(last(file_object, args.last))
                else:
                    print(memory_last(file_object, args.last))

        elif args.timestamps:
            if args.ipv4 and args.ipv6:
                if mmap_possible:
                    print(first(file_object, -1, timestamp, ipv4_ipv6_all))
                else:
                    print(memory_first(file_object, -1, timestamp, ipv4_ipv6_all))
            elif args.ipv4:
                if mmap_possible:
                    print(highlighter_ipv4(first(file_object, -1, timestamp, ipv4)))
                else:
                    print(highlighter_ipv4(memory_first(file_object, -1, timestamp, ipv4)))
            elif args.ipv6:
                if mmap_possible:
                    print(highlighter_ipv6(first(file_object, -1, timestamp, ipv6)))
                else:
                    print(highlighter_ipv6(memory_first(file_object, -1, timestamp, ipv6)))
            else:
                timestamp_all(file_object)
                if mmap_possible:
                    timestamp_all(file_object)
                else:
                    memory_timestamp_all(file_object)

        elif args.ipv4:
            if args.ipv6:
                print(highlight_both(first(file_object, -1, ipv4_ipv6_all)))
                if mmap_possible:
                    print(highlight_both(first(file_object, -1, ipv4_ipv6_all)))
                else:
                    print(highlight_both(memory_first(file_object, -1, ipv4_ipv6_all)))
            else:
                if mmap_possible:
                    print(highlighter_ipv4(ipv4_all(file_object)))
                else:
                    print(highlighter_ipv4(memory_ipv4_all(file_object)))
        elif args.ipv6:
            print(highlighter_ipv6(ipv6_all(file_object)))
            if mmap_possible:
                print(highlighter_ipv6(ipv6_all(file_object)))
            else:
                print(highlighter_ipv6(memory_ipv6_all(file_object)))

        else:
            raise ValueError("Error parsing cmdline options")

    except Exception as e:
        ValueError(e)