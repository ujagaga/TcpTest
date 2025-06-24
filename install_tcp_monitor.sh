#!/usr/bin/env bash

SERVICE_NAME=tcp_monitor.service
SERVICE_FILE=/etc/systemd/system/$SERVICE_NAME

# --- Installation Section ---
echo "Installing dependencies..."
if ! sudo apt update -y; then
  echo "Error: Failed to update apt repositories. Aborting installation."
  exit 1
fi

if ! sudo apt install -y python3-flask; then
  echo "Error: Failed to install dependencies. Aborting installation."
  exit 1
fi

echo "Making tcp_server.py executable..."
chmod +x tcp_monitor.py
if [ $? -ne 0 ]; then
  echo "Error: Failed to make index.py executable. Aborting installation."
  exit 1
fi

# --- Service File Creation ---
echo "Creating systemd service file: $SERVICE_FILE"
cat <<EOF > "$PWD/$SERVICE_NAME"
[Unit]
Description=Tcp Test Server
After=network-online.target
Wants=network-online.target
StartLimitIntervalSec=0

[Service]
Type=simple
User=$USER
ExecStart=$PWD/tcp_monitor.py
WorkingDirectory=$PWD
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF
if [ $? -ne 0 ]; then
  echo "Error: Failed to create the service file. Aborting installation."
  exit 1
fi
sudo mv "$PWD/$SERVICE_NAME" "$SERVICE_FILE"
if [ $? -ne 0 ]; then
  echo "Error: Failed to move the service file to $SERVICE_FILE. Aborting installation."
  exit 1
fi

# --- Service Management ---
echo "Enabling and starting the service..."
sudo systemctl enable "$SERVICE_NAME"
if [ $? -ne 0 ]; then
  echo "Error: Failed to enable the service. Installation incomplete."
  exit 1
fi
sudo systemctl start "$SERVICE_NAME"
if [ $? -ne 0 ]; then
  echo "Error: Failed to start the service. Installation incomplete."
  exit 1
fi

echo "Tcp Test Server installation and service started successfully!"

exit 0