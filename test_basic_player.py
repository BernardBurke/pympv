import os
from pathlib import Path
from player_instance import play_media
import sys


def main():
    while True:
        if len(sys.argv) < 2:
            print("Usage: python test_basic_player.py <path_to_media_file>")
            break
        media_file_input = sys.argv[1]
        if media_file_input.lower() == 'q':
            break
        print(f"Playing {media_file_input}...")
        media_file = Path(media_file_input)
        if not media_file.exists():
            print("File not found. Please try again.")
        else:
            play_media(str(media_file))  # Convert Path object to string for play_media

if __name__ == "__main__":
    main()