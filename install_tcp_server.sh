#!/usr/bin/env bash

# Define variables
VENV_DIR="venv"
PYTHON_BIN="python3"
SERVICE_NAME=tcp_server.service
SERVICE_FILE=/etc/systemd/system/$SERVICE_NAME


# Check if Python is installed
if ! command -v $PYTHON_BIN &> /dev/null; then
    echo "Error: $PYTHON_BIN is not installed. Please install Python 3."
    exit 1
fi

# Create the virtual environment
if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists in '$VENV_DIR'."
else
    echo "Creating virtual environment in '$VENV_DIR'..."
    $PYTHON_BIN -m venv $VENV_DIR
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment."
        exit 1
    fi
    echo "Virtual environment created successfully."
fi

# Activate the virtual environment
source $VENV_DIR/bin/activate

# Upgrade pip to the latest version
echo "Upgrading pip..."
pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo "Error: Failed to upgrade pip."
    deactivate
    exit 1
fi

# Install Flask
echo "Installing Flask..."
pip install flask requests
if [ $? -ne 0 ]; then
    echo "Error: Failed to install Flask."
    deactivate
    exit 1
fi

echo "Flask installed successfully."

# Deactivate the virtual environment
deactivate

echo "Making tcp_server.py executable..."
chmod +x tcp_server.py
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
ExecStart=$PWD/server_runner.sh
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