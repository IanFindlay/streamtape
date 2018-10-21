#!/usr/bin/env python3

"""Record Twitch stream through Streamlink at specified time.

Args:
    Name of Twitch channel
    Time to start recording in local, 24hr time formatted (HH:MM)

Optional Args:
    --quality (-q): Quality of stream to record
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
    """Compare argument to current time to calculate datetime it represents.

    Args:
        str_time: Local 24hr time in HH:MM format - ':' can be any separator

    Return:
        Datetime object

    """
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


def record(channel, path, quality, filename):
    """Start recording channel using Streamlink and save file to path.

    Args:
        channel: The part after 'twitch.tv/' of the desired channel
        path: Absolute file path to the save directory
        quality: Quality of recording - if none default from settings is used
        filename: Name to save recording as with no extension specified -
                  if None a timestamped default using channel name is used

    """
    wait = get_setting('Connecting', 'Wait')
    attempts = get_setting('Connecting', 'Attempts')
    rec_attempts = get_setting('Recording', 'Attempts')

    # Processed here so reconnect recordings have default timestamp option
    if not filename:
        file_time = dt.datetime.now().strftime('%m-%d(%H-%M)')
        filename = '{}-{}.ts'.format(channel, file_time)
    else:
        filename += '.ts'

    if not quality:
        quality = get_setting('Recording', 'Quality')

    subprocess.call([
        'streamlink', 'twitch.tv/{}'.format(channel),
        quality, '-o', '{}/{}'.format(path, filename),
        '--retry-streams', wait, '--retry-max', attempts,
        '--retry-open', rec_attempts
    ])


def get_setting(section, option):
    """Return value of the option in specified section of the settings file."""
    config = configparser.ConfigParser()
    config.read('settings.ini')
    value = config.get(section, option)

    return value


def main():
    """Parse command line arguments and coordinate stream recording."""
    parser = argparse.ArgumentParser(description="Twitch stream recorder")
    parser.add_argument('channel', help="Name of the Twitch channel to record")
    parser.add_argument('start_time',
                        help="Local 24hr time to start recording (HH:MM)")
    parser.add_argument('-f', '--filename', help="Name to save recording as")
    parser.add_argument('-q', '--quality',
                        help=("Set recording quality to a Streamlink "
                              "compatible value e.g. 'best', 720p"))
    parser.add_argument('-r', '--reconnect',
                        help=("Attempt to reconnect and record stream if it "
                              "disconnects before local 24hr time (HH:MM)"))
    parser.add_argument('-s', '--shutdown', action='store_true',
                        help="Shutdown computer when stream finishes")

    args = parser.parse_args()

    path = get_setting('Download', 'Path')
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)

    channel = args.channel
    start_time = args.start_time

    print("Recording of {} will begin around {}".format(channel, start_time))

    # Calculate before recording so it isn't set to next day when stream ends
    if args.reconnect:
        end_dt = strtime_datetime(args.reconnect)

    start_dt = strtime_datetime(start_time)
    while dt.datetime.now() < start_dt:
        time.sleep(10)

    print('Starting recording of {}'.format(channel))
    record(channel, path, args.quality, args.filename)

    if args.reconnect:
        while dt.datetime.now() < end_dt:
            record(channel, path, args.quality, None)

    if args.shutdown:
        subprocess.call(['shutdown'])


if __name__ == '__main__':
    main()
