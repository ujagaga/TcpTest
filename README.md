# TcpTest
The project is intended for testing hardware devices that send simple TCP messages.
It consists of:

1. TCP server receives a tcp message on designated port and writes them in a database.
2. TCP monitor is a simple Flask website to display the messages in a web browser.
3. Routine to check external, public IP address and show it next to the title.

The database used is a simple Sqlite database. You may remove it at any time to clear messages or use a clear button on the web page.
The messages are stored in database with a UTC timestamp, but displayed on the Monitor web page in local time. Only the last 20 messages are stored, so older ones are deleted.

## How to start
1. pip install Flask, requests
2. Rename config.py.example to config.py and adjust parameters
3. Prepare the tcp_server to run on a computer continuously. I run it as a service on a linux computer. Installed it using the "install_tcp_server.sh"
