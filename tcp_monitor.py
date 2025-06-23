#!/usr/bin/env python3

from flask import Flask, request, g, redirect, url_for, render_template_string, jsonify
import sqlite3
import os
from datetime import datetime, UTC
from contextlib import closing

application = Flask(__name__)
DATABASE = 'messages.db'

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
  <h1>Last 20 Messages</h1>
  <ul id="message-list">
  {% for msg in messages %}
    <li><span class="timestamp">{{ msg[2] }}</span>: {{ msg[1] }}</li>
  {% endfor %}
  </ul>

  <script>
    async function fetchMessages() {
      const res = await fetch('/messages');
      const data = await res.json();
      const list = document.getElementById('message-list');
      list.innerHTML = '';
      data.forEach(msg => {
        const li = document.createElement('li');
        li.innerHTML = `<span class="timestamp">${msg.timestamp}</span>: ${msg.text}`;
        li.style.marginBottom = '8px';
        list.appendChild(li);
      });
    }
    setInterval(fetchMessages, 3000);
  </script>
</body>
</html>
"""

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


def get_last_messages(limit=20):
    db = get_db()
    with closing(db.cursor()) as cur:
        cur.execute('SELECT * FROM (SELECT * FROM messages ORDER BY id DESC LIMIT ?) ORDER BY id ASC', (limit,))
        return cur.fetchall()

@application.route('/', methods=['GET', 'POST'])
def index():
    ensure_db()
    db = get_db()
    text = request.form.get('message') or request.args.get('message')
    if text:
        timestamp = datetime.now(UTC).replace(tzinfo=None).isoformat(sep=' ', timespec='seconds')
        db.execute('INSERT INTO messages (text, timestamp) VALUES (?, ?)', (text, timestamp))
        db.execute('DELETE FROM messages WHERE id NOT IN (SELECT id FROM messages ORDER BY id DESC LIMIT 20)')
        db.commit()
        return redirect(url_for('index'))

    messages = get_last_messages()
    return render_template_string(TEMPLATE, messages=messages)

@application.route('/messages')
def get_messages():
    ensure_db()
    messages = get_last_messages()
    return jsonify([{"text": msg[1], "timestamp": msg[2]} for msg in messages])

if __name__ == '__main__':
    application.run(debug=True)
