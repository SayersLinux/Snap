# SNAP Logo Usage Guide

## Overview

This document provides information about the SNAP tool logo and how to use it in different contexts.

## Logo File

The SNAP logo is provided as an SVG (Scalable Vector Graphics) file, which offers several advantages:

- **Scalability**: The logo can be resized without losing quality
- **Small file size**: SVG files are typically smaller than raster images
- **Editability**: The logo can be easily modified using vector graphics editors
- **Transparency**: The logo supports transparent backgrounds

## Viewing the Logo

### On Linux

```bash
# Using a web browser
firefox logo.svg
# or
chrome logo.svg

# Using image viewers
eog logo.svg
# or
display logo.svg

# Using terminal-based viewers (if installed)
svgconsole logo.svg
# or
imgcat logo.svg
```

### On Windows

- Double-click the SVG file to open it in your default browser
- Right-click and select "Open with" to choose a specific program
- Use File Explorer to navigate to the file location

### On macOS

```bash
# Using a web browser
open -a Safari logo.svg
# or
open -a "Google Chrome" logo.svg

# Using Preview
open logo.svg

# Using terminal-based viewers (if installed)
imgcat logo.svg  # For iTerm2
```

## Using the Logo in Documentation

### In Markdown Files

```markdown
<p align="center">
  <img src="logo.svg" alt="SNAP Logo" width="200">
</p>
```

### In HTML Files

```html
<div style="text-align: center;">
  <img src="logo.svg" alt="SNAP Logo" width="200">
</div>
```

### In LaTeX Documents

```latex
\begin{figure}[h]
  \centering
  \includegraphics[width=0.5\textwidth]{logo.svg}
  \caption{SNAP Logo}
\end{figure}
```

## Modifying the Logo

The SVG logo can be modified using vector graphics editors such as:

- **Inkscape** (Free, open-source): Available for Linux, Windows, and macOS
- **Adobe Illustrator**: Commercial software for professional editing
- **Affinity Designer**: Commercial alternative to Illustrator
- **Online editors**: Such as Figma, SVG-edit, or Vectr

## Logo Colors

The SNAP logo uses the following color palette:

- Background: #1a1a1a (Dark gray)
- Outer Ring: #e74c3c (Red)
- Network Nodes: Various colors (#3498db, #2ecc71, #f39c12, #9b59b6, #1abc9c, #e74c3c, #f1c40f)
- Connection Lines: #ffffff (White) with varying opacity
- Text: #ffffff (White)

## Programmatic Display

The SNAP tool includes functionality to display information about the logo:

```python
# Import the logo display module
from modules.logo_display import display_svg_logo, try_display_svg_in_terminal

# Try to display the logo directly in the terminal (if supported)
try_display_svg_in_terminal()

# Display information about the logo
display_svg_logo()
```

## Terminal Support

Some terminals support displaying images directly:

- **iTerm2** (macOS): Supports the `imgcat` command
- **Kitty** (Cross-platform): Has built-in image display capabilities
- **Modern terminals**: Many modern terminals have some level of image support

The SNAP tool will attempt to detect and use available methods to display the logo in supported terminals.