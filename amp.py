#!/usr/bin/env python3
"""
AMP - AI Music Player
Your intelligent Spotify assistant. Just type what you want!

Usage:
    python amp.py                    # Start interactive mode
    python amp.py "play chill music" # Quick command
    python amp.py --help             # Show help
"""

from amp.cli import main

if __name__ == "__main__":
    main()
