#!/usr/bin/env python3

"""Record Twitch stream through Streamlink at specified time.

Args:
    Name of Twitch channel
    Time to start recording(HH:MM)

Optional Args:
    --filename (-f): Name to save recorded file as
    --reconnect (-r): Try to record stream again if it ends before this time
    --shutdown (-s): Shutdown computer when recording is finished

"""

import argparse
import configparser
import datetime as dt
import os
import subprocess
import time


def strtime_datetime(str_time):
    """Return datetime object of given time calculated from current time."""
    hour = int(str_time[0: 2])
    minutes = int(str_time[3: 5])
    now = dt.datetime.now()
    dt_time = dt.datetime(now.year, now.month, now.day,
                          hour=hour, minute=minutes)

    # Need to change the day to tommorow if time has already passed
    if dt_time < now:
        day = now.day + 1
        dt_time = dt.datetime(now.year, now.month, day,
                              hour=hour, minute=minutes)

    return dt_time


def start_recording(channel, path, filename=None):
    """Start recording channel using Streamlink and save file to path."""
    wait = get_setting('Connecting', 'Wait')
    attempts = get_setting('Connecting', 'Attempts')
    rec_attempts = get_setting('Recording', 'Attempts')
    quality = get_setting('Recording', 'Quality')

    print('Starting recording of {}'.format(channel))

    if not filename:
        file_time = dt.datetime.now().strftime('%m-%d(%H-%M)')
        filename = '{}-{}.ts'.format(channel, file_time)
    else:
        filename += '.ts'
    subprocess.call([
        'streamlink', 'twitch.tv/{}'.format(channel),
        quality, '-o', '{}/{}'.format(path, filename),
        '--retry-streams', wait, '--retry-max', attempts,
        '--retry-open', rec_attempts
    ])


def get_setting(section, option):
    """Retrieve and return a value from settings file."""
    config = configparser.ConfigParser()
    config.read('settings.ini')
    value = config.get(section, option)

    return value


def main():
    """Parse command line arguments and coordinate stream recording."""
    # Process sys arguments
    parser = argparse.ArgumentParser(description="Twitch stream recorder")
    parser.add_argument('channel', help="Name of the Twitch channel to record")
    parser.add_argument('start_time', help="Time to start recording (HH:MM)")
    parser.add_argument('-f', '--filename', help="Name to save recording as")
    parser.add_argument('-r', '--reconnect',
                        help=("Attempt to reconnect and record stream if it "
                              "disconnects before this time (HH:MM)"))
    parser.add_argument('-s', '--shutdown', action='store_true',
                        help="Shutdown computer when stream finishes")

    args = parser.parse_args()

    # Create save path directory if it doesn't exist
    path = get_setting('Download', 'Path')
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)

    channel = args.channel
    start_time = args.start_time

    print("Recording of {} will begin around {}".format(channel, start_time))

    start_dt = strtime_datetime(start_time)

    while dt.datetime.now() < start_dt:
        time.sleep(10)

    if args.filename:
        start_recording(channel, path, filename=args.filename)
    else:
        start_recording(channel, path)

    # If reconnect argument given, keep trying to record stream until end_time
    if args.reconnect:
        end_dt = strtime_datetime(args.reconnect)
        while dt.datetime.now() < end_dt:
            start_recording(channel, path)

    if args.shutdown:
        subprocess.call(['shutdown'])


if __name__ == '__main__':
    main()
