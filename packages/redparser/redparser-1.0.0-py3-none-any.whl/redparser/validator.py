import ipaddress
import re

def validate_first(input):
    try:
        i = int(input)
    except Exception as e:
        return False

    if int(i) <= 0:
        return False
    return True

def validate_last(input):
    try:
        i = int(input)
    except Exception as e:
        return False

    if int(i) <= 0:
        return False
    return True

def validate_timestamp(input):
    if input != -1:
        # Regex to check valid time in 24-hour format.
        pattern = rb'(?:[01]\d|2[0123]):(?:[012345]\d):(?:[012345]\d)'

        # Compile the ReGex
        p = re.compile(pattern)
        m = re.search(p, input)
        # matched the ReGex otherwise False
        if m is None:
            raise ValueError("Input timestamp as HH:MM:SS")
    return True


def validate_ipv4(input):
    if input != -1:
        try:
            ipaddress.IPv4Address(input)
        except Exception as e:
            return False
    return True

def validate_ipv6(input):
    if input != -1:
        try:
            ipaddress.IPv6Address(input)
        except Exception as e:
            return False
    return True