#!/usr/bin/env python3

"""Automatically loads a Twitch stream using Streamlink and records it with VLC.
Takes two sys arguments: Name of channel, Time to start recording (HH:MM)
e.g. twitch-recorder chess 18:00
"""

import time
import datetime
import sys
import pyautogui
import psutil


def time_reached():
    """Check if a time has been reached/passed."""
    date = datetime.datetime.now()
    hour = int(date.strftime('%-H'))
    minutes = int(date.strftime('%-M'))
    if hour == start_hour and minutes >= start_minutes:
        return True


def start_stream(channel_name):
    """Opens the channel_name Twitch stream in VLC through the Terminal."""
    # Open Terminal
    pyautogui.hotkey('ctrl', 'alt', 't')
    time.sleep(3)
    # Enter required Streamlink information
    pyautogui.typewrite('streamlink twitch.tv/{} best'.format(channel_name))
    pyautogui.press('enter')


def check_and_rec():
    """Checks if VLC has sucessfully launched the stream then begins recording."""
    for pid in psutil.pids():
        p = psutil.Process(pid)
        if p.name() == "vlc":
            # Record with VLC using Hotkey
            pyautogui.hotkey('shift', 'r')
            return True


channel = sys.argv[1]
record_time = sys.argv[2]
time_list = record_time.split(':')
start_hour = int(time_list[0])
start_minutes = int(time_list[1])

print('Waiting for the scheduled time (' + str(start_hour).zfill(2) + ':'
      + str(start_minutes).zfill(2) +'). Recording of ' + channel +
      ' will begin then...')

while True:
    if time_reached():
        break
    else:
        time.sleep(60)

print('Attempting to start and record the stream...')

start_stream(channel)
time.sleep(30)

attempts = 1
while True:
    if check_and_rec():
        print("Recording...")
        break
    elif attempts == 20:
        print("The Stream has failed to start {} times "
              "- Program shutting Down.".format(str(attempts)))
        break
    else:
        print("The stream hasn't started sucessfully - Trying again in 30s.")
        time.sleep(30)
        attempts += 1
        start_stream(channel)
