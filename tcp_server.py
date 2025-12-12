#!/usr/bin/env python3

from flask import Flask, g, render_template_string, jsonify, redirect, url_for
import sqlite3
import os
from datetime import datetime, UTC
from contextlib import closing
import threading
import socket
import config
import subprocess
import argparse


application = Flask(__name__)
DATABASE = 'messages.db'

HOST = '0.0.0.0'
TCP_SERVER_PORT = 4060


# --- HTML Template ---
TEMPLATE = """
<!doctype html>
<html>
<head>
  <title>Messages</title>
  <style>
    body {
      background-color: black;
      color: #c0c0c0;
      font-family: monospace;
      padding: 20px;
    }
    h1 {
      color: #00ff00;
    }
    ul {
      list-style-type: none;
      padding-left: 0;
    }
    li {
      margin-bottom: 8px;
    }
    .timestamp {
      color: #00ff00;
    }
  </style>
</head>
<body>
  <h1 style="display: flex; align-items: center; gap: 1rem;">
  Last 20 Messages ({{ external_ip }})
  <form method="post" action="/clear" style="margin:0;">
    <button type="submit" style="
      background: #222;
      color: #00ff00;
      border: 1px solid #00ff00;
      font-family: monospace;
      cursor: pointer;
      padding: 4px 8px;
      font-size: 0.8rem;
    ">Clear</button>
  </form>
</h1>
  <ul id="message-list">
  {% for msg in messages %}
    <li><span class="timestamp">{{ msg[2] }}</span>: {{ msg[1] }}</li>
  {% endfor %}
  </ul>

  <script>
    function pad(n) {
    return n.toString().padStart(2, '0');
  }

  function utcToLocal(utcStr) {
    const date = new Date(utcStr + 'Z');
    const year = date.getFullYear();
    const month = pad(date.getMonth() + 1); // 0-based
    const day = pad(date.getDate());
    const hour = pad(date.getHours());
    const min = pad(date.getMinutes());
    const sec = pad(date.getSeconds());
    return `${year}-${month}-${day} ${hour}:${min}:${sec}`;
  } 

    async function fetchMessages() {
      const res = await fetch('/messages');
      const data = await res.json();
      const list = document.getElementById('message-list');
      list.innerHTML = '';
      data.forEach(msg => {
        const li = document.createElement('li');
        li.innerHTML = `<span class="timestamp">${utcToLocal(msg.timestamp)}</span>: ${msg.text}`;
        li.style.marginBottom = '8px';
        list.appendChild(li);
      });
    }

    setInterval(fetchMessages, 3000);
  </script>
</body>
</html>
"""

# --- SQLite Helpers ---
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
    return g.db

@application.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None)
    if db:
        db.close()

def ensure_db():
    if not os.path.exists(DATABASE):
        db = sqlite3.connect(DATABASE)
        db.execute('CREATE TABLE messages (id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT, timestamp TEXT)')
        db.commit()
        db.close()

def insert_message(text):
    ensure_db()
    timestamp = datetime.now(UTC).replace(tzinfo=None).isoformat(sep=' ', timespec='seconds')
    with sqlite3.connect(DATABASE) as db:
        db.execute('INSERT INTO messages (text, timestamp) VALUES (?, ?)', (text, timestamp))
        db.execute('DELETE FROM messages WHERE id NOT IN (SELECT id FROM messages ORDER BY id DESC LIMIT 20)')
        db.commit()

def get_last_messages(limit=20):
    db = get_db()
    with closing(db.cursor()) as cur:
        cur.execute('SELECT * FROM (SELECT * FROM messages ORDER BY id DESC LIMIT ?) ORDER BY id ASC', (limit,))
        return cur.fetchall()

# --- External IP check ---
def get_external_ip():
    try:
        ip = subprocess.check_output(['curl', '-s', 'ifconfig.me'], timeout=2).decode().strip()
        return ip
    except Exception as e:
        return 'Unavailable'

# --- Timestamp helper
def format_timestamp(ts_str):
    dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
    local = dt.astimezone()
    return local.strftime("%Y-%m-%d %H:%M:%S")  # leading zeros by default

# --- Flask Routes ---
@application.route('/')
def index():
    ensure_db()
    raw_messages = get_last_messages()
    formatted = [(msg[0], msg[1], format_timestamp(msg[2])) for msg in raw_messages]
    external_ip = get_external_ip()
    return render_template_string(TEMPLATE, messages=formatted, external_ip=external_ip)

@application.route('/messages')
def get_messages():
    ensure_db()
    messages = get_last_messages()
    return jsonify([{"text": msg[1], "timestamp": msg[2]} for msg in messages])

@application.route('/clear', methods=['POST'])
def clear_messages():
    ensure_db()
    db = get_db()
    db.execute('DELETE FROM messages')
    db.commit()
    return redirect(url_for('index'))

# --- TCP Listener in Background ---
def tcp_listener():
    ensure_db()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, TCP_SERVER_PORT))
        s.listen()
        print(f"[TCP SERVER] Listening on {HOST}:{TCP_SERVER_PORT}...")

        while True:
            try:
                conn, addr = s.accept()
                print(f"[TCP] Connected by {addr}")
                conn.settimeout(300)  # 5 minutes of inactivity

                try:
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            print(f"[TCP] Connection closed by client {addr}")
                            break
                        hex_data = ' '.join(f'{b:02X}' for b in data)
                        print(f"[TCP] RX: {hex_data}")
                        insert_message(f"HEX: {hex_data}")
                except socket.timeout:
                    print(f"[TCP] Connection with {addr} timed out due to inactivity.")
                finally:
                    conn.close()
                    print(f"[TCP] Closed connection with {addr}")

            except Exception as e:
                print(f"[TCP SERVER] Listener error: {e}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="TCP Monitor Server")
    parser.add_argument('tcp_port', nargs='?', type=int, help='Optional TCP server port override')
    args = parser.parse_args()

    if args.tcp_port:
        TCP_SERVER_PORT = args.tcp_port
    MONITOR_PORT = TCP_SERVER_PORT + 1
    
    print(f"[CONFIG] TCP_SERVER_PORT: {TCP_SERVER_PORT}, MONITOR_PORT: {MONITOR_PORT}")

    threading.Thread(target=tcp_listener, daemon=True).start()
    print(f"[TCP_MONITOR] Serving web preview on port {MONITOR_PORT}")
    application.run(debug=False, port=MONITOR_PORT, host=HOST)
