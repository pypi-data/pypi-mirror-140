import re
import ipaddress
import collections

from .mmap_parser import ipv4, ipv6


def memory_first(bytes_obj, num_lines=0, callback=None, callback2=None):
    try:
        file_length = len(bytes_obj)-1
        startpointer = 0
        endpointer = 0
        found_items = {}
        while num_lines != 0 and endpointer < file_length:
            endpointer = bytes_obj.find(b'\n', startpointer, file_length) + 1
            # have to track pointers to print logs in reverse order

            # end of file
            if endpointer == 0:
                endpointer = file_length+1

            if callback == None:
                num_lines -= 1
            else:
                # last line won't end in \n
                success = callback(bytes_obj[startpointer:endpointer], callback2)
                if success:
                    found_items[startpointer] = endpointer

                num_lines -= success
            startpointer = endpointer
        if callback == None:
            return bytes_obj[:endpointer].decode('utf-8')
        else:
            # sucks that we have to do this but le HIGHLIGHTING
            odered_items = collections.OrderedDict(sorted(found_items.items()))
            result = ""
            for k, v in odered_items.items():
                result += bytes_obj[k:v].decode('utf-8')
            return result.rstrip('\n')

    except Exception as e:
        print(e)

def memory_last(bytes_obj, num_lines=0, callback=None, callback2=None):
    try:
        file_length = len(bytes_obj) - 1
        startpointer = file_length
        endpointer = file_length
        #have to track pointers to print logs in reverse order
        found_items = {}
        # is it safe for startpointer > 0
        while num_lines != 0 and startpointer > 0:
            startpointer = bytes_obj.rfind(b'\n', 0, endpointer)

            if callback == None:
                num_lines -= 1
            else:
                # shift by one to be like first
                success = callback(bytes_obj[startpointer+1:endpointer+1], callback2)
                if success:
                    found_items[startpointer+1] = endpointer+1
                num_lines -= success

            # end of file
            # if startpointer + 1 == 0:
            #     startpointer = 0

            endpointer = startpointer
        if callback == None:
            return bytes_obj[startpointer+1:].decode('utf-8')
        else:
            # sucks that we have to do this but reversing it makes the last item we want to print be first unless we reverse again
            odered_items = collections.OrderedDict(sorted(found_items.items()))
            result = ""
            for k, v in odered_items.items():
                result += bytes_obj[k:v].decode('utf-8')
            return result.rstrip('\n')

    except Exception as e:
        print(e)

def memory_timestamp_all(bytes_obj):
    try:
        ts = re.compile(rb'.*(?:[01]\d|2[0123]):(?:[012345]\d):(?:[012345]\d[^\n]*)')

        matches = ts.findall(bytes_obj)
        print(b'\n'.join(matches).decode('utf-8'))

    except Exception as e:
        raise ValueError(e)

def memory_ipv4_all(bytes_obj):
    return memory_first(bytes_obj, -1, ipv4)

def memory_ipv6_all(bytes_obj):
    return memory_first(bytes_obj, -1, ipv6)