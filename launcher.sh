#!/bin/bash

# Ask for root password once at the beginning
echo "TailGUI needs root privileges for Tailscale operations."
sudo -v

# Keep-alive: update existing sudo timestamp until script finishes
while true; do
    sudo -n true
    sleep 60
    kill -0 "$$" || exit
done 2>/dev/null &

# Run the application
cd "$(dirname "$0")"
source pythonvenv/bin/activate
python3 main.py