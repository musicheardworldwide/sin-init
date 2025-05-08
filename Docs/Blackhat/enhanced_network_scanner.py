#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Network Scanner
Author: Your Name
Date: YYYY-MM-DD
"""

import socket
import threading
import time
import os
import struct
from netaddr import IPNetwork, IPAddress
from ctypes import *
import logging
import argparse

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global settings
host = ""
subnet = ""
magic_message = "PYTHONRULES!"

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

class ICMP(Structure):
    _fields_ = [
        ("type", c_ubyte),
        ("code", c_ubyte),
        ("checksum", c_ushort),
        ("unused", c_ushort),
        ("next_hop_mtu", c_ushort),
    ]

    def __new__(self, socket_buffer):
        return self.from_buffer_copy(socket_buffer)

def udp_sender(subnet, magic_message):
    """Send UDP packets to the specified subnet."""
    time.sleep(5)
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    for ip in IPNetwork(subnet):
        try:
            sender.sendto(magic_message.encode(), (str(ip), 65212))
        except Exception as e:
            logging.error("Error sending packet to %s: %s", ip, str(e))

def packet_listener():
    """Listen for incoming packets and process them."""
    protocol = socket.IPPROTO_IP if os.name == "nt" else socket.IPPROTO_ICMP
    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, protocol)
    sniffer.bind((host, 0))
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    try:
        while True:
            raw_buffer = sniffer.recvfrom(65565)[0]
            ip_header = IP(raw_buffer[:20])

            logging.info("Protocol %s %s -> %s", ip_header.protocol, ip_header.src_address, ip_header.dst_address)

            if ip_header.protocol == "ICMP":
                offset = ip_header.ihl * 4
                buf = raw_buffer[offset:offset + sizeof(ICMP)]
                icmp_header = ICMP(buf)

                logging.info("ICMP -> Type: %d Code: %d", icmp_header.type, icmp_header.code)

                if icmp_header.code == 3 and icmp_header.type == 3:
                    if IPAddress(ip_header.src_address) in IPNetwork(subnet):
                        if raw_buffer[len(raw_buffer) - len(magic_message):] == magic_message.encode():
                            logging.info("Host Up: %s", ip_header.src_address)
    except KeyboardInterrupt:
        logging.info("Exiting...")
        if os.name == "nt":
            sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)

def main():
    global host, subnet

    # Command-line argument parsing
    parser = argparse.ArgumentParser(description='Network Scanner')
    parser.add_argument('-H', '--host', required=True, help='Host to listen on')
    parser.add_argument('-s', '--subnet', required=True, help='Subnet to target (e.g., 192.168.0.0/24)')
    args = parser.parse_args()

    host = args.host
    subnet = args.subnet

    # Start the UDP sender and packet listener
    t = threading.Thread(target=udp_sender, args=(subnet, magic_message))
    t.start()
    packet_listener()

if __name__ == '__main__':
    main()