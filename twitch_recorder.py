#!/usr/bin/env python3

"""Automatically load a Twitch stream with Streamlink and record it with VLC.

Takes two sys arguments:
    Name of Twitch channel:
    Time to start recording: In local time and formatted HH:MM

e.g. twitch_recorder.py chess 18:00
"""

import configparser
import datetime as dt
import os
import subprocess
import sys
import time


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


def get_setting(section, option):
    """Retrieve and return a value from settings."""
    config = configparser.ConfigParser()
    config.read('settings.ini')
    value = config.get(section, option)

    return value


if __name__ == '__main__':

    # Get settings
    path = get_setting('Download', 'Path')
    shutdown = get_setting('Download', 'Shutdown')
    delay = get_setting('Retry', 'Delay')
    attempts = get_setting('Retry', 'Attempts')
    record = get_setting('Retry', 'Record')

    # Create path if it doesn't exist
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)

    channel = sys.argv[1]
    record_time = sys.argv[2]

    print('Recording of {} will begin around {}'.format(channel, record_time))

    start_time = calc_start(record_time)

    while dt.datetime.now() < start_time:
        time.sleep(10)

    print('Starting recording of {}'.format(channel))

    day = dt.datetime.now().strftime('%y.%m.%d')
    filename = '{}-{}-{}'.format(channel, day, record_time)
    subprocess.call(['streamlink', 'twitch.tv/{}'.format(channel),
                     'best', '-o', '{}/{}'.format(path, filename),
                     '--retry-streams', delay, '--retry-max', attempts,
                     '--retry-open', record])

    if shutdown.lower() in ('y', 'yes'):
        subprocess.call(['shutdown'])
