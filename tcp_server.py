#!/usr/bin/env python3

import socket
import requests
import config

HOST = '0.0.0.0'
PORT = config.TCP_SERVER_PORT
MONITOR_URL = config.MONITOR_URL

def send_to_flask(text_to_send):
    try:
        # Send message as form data, like your curl
        response = requests.post(MONITOR_URL, data={'message': text_to_send}, timeout=2)
        if response.status_code != 200:
            print(f"TX status: {response.status_code}")
        else:
            print(f"TX response: {response.text}")
    except Exception as e:
        print(f"Failed to send to Flask: {e}")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()

    print(f"Listening on {HOST}:{PORT}...")

    try:
        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    text = data.decode(errors='ignore').strip()
                    print(f"RX: {text}")
                    send_to_flask(text)
    except KeyboardInterrupt:
        print("\nServer shutting down.")
