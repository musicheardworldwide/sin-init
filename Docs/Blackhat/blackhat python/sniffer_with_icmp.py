#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Packet Sniffer
Author: Your Name
Date: YYYY-MM-DD
"""

import socket
import os
import struct
from ctypes import *
import logging
import argparse

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global settings
host = ""

class IP(Structure):
    _fields_ = [
        ("ihl", c_ubyte, 4),
        ("version", c_ubyte, 4),
        ("tos", c_ubyte),
        ("len", c_ushort),
        ("id", c_ushort),
        ("offset", c_ushort),
        ("ttl", c_ubyte),
        ("protocol_num", c_ubyte),
        ("sum", c_ushort),
        ("src", c_uint32),
        ("dst", c_uint32),
    ]

    def __new__(self, socket_buffer=None):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):
        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}
        self.src_address = socket.inet_ntoa(struct.pack("@I", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("@I", self.dst))
        self.protocol = self.protocol_map.get(self.protocol_num, str(self.protocol_num))

def start_sniffing():
    """Start sniffing packets and process them."""
    protocol = socket.IPPROTO_IP if os.name == "nt" else socket.IPPROTO_ICMP
    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, protocol)
    sniffer.bind((host, 0))
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    try:
        while True:
            raw_buffer = sniffer.recvfrom(65565)<source_id data="0" title="scanner.py" />
            ip_header = IP(raw_buffer[:20])
            logging.info("Protocol %s %s -> %s", ip_header.protocol, ip_header.src_address, ip_header.dst_address)

            if ip_header.protocol == "ICMP":
                offset = ip_header.ihl * 4
                buf = raw_buffer[offset:offset + sizeof(ICMP)]
                icmp_header = ICMP(buf)
                logging.info("ICMP -> Type: %d Code: %d", icmp_header.type, icmp_header.code)
    except KeyboardInterrupt:
        logging.info("Exiting...")
        if os.name == "nt":
            sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
    except Exception as e:
        logging.error("Error occurred while sniffing: %s", str(e))

def main():
    global host

    # Command-line argument parsing
    parser = argparse.ArgumentParser(description='Packet Sniffer')
    parser.add_argument('-H', '--host', required=True, help='Host to listen on')
    args = parser.parse_args()

    host = args.host

    # Start sniffing
    start_sniffing()

if __name__ == '__main__':
    main()