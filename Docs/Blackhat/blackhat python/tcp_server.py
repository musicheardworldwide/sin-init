#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced TCP Server Example
"""

import socket
import threading
import json
import ssl
import logging
import sys

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load configuration from a JSON file
def load_config(config_file):
    with open(config_file, 'r') as f:
        return json.load(f)

def handle_client(client_socket):
    try:
        request = client_socket.recv(4096)
        logging.info("[*] Received: %s", request.decode())
        
        # Send back a packet
        client_socket.send(b"ACK!")
    except Exception as e:
        logging.error("Error handling client: %s", e)
    finally:
        client_socket.close()

def server_loop(bind_ip, bind_port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((bind_ip, bind_port))
    server.listen(5)
    logging.info("[*] Listening on %s:%d", bind_ip, bind_port)

    while True:
        client_socket, addr = server.accept()
        logging.info("[*] Accepted connection from %s:%d", addr<source_id data="0" title="tcp_proxy.py" />, addr<source_id data="1" title="tcp_server.py" />)
        
        # Spin up a thread to handle the client
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 server.py [config_file.json]")
        sys.exit(1)

    config = load_config(sys.argv<source_id data="1" title="tcp_server.py" />)
    bind_ip = config['bind_ip']
    bind_port = config['bind_port']

    server_loop(bind_ip, bind_port)

if __name__ == "__main__":
    main()