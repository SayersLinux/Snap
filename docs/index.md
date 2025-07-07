# SNAP Tool Documentation

<p align="center">
  <img src="../logo.svg" alt="SNAP Logo" width="200">
</p>

## Overview

SNAP (Social Network Analysis and Profiling Tool) is a powerful OSINT tool designed for gathering information about social media profiles. This documentation provides details about each module and how to use them effectively.

## Available Modules

- [Instagram Module](instagram_module.md) - Gather information from Instagram profiles
- [Facebook Module](facebook_module.md) - Extract data from Facebook profiles
- [Twitter Module](twitter_module.md) - Collect information from Twitter accounts
- [Snapchat Module](snapchat_module.md) - Retrieve profile details, follower counts, and posts from Snapchat
- [Email Finder](email_finder.md) - Discover email addresses associated with usernames
- [Phone Finder](phone_finder.md) - Find phone numbers linked to social media accounts

## Additional Documentation

- [Logo Usage Guide](logo_usage.md) - Information about the SNAP logo and how to use it

## General Usage

```bash
# Basic usage
./snap.py -u <username>

# Enable stealth mode
./snap.py -u <username> -s

# Save results to a file
./snap.py -u <username> -o results.json

# Enable verbose output
./snap.py -u <username> -v

# Specify platforms to analyze
./snap.py -u <username> -p instagram,twitter,snapchat
```

## Command Line Arguments

- `-u, --username`: Target username (required)
- `-o, --output`: Output file to save results
- `-v, --verbose`: Enable verbose output
- `-s, --stealth`: Enable stealth mode (slower but more secure)
- `-p, --platforms`: Specific platforms to analyze (comma separated)

## Stealth Mode

When stealth mode is enabled, SNAP will:

- Use random delays between requests
- Route traffic through proxies (requires Tor to be installed)
- Use random user agents
- Limit the number of requests

This helps avoid detection and blocking by social media platforms.

## Installation

```bash
# Clone the repository
git clone https://github.com/SayersLinux/snap.git

# Navigate to the directory
cd snap

# Install required packages
pip install -r requirements.txt

# Make the script executable
chmod +x snap.py
```

## Testing

To run the test suite:

```bash
# Run all tests
python tests/run_tests.py

# Run a specific test
python tests/test_snapchat.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.