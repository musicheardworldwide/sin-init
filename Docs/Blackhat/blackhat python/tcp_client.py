#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced TCP Client Example
"""

import socket
import ssl
import threading
import argparse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

def handle_response(response):
    # Parse and log the response
    headers, body = response.split(b'\r\n\r\n', 1)
    logging.info("Headers:\n%s", headers.decode())
    logging.info("Body:\n%s", body.decode())

def client_thread(target_host, target_port):
    try:
        # Create a secure socket
        context = ssl.create_default_context()
        with socket.create_connection((target_host, target_port)) as sock:
            with context.wrap_socket(sock, server_hostname=target_host) as secure_sock:
                # Send HTTP GET request
                request = f"GET / HTTP/1.1\r\nHost: {target_host}\r\n\r\n"
                secure_sock.send(request.encode())
                
                # Receive response
                response = secure_sock.recv(4096)
                handle_response(response)
    except Exception as e:
        logging.error("Error: %s", e)

def main():
    parser = argparse.ArgumentParser(description='Advanced TCP Client')
    parser.add_argument('host', type=str, help='Target host')
    parser.add_argument('port', type=int, help='Target port')
    parser.add_argument('--threads', type=int, default=5, help='Number of concurrent threads')
    
    args = parser.parse_args()
    
    threads = []
    for _ in range(args.threads):
        thread = threading.Thread(target=client_thread, args=(args.host, args.port))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()