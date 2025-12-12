FROM python:3.12-slim

# Create app directory
WORKDIR /app

# Install system dependencies (optional but good for safety)
#RUN apt-get update && apt-get install -y --no-install-recommends \
#        build-essential \
#    && rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN pip install flask requests

COPY tcp_server.py .

# Expose ports used by your app
EXPOSE 4060 4061

# The app defaults to config.TCP_SERVER_PORT unless overridden
ENTRYPOINT ["python3", "tcp_server.py"]
