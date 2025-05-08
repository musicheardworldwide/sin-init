#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced SSH Command Executor
Author: Your Name
Date: YYYY-MM-DD
"""

import paramiko
import argparse
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def ssh_command(ip, user, passwd, command):
    """Execute a command on a remote server via SSH."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(ip, username=user, password=passwd)
        ssh_session = client.get_transport().open_session()
        
        if ssh_session.active:
            ssh_session.exec_command(command)
            output = ssh_session.recv(1024).decode('utf-8')
            logging.info(f"Command output: {output}")
            return output
    except paramiko.AuthenticationException:
        logging.error("Authentication failed, please verify your credentials.")
    except paramiko.SSHException as e:
        logging.error(f"Unable to establish SSH connection: {e}")
    except Exception as e:
        logging.error(f"Error occurred: {e}")
    finally:
        client.close()

def main():
    parser = argparse.ArgumentParser(description='Execute a command on a remote server via SSH.')
    parser.add_argument('-i', '--ip', required=True, help='IP address of the remote server')
    parser.add_argument('-u', '--user', required=True, help='Username for SSH login')
    parser.add_argument('-p', '--password', required=True, help='Password for SSH login')
    parser.add_argument('-c', '--command', required=True, help='Command to execute on the remote server')
    
    args = parser.parse_args()
    
    ssh_command(args.ip, args.user, args.password, args.command)

if __name__ == '__main__':
    main()