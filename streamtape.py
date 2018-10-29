#!/usr/bin/env python3

"""Record Twitch stream through Streamlink at specified time.

Args:
    Name of Twitch channel
    Time to start recording in local, 24hr time formatted (HH:MM)

    Note: These args aren't needed if --list, --load, or --delete are called

Optional Args:
    --quality (-q): Quality of stream to record
    --filename (-f): Name to save recorded file as
    --reconnect (-r): Try to record stream again if it ends before this time
    --shutdown (-s): Shutdown computer when recording is finished
    --bookmark (-b): Save current arguments to Quickstreams under given name
    --list (-ls): List all Quickstreams
    --load (-l): Load specified Quickstream bookmark
    --delete (-d): Delete specified Quickstream bookmark
    --help, (-h): Show help information

"""

import argparse
import configparser
import datetime as dt
import json
from json import JSONDecodeError
import os
import subprocess
import sys
import time


def parse_arguments():
    """Parse command line arguments and return a dictionary of their values."""
    parser = argparse.ArgumentParser(description="Twitch stream recorder")
    parser.add_argument('channel', nargs='?',
                        help="Name of the Twitch channel to record")

    parser.add_argument('start_time', nargs='?',
                        help="Local 24hr time to start recording (HH:MM)")

    parser.add_argument('-f', '--filename', metavar='filename',
                        help="Name to save recording as")

    parser.add_argument('-q', '--quality', metavar='quality',
                        help=("Set recording quality to a Streamlink "
                              "compatible value e.g. 'best', '720p'"))

    parser.add_argument('-r', '--reconnect', metavar='HH:MM',
                        help=("Attempt to reconnect and record stream if it "
                              "disconnects before local 24hr time"))

    parser.add_argument('-s', '--shutdown', action='store_true',
                        help="Shutdown computer when stream finishes")

    parser.add_argument('-b', '--bookmark', metavar='name',
                        help="Bookmark recording settings under given name")

    parser.add_argument('-ls', '--list', action='store_true',
                        help="List all Quickstream bookmarks")

    parser.add_argument('-l', '--load', metavar='bookmark name',
                        help="Load specified Quickstream bookmark")

    parser.add_argument('-d', '--delete', metavar='bookmark name',
                        help="Delete specified Quickstream bookmark")

    args = parser.parse_args()
    return vars(args)


def list_quickstreams():
    """Print quickstreams to terminal."""
    quickstreams = read_quickstreams()
    print()
    if quickstreams == {}:
        print("No Quickstream bookmarks found.")
    else:
        print(json.dumps(quickstreams, indent=4))


def delete_quickstream(name):
    """Delete Quickstream with argument name from quickstreams.txt."""
    quickstreams = read_quickstreams()
    if name in quickstreams:
        del quickstreams[name]
        save_quickstreams(quickstreams)
        print("Quickstream {} successfully deleted.".format(name))
    else:
        print("No Quickstream under that name (-ls to list them, -h for help)")


def load_quickstream(name):
    """Load and return a quickstream dict from nested quickstreams dict."""
    quickstreams = read_quickstreams()
    if name in quickstreams:
        return quickstreams[name]

    else:
        print("No Quickstream under that name (-ls to list, -h for help).")
        sys.exit()


def read_quickstreams():
    """Read quickstreams nested dictionary from file and return it."""
    try:
        with open('quickstreams.txt', 'r') as f:
            quickstreams = json.load(f)
    except FileNotFoundError:
        quickstreams = {}
    except JSONDecodeError:
        quickstreams = {}

    return quickstreams


def save_quickstreams(quickstreams):
    """Save quickstreams to file."""
    with open('quickstreams.txt', 'w') as f:
        json.dump(quickstreams, f, indent=4)


def create_bookmark(record_settings):
    """Write record_settings to quickstreams.txt under bookmark name."""
    bookmark_name = record_settings['bookmark']
    # Set bookmark to None to avoid future loading attempting to bookmark
    record_settings['bookmark'] = None
    quickstreams = read_quickstreams()
    while bookmark_name in quickstreams or bookmark_name == '':
        bookmark_name = input("Name in use or blank, enter another: ")

    quickstreams[bookmark_name.lower()] = record_settings
    save_quickstreams(quickstreams)


def time_to_datetime(time):
    """Return time's equivalent datetime object compared to current time."""
    split_time = time.split(':')
    hour = int(split_time[0])
    minutes = int(split_time[1])
    now = dt.datetime.now()
    time_as_datetime = dt.datetime(now.year, now.month, now.day,
                                   hour=hour, minute=minutes)

    # Need to change the day to tommorow if time has already passed
    if time_as_datetime < now:
        day = now.day + 1
        time_as_datetime = dt.datetime(now.year, now.month, day,
                                       hour=hour, minute=minutes)

    return time_as_datetime


def record_stream(channel, quality, filename):
    """Start recording channel using Streamlink and save file to path.

    Args:
        channel: The part after 'twitch.tv/' of the desired channel
        quality: Quality of recording - if none default from settings is used
        filename: Name to save recording as with no extension specified -
                  if None a timestamped default using channel name is used

    """
    # Processed here so reconnected recordings have default timestamp option
    if not filename:
        file_time = dt.datetime.now().strftime('%m-%d(%H-%M)')
        filename = '{}-{}'.format(channel, file_time)
    filename += '.ts'

    if not quality:
        quality = get_setting('Recording', 'Quality')

    path = get_setting('Download', 'Path')
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)

    wait = get_setting('Connecting', 'Wait')
    attempts = get_setting('Connecting', 'Attempts')
    rec_attempts = get_setting('Recording', 'Attempts')

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
    """Coordinate recording of stream."""
    args = parse_arguments()

    if args['list']:
        list_quickstreams()
        sys.exit()

    elif args['delete']:
        delete_quickstream(args['delete'])
        sys.exit()

    elif args['load']:
        args = load_quickstream(args['load'])

    channel = args['channel']
    start_time = args['start_time']

    if None in (channel, start_time):
        print("Channel and Start_time arguments are required if "
              "--delete, --list, or --load aren't being called.")
        sys.exit()

    if args['bookmark']:
        create_bookmark(args)

    print("Recording of {} will begin around {}".format(channel, start_time))

    # Calculate before recording so it isn't set to next day when stream ends
    if args['reconnect']:
        end_dt = time_to_datetime(args['reconnect'])

    start_dt = time_to_datetime(start_time)
    while dt.datetime.now() < start_dt:
        time.sleep(10)

    print('Starting recording of {}'.format(channel))
    record_stream(channel, args['quality'], args['filename'])

    if args['reconnect']:
        while dt.datetime.now() < end_dt:
            record_stream(channel, args['quality'], None)

    if args['shutdown']:
        subprocess.call(['shutdown'])


if __name__ == '__main__':
    main()
