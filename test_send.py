#!/usr/bin/env python3
import socket
import config


def send_tcp_message(message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((config.TCP_SERVER_URL, config.TCP_SERVER_PORT))
        s.sendall(message.encode())

if __name__ == '__main__':
    send_tcp_message("Test msg")
