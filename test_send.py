#!/usr/bin/env python3
import socket
import sys

HOST = 'localhost'  # or your server IP
PORT = 4060

def send_tcp_message(message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(message.encode())

if __name__ == '__main__':
    send_tcp_message("Test msg")
