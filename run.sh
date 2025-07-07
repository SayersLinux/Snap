#!/bin/bash

# SNAP - Social Network Analysis and Profiling Tool
# Run script for Linux systems
# Developer: SayersLinux
# Email: SayerLinux@gmail.com

# Display banner
echo -e "\e[31m███████╗███╗   ██╗ █████╗ ██████╗ \e[0m"
echo -e "\e[31m██╔════╝████╗  ██║██╔══██╗██╔══██╗\e[0m"
echo -e "\e[31m███████╗██╔██╗ ██║███████║██████╔╝\e[0m"
echo -e "\e[31m╚════██║██║╚██╗██║██╔══██║██╔═══╝ \e[0m"
echo -e "\e[31m███████║██║ ╚████║██║  ██║██║     \e[0m"
echo -e "\e[31m╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝     \e[0m"
echo -e "\e[36mSocial Network Analysis and Profiling Tool\e[0m"
echo -e "\e[37mDeveloped by: \e[32mSayersLinux\e[0m"
echo -e "\e[37mEmail: \e[32mSayerLinux@gmail.com\e[0m"
echo -e "\e[33mVersion: 1.0.0\e[0m"
echo -e "\e[31mWARNING: Use responsibly and ethically. For educational purposes only.\e[0m"
echo ""

# Check if running on Linux
if [[ "$(uname)" != "Linux" ]]; then
    echo -e "\e[31m[!] Error: This tool only works on Linux systems.\e[0m"
    exit 1
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "\e[31m[!] Error: Python 3 is not installed.\e[0m"
    echo -e "\e[33m[*] Please install Python 3 using your package manager.\e[0m"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo -e "\e[31m[!] Error: pip3 is not installed.\e[0m"
    echo -e "\e[33m[*] Please install pip3 using your package manager.\e[0m"
    exit 1
fi

# Check if requirements are installed
echo -e "\e[36m[*] Checking dependencies...\e[0m"
if ! pip3 freeze | grep -q "requests"; then
    echo -e "\e[33m[*] Installing required packages...\e[0m"
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "\e[31m[!] Error: Failed to install required packages.\e[0m"
        exit 1
    fi
fi

# Check if Tor is installed (for stealth mode)
if ! command -v tor &> /dev/null; then
    echo -e "\e[33m[!] Warning: Tor is not installed. Stealth mode may not work properly.\e[0m"
    echo -e "\e[33m[*] Consider installing Tor for better anonymity: sudo apt install tor\e[0m"
fi

# Make sure snap.py is executable
chmod +x snap.py

# Run the tool with provided arguments
echo -e "\e[36m[*] Starting SNAP...\e[0m"
python3 snap.py "$@"