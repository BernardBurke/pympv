#!/usr/bin/env python3
import mpv

# Enable the on-screen controller and keyboard shortcuts
player = mpv.MPV(input_default_bindings=True, input_vo_keyboard=True, osc=True)
player.play('/home/ben/vision.x265.mkv')
player.wait_for_playback()