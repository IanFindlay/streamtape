#!/usr/bin/env python3

"""Automatically loads a Twitch stream using Streamlink and records it with VLC.
Takes two sys arguments: Name of channel, Time to start recording (HH:MM)
e.g. twitch-recorder chess 18:00
"""

import time
import datetime
import sys
import pyautogui


def record_stream(channel_name):
    """Opens the channel_name Twitch stream in VLC and records it."""
    # Open Terminal and click on it.
    pyautogui.hotkey('ctrl', 'shift', 't')
    time.sleep(3)

    # Input streamlink information
    pyautogui.typewrite('streamlink twitch.tv/{} best'.format(channel_name))
    pyautogui.press('enter')
    time.sleep(10)

    # Record with VLC
    pyautogui.hotkey('shift', 'r')


channel = sys.argv[1]
record_time = sys.argv[2]
time_list = record_time.split(':')
start_hour = int(time_list[0])
start_minutes = int(time_list[1])

print('Waiting for the scheduled time (' + str(start_hour).zfill(2) + ':'
      + str(start_minutes).zfill(2) +'). Recording of ' + channel +
      ' will begin then...')

while True:
    date = datetime.datetime.now()
    hour = int(date.strftime('%-H'))
    minutes = int(date.strftime('%-M'))
    if hour == start_hour and minutes >= start_minutes:
        break
    else:
        time.sleep(60)

print('Starting and recording the stream.')

record_stream(channel)
