# TcpTest
The project is intended for testing hardware devices that send simple TCP messages.
It consists of:

1. tcp_server.py - script to receive a tcp message on designated port. This script needs to run continuously on a computer with a public IP address
2. tcp_monitor.py - a simple Flask website to receive the messages from the tcp_server and display the last 20 of them in a web browser
3. test_send.py - a test script to be used to confirm that messages received by the tcp_server are displayed on the tcp_monitor

The database used is a simple Sqlite database. You may remove it at any time to clear messages or use a clear button on the web page.

## How to start
1. pip install Flask, requests
2. Prepare the tcp_server to run on a computer continuously. I run it as a service on a linux computer.
3. Deploy the tcp_monitor on some hosting service so it is accessible by anyone.