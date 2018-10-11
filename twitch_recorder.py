#!/usr/bin/env python3

"""Automatically load a Twitch stream with Streamlink and record it with VLC.

Takes two sys arguments:
    Name of Twitch channel:
    Time to start recording: In local time and formatted HH:MM

e.g. twitch_recorder.py chess 18:00
"""

import time
import datetime as dt
import sys
import pyautogui
import psutil


def calc_start(start_time):
    """Return a datetime object representing the start_time compared to now."""
    hour = int(start_time[0: 2])
    minutes = int(start_time[3: 5])
    now = dt.datetime.now()
    # Need to change the day to tommorow if the hour is less than current one
    if now.hour > hour:
        day = now.day + 1
    else:
        day = now.day

    dt_time = dt.datetime(now.year, now.month, day, hour=hour, minute=minutes)

    return dt_time


def start_stream(channel_name):
    """Opens the channel_name Twitch stream in VLC through the Terminal."""
    # Open Terminal
    pyautogui.hotkey('ctrl', 'alt', 't')
    time.sleep(3)
    # Enter required Streamlink information
    pyautogui.typewrite('streamlink twitch.tv/{} best'.format(channel_name))
    pyautogui.press('enter')
    time.sleep(30)


def check_and_rec():
    """Check if VLC has sucessfully launched then begin recording."""
    for pid in psutil.pids():
        p = psutil.Process(pid)
        if p.name() == "vlc":
            # Record with VLC using Hotkey
            pyautogui.hotkey('shift', 'r')
            return True


if __name__ == '__main__':

    channel = sys.argv[1]
    record_time = sys.argv[2]

    print('Recording of {} will begin around {}'.format(channel, record_time))

    start_time = calc_start(record_time)

    while dt.datetime.now() < start_time:
        time.sleep(10)

    print('Attempting to start and record the stream...')

    start_stream(channel)

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
            print("The stream hasn't started - Trying again in 30s.")
            time.sleep(30)
            attempts += 1
            start_stream(channel)
