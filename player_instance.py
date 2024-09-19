import os
import random
import unittest

import utilities

try:
    import mpv
    print("MPV is available.")
except ImportError:
    mpv = None  # Or set a flag to indicate mpv is not available
    print("MPV is not available.")


geometry_map = {
    'override': '1920x1080+0+0',
    'topleft': '960x540+0+0',
    'topright': '960x540+960+0',
    'botleft': '960x540+0+540',
    'botright': '960x540+960+540',
    'topll': '480x540+0+0',
    'toplr': '480x540+480+0',
    'toprl': '480x540+960+0',
    'toprr': '480x540+1440+0',
    'botll': '480x540+0+540',
    'botlr': '480x540+480+540',
    'botrl': '480x540+960+540',
    'botrr': '480x540+1440+540',
    'topmid': '960x540+480+0',
    'botmid': '960x540+480+540'
}


def play_media(media_file, volume=10, screen=0, geometry="override"):
    """
    Plays the specified media file using MPV, with optional volume, screen, and profile settings.

    Args:
        media_file (str): The path to the media file to play.
        volume (int, optional): The desired volume level (0-100). Defaults to 10.
        screen (int, optional): The screen number to display the video on. Defaults to 0.
        profile (str, optional): The MPV profile to use. 
                                 Valid options are: 'override', 'topleft', 'topright', 
                                 'botleft', 'botright', 'topll', 'toplr', 'toprl', 'toprr',
                                 'botll', 'botlr', 'botrl', 'botrr', 'topmid', 'botmid'.
                                 Defaults to 'override'.
    """

    player = mpv.MPV(input_default_bindings=True, input_vo_keyboard=True, osc=True)

    # Set volume
    player.volume = volume

    # Set screen
    player["screen"] = screen

    if geometry not in geometry_map:
        raise ValueError(f"Invalid geometry: {geometry}. Valid options are: {', '.join(geometry_map.keys())}")
    player["geometry"] = geometry_map[geometry]
    # Play the media file
    print(f"Playing {media_file}...")
    print(f'"{media_file}"')
    #player.play(f'"{media_file}"') 
    player.play(media_file)
    # Keep the script running until playback is finished
    print("Launched Player - awaiting playback completion.")
    player.wait_for_playback()

