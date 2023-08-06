import mmap
import re
import ipaddress
import collections

def first(file_obj, num_lines=0, callback=None, callback2=None):
    try:
        with mmap.mmap(file_obj.fileno(), length=0, access=mmap.ACCESS_READ) as mmap_obj:
            file_length = len(mmap_obj)-1
            startpointer = 0
            endpointer = 0
            found_items = {}
            while num_lines != 0 and endpointer < file_length:
                endpointer = mmap_obj.find(b'\n', startpointer, file_length) + 1
                # have to track pointers to print logs in reverse order

                # end of file
                if endpointer == 0:
                    endpointer = file_length+1

                if callback == None:
                    num_lines -= 1
                else:
                    # last line won't end in \n
                    success = callback(mmap_obj[startpointer:endpointer], callback2)
                    if success:
                        found_items[startpointer] = endpointer

                        # print(mmap_obj[startpointer:endpointer].decode('utf-8').rstrip('\n'))
                    num_lines -= success
                startpointer = endpointer
            if callback == None:
                return mmap_obj[:endpointer].decode('utf-8')
            else:
                # sucks that we have to do this but le HIGHLIGHTING
                odered_items = collections.OrderedDict(sorted(found_items.items()))
                result = ""
                for k, v in odered_items.items():
                    result += mmap_obj[k:v].decode('utf-8')
                return result.rstrip('\n')

    except Exception as e:
        print(e)

def last(file_obj, num_lines=0, callback=None, callback2=None):
    try:
        with mmap.mmap(file_obj.fileno(), length=0, access=mmap.ACCESS_READ) as mmap_obj:
            file_length = len(mmap_obj) - 1
            startpointer = file_length
            endpointer = file_length
            #have to track pointers to print logs in reverse order
            found_items = {}
            # is it safe for startpointer > 0
            while num_lines != 0 and startpointer > 0:
                startpointer = mmap_obj.rfind(b'\n', 0, endpointer)

                if callback == None:
                    num_lines -= 1
                else:
                    # shift by one to be like first
                    success = callback(mmap_obj[startpointer+1:endpointer+1], callback2)
                    if success:
                        found_items[startpointer+1] = endpointer+1
                    num_lines -= success

                # end of file
                # if startpointer + 1 == 0:
                #     startpointer = 0

                endpointer = startpointer
            if callback == None:
                return mmap_obj[startpointer+1:].decode('utf-8')
            else:
                # sucks that we have to do this but reversing it makes the last item we want to print be first unless we reverse again
                odered_items = collections.OrderedDict(sorted(found_items.items()))
                result = ""
                for k, v in odered_items.items():
                    result += mmap_obj[k:v].decode('utf-8')
                return result.rstrip('\n')

    except Exception as e:
        print(e)

def timestamp(line, callback=None):
    if line:
        pattern = re.compile(rb'(?:[01]\d|2[0123]):(?:[012345]\d):(?:[012345]\d)')

        if len(pattern.findall(line)):

            if callback == None:
                # found timestamp
                return 1
            else:
                return callback(line)

    # timestamp not found
    return 0

def ipv4(line, callback=None):

    if line:
        pattern = re.compile(rb'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
        ips = pattern.findall(line)

        if len(ips):
            for ip in ips:
                try:
                    ipaddress.IPv4Address(ip.decode('utf-8'))

                    # found ipv4
                    return 1
                except Exception as e:
                    pass

    # ipv4 not found
    return 0

def ipv6(line, callback=None):

    if line:
        pattern = rb'^.*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?'

        if re.match(pattern, line):

            # found ipv6
            return 1

    # ipv6 not found
    return 0


def timestamp_all(file_obj):
    try:
        ts = re.compile(rb'.*(?:[01]\d|2[0123]):(?:[012345]\d):(?:[012345]\d[^\n]*)')

        with mmap.mmap(file_obj.fileno(), length=0, access=mmap.ACCESS_READ) as mmap_obj:
            # prepend \n to begining and search for \n timestamp \n, concat together and print
            matches = ts.findall(mmap_obj)
            print(b'\n'.join(matches).decode('utf-8'))

    except Exception as e:
        raise ValueError(e)

def ipv4_all(file_obj):
    return first(file_obj, -1, ipv4)

    # ip_pattern = re.compile(rb'(.*\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}[^\n]*)')
    #
    # try:
    #     with mmap.mmap(file_obj.fileno(), length=0, access=mmap.ACCESS_READ) as mmap_obj:
    #         # prepend \n to begining and search for \n timestamp \n, concat together and print
    #         matches = ip_pattern.findall(mmap_obj)
    #         iter = 0
    #         while iter < len(matches):
    #             valid_pattern = re.compile(rb'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    #             ips = valid_pattern.findall(matches[iter])
    #             for ip in ips:
    #                 try:
    #                     ipaddress.IPv4Address(ip.decode('utf-8'))
    #                     print(matches[iter].decode('utf-8'))
    #                     iter += 1
    #                     break
    #                 except Exception as e:
    #                     print(e)
    #             iter += 1
    # except Exception as e:
    #     print(e)

def ipv6_all(file_obj):
    # use ipv6 callback for every line in file, by using -1 the first loop will run until the end
    return first(file_obj, -1, ipv6)

def ipv4_ipv6_all(line, callback=None):
    if line:
        ipv4_pattern = re.compile(rb'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
        ipv6_pattern = rb'^.*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?'

        ipv4_ips = ipv4_pattern.findall(line)

        if len(ipv4_ips):
            for ip in ipv4_ips:
                try:
                    ipaddress.IPv4Address(ip.decode('utf-8'))

                    # found ipv4
                    return 1
                except Exception as e:
                    pass


        if re.match(ipv6_pattern, line):

            # found ipv6
            return 1

    # ipv6 not found
    # ipv4 not found
    return 0