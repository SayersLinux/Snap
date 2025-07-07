# Snapchat Module Documentation

## Overview

The Snapchat module for SNAP tool allows you to gather information about Snapchat profiles, including profile details, follower counts, recent posts, and last active status.

## Features

- Retrieve basic profile information (username, display name, bitmoji)
- Get subscriber count and story count
- Find last active timestamp
- Retrieve recent stories and their details
- Support for stealth mode operation

## Usage

### Command Line

```bash
# Include Snapchat in your analysis
./snap.py -u <username> -p snapchat

# Run with all platforms including Snapchat
./snap.py -u <username>

# Use stealth mode for more secure operation
./snap.py -u <username> -p snapchat -s
```

### Example Output

```
[+] SNAPCHAT Results:
  username: johndoe
  display_name: John Doe
  subscriber_count: 1823
  story_count: 5
  last_active: 2023-06-15 14:32:45
  recent_stories:
    - timestamp: 2023-06-15 12:30:22
      type: image
      view_count: 342
```

## Technical Details

The Snapchat module works by:

1. Accessing the public Snapchat profile page
2. Extracting information from HTML and JavaScript data
3. Parsing profile details, subscriber counts, and story information
4. Formatting the data into a structured format

## Limitations

- Only works with public Snapchat profiles
- Some information may not be available for all profiles
- Snapchat's frequent UI changes may affect the module's functionality
- Last active status may not be available for all users due to privacy settings

## Troubleshooting

If you encounter issues with the Snapchat module:

1. Ensure the target username exists and is spelled correctly
2. Check that the profile is public
3. Try using stealth mode (`-s` flag) to avoid rate limiting
4. Update to the latest version of SNAP tool

## Privacy and Ethical Considerations

Remember that this tool should only be used for legitimate security research and with proper authorization. Respect privacy settings and terms of service of Snapchat.