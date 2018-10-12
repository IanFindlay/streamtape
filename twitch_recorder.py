#!/usr/bin/env python3

"""Automatically load a Twitch stream with Streamlink and record it with VLC.

Takes two sys arguments:
    Name of Twitch channel:
    Time to start recording: In local time and formatted HH:MM

e.g. twitch_recorder.py chess 18:00
"""

import time
import datetime as dt
import subprocess
import sys


def calc_start(start_time):
    """Return datetime object of the start_time calculate from current time."""
    hour = int(start_time[0: 2])
    minutes = int(start_time[3: 5])
    now = dt.datetime.now()
    dt_time = dt.datetime(now.year, now.month, now.day,
                          hour=hour, minute=minutes)

    # Need to change the day to tommorow if time has already passed
    if dt_time < now:
        day = now.day + 1
        dt_time = dt.datetime(now.year, now.month, day,
                              hour=hour, minute=minutes)

    return dt_time


if __name__ == '__main__':

    channel = sys.argv[1]
    record_time = sys.argv[2]

    print('Recording of {} will begin around {}'.format(channel, record_time))

    start_time = calc_start(record_time)

    while dt.datetime.now() < start_time:
        time.sleep(10)

    print('Starting recording of {}'.format(channel))

    day = dt.datetime.now().strftime('%y-%m-%d')
    filename = '{}-{}'.format(channel, day)
    subprocess.call(['streamlink', 'twitch.tv/{}'.format(channel),
                     'best', '-o', 'saves/{}'.format(filename),
                     '--retry-streams', '30', '--retry-max', '10',
                     '--retry-open', '5'])

    # Shutdown
    subprocess.call(['shutdown'])
