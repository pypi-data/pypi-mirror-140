## Redparser

Redparser is a simple Python program that can parse a log based on command line arguments. 

## Usage

Run `util.py` as a Python script, passing the log file as the last argument to utilize
the mmap library for fast searches or push the log file to memory for the util to read log file from stdin.

Example:

```python
./util.py --last 10 --timestamps --ipv4 --ipv6 example.log
```
Outputs:
![Alt Text](example.gif)


The complete usage can be seen by using the -h flag.
```
usage: ./util.py [OPTION]... [FILE]
usage: cat [FILE] | ./util.py [OPTION]
usage: redparser [OPTION]... [FILE]
usage: cat [FILE] | redparser[OPTION]

Parse logs of various kinds

optional arguments:
  -h, --help            show this help message and exit
  -f, --first NUM       Print first NUM lines
  -l, --last NUM        Print last NUM lines
  -t, --timestamps      Print lines that contain a timestamp in HH:MM:SS format
  -i, --ipv4 IP         Print lines that contain an IPv4 address, matching IPs (Optional) highlighted
  -I, --ipv6 IP         Print lines that contain an IPv6 address, matching IPs (Optional) highlighted

```

## Install with pip
```
pip install redparser
```


## TODO

- [ ] More readable highlighting of ip address
- [ ] Refactor argparser to be more readable and use better data structures
- [ ] More testing needs to be added
- [ ] Should be able to check ip address from cmdline matches a line (easy fix)