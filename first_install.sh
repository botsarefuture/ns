# Clone the repository
git clone https://github.com/botsarefuture/ns.git

# Navigate to the project directory
cd ns/client

# Check if Python is installed
if command -v python3 &> /dev/null; then
    echo "Python 3 is already installed."
else
    # Install Python 3
    echo "Installing Python 3..."
    # Add commands for installing Python based on your system (e.g., apt-get, yum, brew, etc.)
    # For example, on Debian/Ubuntu:
    sudo apt-get update -y
    sudo apt-get install python3 python-is-python3 python3-pip -y
fi

# Install the required Python packages
python3 -m pip install -r mhddos/MHDDoS/requirements.txt

# Run the client script
python3 client.py
