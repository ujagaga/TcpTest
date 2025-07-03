#!/usr/bin/env python3

import socket

# Target host and port
HOST = 'ujagaga.tplinkdns.com'
PORT = 4060

# The message to send
message = 'Hello from Python TCP client!'

# Create a TCP socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print(f'Connecting to {HOST}:{PORT}...')
    s.connect((HOST, PORT))
    print('Connected. Sending message...')
    s.sendall(message.encode('utf-8'))
    print('Message sent. Closing connection.')
